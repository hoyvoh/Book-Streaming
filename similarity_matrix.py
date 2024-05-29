import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pymongo import ASCENDING
import logging
import atexit
import random
from transformers import AutoTokenizer, AutoModel
import torch

# Load the MiniLM model and tokenizer
tokenizer = AutoTokenizer.from_pretrained('microsoft/MiniLM-L12-H384-uncased')
model = AutoModel.from_pretrained('microsoft/MiniLM-L12-H384-uncased')

pid = random.randint(1, 2000)


'''
This module creates a similarity matrix storing in RAM. 
For each new product, after processing.py module extract the features, this module will be called to update the similarity matrix 
according to the product features{key, features}.
'''

'''
def get_mongo():
    uri = "mongodb+srv://general_user:MongoUser123@cluster0.nex3ywa.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    # Create a new client and connect to the server
    client = MongoClient(uri, server_api=ServerApi('1'))

    # Send a ping to confirm a successful connection
    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)
    return client
client = get_mongo()
db = client['BookDatabase']
collection = db['BookFeaturesIndexing']
collection.create_index([("key", ASCENDING)], unique=True)
'''

# Initialize logging
logging.basicConfig(filename='similarity_matrix.log', level=logging.INFO, format='%(asctime)s %(message)s')

def encode_features(text, max_length = 128):
    print("Encoding features...")
    # Tokenize the input text
    inputs = tokenizer(text, return_tensors='pt', padding=True, truncation=True, max_length=max_length)
    # Pass the tokenized inputs through the model
    with torch.no_grad():
        outputs = model(**inputs)
    # The last hidden state of the [CLS] token is often used as the sentence embedding
    cls_embedding = outputs.last_hidden_state[:, 0, :].squeeze().numpy()
    return cls_embedding

'''
- Similarity matrix :: Object (
    + Init Similarity matrix (empty at first): -> matrix instance
    + Add new product to Similariry Matrix () -> matrix instance
    + similarity evaluator (features using vector embedding and cosine similarity,
                            author, title similarity,
                            bonus: sales probability, 
                            bonus: comments sentiment) -> double recommend_score
    + similarity ranking (sort product row, get top 10 product ids) -> list [top 10 product ids]
    ): -> matrix instance
    + log current content (trigger for every update) -> add current content to log file
    + track system shutdown (system shutdown detect) -> empty current similarity matrix
'''
class Similarity_Matrix:
    def __init__(self) -> None:
        self.matrix = pd.DataFrame()
        self.feature_vectors = {}
        self.product_ids = []
        atexit.register(lambda: self.shutdown_handler())
    def add_product(self, pid, features):
        # format:
        # features = [title, authors(list), keywords(list), sales_prob, positive_prob]
        if pid in self.matrix.index:
            print("do not add duplicate instance.")
            return
        title_embed = encode_features(features[0])
        author_embed = encode_features(', '.join(features[1]))
        f_embeds = encode_features(', '.join(features[2]))
        sales = np.array([features[3]])
        if len(features[4]) != 0:
            pos = np.array([features[4][-1]])
        else:
            pos = np.array([0])
        # combined_features = np.concatenate([title_embed, author_embed, f_embeds])
        combined_features = np.mean([title_embed*0.1, author_embed*0.5, f_embeds*2], axis=0)
        combined_features = np.concatenate([combined_features, sales, pos])
        # combined_features = np.concatenate(mean_features, sales, pos)
        
        # collection.insert_one(doc)
        self.feature_vectors[pid] = combined_features
        self.product_ids.append(pid)
        self._update_matrix(pid)

    def _update_matrix(self, pid):
        try:
            feature_matrix = np.array(list(self.feature_vectors.values()))
            print(feature_matrix.shape)
            similarities = cosine_similarity(feature_matrix)
            print(similarities.shape)
            self.matrix = pd.DataFrame(similarities, index=self.product_ids, columns=self.product_ids)
            self.log_current_content()
        except ValueError as e:
            print(self.product_ids)
            print(e)
            # Find the index of the latest added product
            latest_index = self.product_ids.index(pid)

            # Set all elements in the row and column corresponding to the latest product to 0
            self.matrix.iloc[latest_index, :] = 0  # Set row to 0
            self.matrix.iloc[:, latest_index] = 0  # Set column to 0

            self.log_current_content()
            

    def similarity_evaluator(self, pid):
        if pid not in self.matrix.index:
            return []
        if pid is None:
            return []
        print(pid)
        similarities = self.matrix[pid].sort_values(ascending=False)
        top_10_similarities = similarities.iloc[1:6]
        return list(top_10_similarities.index)
    
    def log_current_content(self):
        logging.info(f"Similarity matrix at \n{self.matrix}\n\n")
    
    def shutdown_handler(self):
        logging.info("System shutting down. Cleaning similarity matrix of current session...")
        self.matrix = pd.DataFrame()
        self.feature_vectors = {}
        self.product_ids=[]

