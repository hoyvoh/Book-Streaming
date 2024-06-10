from pymongo import MongoClient
from transformers import AutoTokenizer, AutoModel
import torch
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

'''
From processing module, we received a list of features that looks like:
FEATURES
---
title: "góc nhìn alan - bộ di sản alan phan"
author: "alan phan"
keywords: [words array]
sales: [sales posibility]
pos: [comment positivity]
---

This module needs to:
User will have a User vector that is initially 0
Recommendation
- Create vector database and indexing: For each row of Features, embed keywords to vectors
- Combine feature vectors of all product, marked by their pids, 
keep the sales possibility and comment positive rate as ranking aspects
- Put all products into BookIndexing and try to query some books with list and title
- Function to capture top 5 most recent products of user
> query features, embed, combine to user vector
> query similar products based on the updated user vector
> return the list of recommended products for 

- Function to display top products

Search top keywords
- Add a search function and log the search history to mongoDB SearchLog
- For each search log, do vietnamese preprocessing before adding
- For each search log, re-analyze the search trending keywords based on the top search

This block of functions will be run for every time user update the product history
'''

'''
Embed features and load to vector database
'''
# Load PhoRanker model and tokenizer
model_name = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)
print('model loaded')

# Vectorize keywords
def vectorize_keywords(keywords):
    inputs = tokenizer(keywords, padding=True, truncation=True, return_tensors="pt")
    with torch.no_grad():
        outputs = model(**inputs)
    embeddings = outputs.last_hidden_state.mean(dim=1)  # Mean pooling
    print('keyword vectorized')
    return embeddings

# Create feature vector
def create_feature_vector(keyword_embeddings, sales_possibility, positive_rate):
    keyword_embeddings = keyword_embeddings.mean(axis=0)
    additional_features = np.array([sales_possibility, positive_rate], dtype=np.float32)
    print(keyword_embeddings.shape)
    print(additional_features.shape)

    combined_vector = np.hstack((keyword_embeddings, additional_features))
    print('feature combined')
    return combined_vector

# Initialize MongoDB client
client = MongoClient("mongodb://localhost:27017/")
db = client['BookDatabase']
collection = db['BookFeatureIndexing']

# The input document is expected to look like this:
document = [{
    "key": "121635154",
    # <some other things here>
    'value':{
        "FEATURES": [
        "điều đẹp nhất có khi là buông tay (tặng kèm bookmark)",
        "thought catalog",
        [
            "bạn",
            "tình yêu",
            "đợi chờ",
            "dấu hiệu",
            "sẵn sàng",
            "giúp đỡ",
            "Nhà Sách Tiki",
            "Sách tiếng Việt",
            "Sách văn học",
            "Truyện ngắn - Tản văn - Tạp Văn",
            "Truyện ngắn - Tản văn - Tạp Văn Nước Ngoài",
            "Điều Đẹp Nhất Có Khi Là Buông Tay (Tặng Kèm Bookmark)"
        ],
        1,
        [66,0,0,1]
    ]
    },
}]

def load_vector_database(document, db):
    collection = db['BookFeatureIndexing']
    # collection.drop()
    
    keyword_embeddings = vectorize_keywords(document['value']['FEATURES'][2])
    try:
        feature_vector = create_feature_vector(keyword_embeddings, document['value']['FEATURES'][3], document['value']['FEATURES'][4][3])
        doc = {
            'key': document['key'],
            'embedding': feature_vector.tolist(),
            'sales_possibility' : document['value']['FEATURES'][3],
            'positive_rate': document['value']['FEATURES'][4][3]
        }
    except IndexError as e:
        feature_vector = create_feature_vector(keyword_embeddings, document['value']['FEATURES'][3], 0)
        doc = {
            'key': document['key'],
            'embedding': feature_vector.tolist(),
            'sales_possibility' : document['value']['FEATURES'][3],
            'positive_rate': 0
        }
    collection.insert_one(doc)
    print('vector database loaded 1.')
    return collection

def search_by_key(key, db):
    collection = db['BookFeatureIndexing']
    results = collection.find_one({"key": key})

    if results:
        embedding = results.get("embedding")
        if embedding:
            pid_list = semantic_search_vector(embedding, db)
            # Drop the key from the PID list if it exists
            pid_list = [pid for pid in pid_list if pid != key]
            return pid_list
        else:
            return []
    else:
        return []

def semantic_search_key(query_key, db, sales = 1, pos = 1):
    collection = db['BookFeatureIndexing']
    query_key_embeddings = vectorize_keywords(query_key)
    query_feature_vector = create_feature_vector(query_key_embeddings, sales, pos)
    docs = list(collection.find())
    similarities = []
    for doc in docs:
        stored_vector = np.array(doc["embedding"])
        similarity = cosine_similarity([query_feature_vector], [stored_vector])[0][0]
        similarities.append([similarity, doc])
    similarities.sort(key=lambda x :(x[0], x[1]['sales_possibility'], x[1]['positive_rate']), reverse=True)
    top_docs = [doc for _, doc in similarities[:10]]
    return top_docs

def semantic_search_vector(user_vector, db):
    # Context: Each time user is in a product details page, this function will be called
    # to get the list of 10 most relevant products to the user vector
    # Input: user_vector, db
    # Process: query top 10 relevant products
    # Output: list of 10 pids
    collection = db['BookFeatureIndexing']
    docs = list(collection.find())
    similarities = []
    seen_keys = set()
    for doc in docs:
        key = doc['key']
        if key in seen_keys:
            continue
        stored_vector = np.array(doc["embedding"])
        similarity = cosine_similarity([user_vector], [stored_vector])[0][0]
        similarities.append([similarity, doc])
        seen_keys.add(key)
    similarities.sort(key=lambda x :(x[0], x[1]['sales_possibility'], x[1]['positive_rate']), reverse=True)
    top_docs = [doc.get('key') for _, doc in similarities[:10]]
    return top_docs
    

'''
Init a User vector with 0 
Approach 1: Function to get 5 most recent product feature vectors from a list of pid,
combine them to a user vector
Approach 2: Function to add new feature vectors to User vector 
Function to semantic query 5 products from user vector
'''
def init_user_vector(size=386):
    # Context: User came to the shop for the first time, no idea what they want
    # Input: No inp
    # Output: initial 0 vector
    return [0]*size

def update_user_vector_a1(pid, db):
    # Context: Each time user choose to see a product, this will be recorded in a log in Mongo
    # This function will be called to update user vector
    # Input: database
    # Process: query the embedded features of top 5 recent in log, combine them, update the user vector
    # Output: new user vector
    user_log = db['UserLog']
    book_features = db['BookFeatureIndexing']

    # Find the product embedding
    product = book_features.find_one({"key": pid})
    if not product:
        raise ValueError(f"Product with key {pid} not found in BookFeatureIndexing")

    # Insert the product embedding into the user log
    user_element = {
        'key': pid,
        'embedding': product['embedding']
    }
    user_log.insert_one(user_element)

    # Retrieve the most recent 5 embeddings from the user log
    user_vector_it = user_log.find().sort([('_id', -1)]).limit(5)
    user_vector = []
    for uv in user_vector_it:
        user_vector.append(uv['embedding'])
    
    if not user_vector:
        return np.zeros_like(product['embedding'])  # Return zero vector if no logs found

    user_vector = np.array(user_vector).mean(axis=0)
    return user_vector

def update_user_vector_a2(pid, db):
    # Context: Each time user chooses to see a product, this will be recorded in a log in Mongo
    # This function will be called to update user vector
    # Input: database
    # Process: query the newest log, embed and add to current user vector
    # Output: new user vector
    user_log = db['UserLog']
    book_features = db['BookFeatureIndexing']

    # Find the product embedding
    product = book_features.find_one({"key": pid})
    if not product:
        raise ValueError(f"Product with key {pid} not found in BookFeatureIndexing")

    # Insert the product embedding into the user log
    user_element = {
        'key': pid,
        'embedding': product['embedding']
    }
    user_log.insert_one(user_element)

    # Retrieve all embeddings from the user log
    user_vector_it = user_log.find()
    user_vector = []
    for uv in user_vector_it:
        user_vector.append(uv['embedding'])

    if not user_vector:
        return np.zeros_like(product['embedding'])  # Return zero vector if no logs found

    user_vector = np.array(user_vector).mean(axis=0)
    return user_vector

'''
Additional
Create a bag of keywords with stopwords truncated
feed it to a UI bag of words to visualize

'''
def update_search_dict(db):
    # Context: for each search term enterred, this will be recored
    # The search term will be preprocessed to keywords using processing.py
    # each processed keyword will be added to SearchDict
    # close connection and notify add success
    pass

def visualize_search_dict(db):
    # Context: for each new update, this visualization should be updated
    # according to all time search terms
    pass

if __name__ == '__main__':
    # load_vector_database(document, db)
    # key = '121635154'
    # results = search_by_key(key, db)
    # for key in results:
    #     print(key['key'])
    # key = '121635154'
    # x = update_user_vector_a1(key, db)
    # print(x.shape)
    # y = update_user_vector_a2(key, db)
    # print(y.shape)
    # print(cosine_similarity([x], [y])[0][0])
    # print(semantic_search_vector(x, db))
    # print(semantic_search_vector(y, db))
    key2= '72459686'
    print(search_by_key(key2, db))

    
    