input_example = {
    'key': 50685547,
    'value': ['bản đồ', 'aleksandra mizielińska, daniel mizieliński', ['khổng lồ', 'đầu tiên', 'bản đồ', 'hai', 'thuế nhập khẩu', 'đơn', 'bản đồ', 'quốc gia', 'địa danh', 'trang phục', 'thế giới', 'bản đồ', 'đồng hành', 'con em', 'thông tin', 'bản đồ', 'màu sắc', 'sống động', 'minh họa', 'sinh động', 'Nhà Sách Tiki', ' Sách tiếng Việt', ' Sách văn học', ' Truyện ngắn - Tản văn - Tạp Văn', ' Truyện ngắn - Tản văn - Tạp Văn Nước Ngoài', ' Điều Kỳ Diệu Của Tiệm Tạp Hóa NAMIYA (Tái Bản)'], 1, 1.0]
}
input_example2 = {
    'key': 50685548,
    'value': ['bản đồ', 'aleksandra mizielińska, daniel mizieliński', ['khổng lồ', 'đầu tiên', 'bản đồ', 'hai', 'thuế nhập khẩu', 'đơn', 'bản đồ', 'quốc gia', 'địa danh', 'trang phục', 'thế giới', 'bản đồ', 'đồng hành', 'con em', 'thông tin', 'bản đồ', 'màu sắc', 'sống động', 'minh họa', 'sinh động', 'Nhà Sách Tiki', ' Sách tiếng Việt', ' Sách văn học', ' Truyện ngắn - Tản văn - Tạp Văn', ' Truyện ngắn - Tản văn - Tạp Văn Nước Ngoài', ' Điều Kỳ Diệu Của Tiệm Tạp Hóa NAMIYA (Tái Bản)'], 1, 1.0]
}
input_example3 = {
    'key': 50685528,
    'value': ['Kamenrider', 'aleksandra mizielińska, daniel mizieliński', ['khổng lồ', 'The founding titan', 'The attack titan', 'eremika', 'thuế nhập khẩu', 'đơn', 'bản đồ', 'quốc gia', 'địa danh', 'trang phục', 'thế giới', 'bản đồ', 'đồng hành', 'con em', 'thông tin', 'bản đồ', 'màu sắc', 'sống động', 'minh họa', 'sinh động', 'Nhà Sách Tiki', ' Sách tiếng Việt', ' Sách văn học', ' Truyện ngắn - Tản văn - Tạp Văn', ' Truyện ngắn - Tản văn - Tạp Văn Nước Ngoài', ' chú bé kỳ lạ'], 0.5, 0.0]
}

matrix = Similarity_Matrix()
# atexit.register(lambda: matrix.shutdown_handler())

def main(input_dict, matrix):
    matrix.add_product(input_dict.get('key'), input_dict.get('value'))
    

if __name__ == "__main__":
    from time import time
    start = time()
    main(input_example, matrix)
    end = time()
    print('Insert 1:', end-start)
    main(input_example2, matrix)
    end = time()
    print('Insert 2:', end-start)
    main(input_example3, matrix)
    end = time()
    print('Insert 3:', end-start)
    print(matrix.similarity_evaluator(input_example3.get('key')))
    end = time()
    print('Similarity after:', end-start)