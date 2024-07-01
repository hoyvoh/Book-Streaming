import json
import numpy as np
import pandas as pd
from gensim.models import Word2Vec
from pymongo import MongoClient
from processing import vietnamese_preprocessing

client = MongoClient('localhost', 27017)
db = client['BookDatabase']

def preprocess_text(text):
    return vietnamese_preprocessing(text).split()

def extract_features(data):
    title = data['TITLE']
    cats = data['CATEGORIES']
    feature_tokens = preprocess_text(title) + preprocess_text(cats)
    for feature in data['DESCRIPTION']:
        feature_tokens += preprocess_text(feature) if isinstance(feature, str) else [str(sub) for sub in feature if isinstance(sub, (str, int))]
    return feature_tokens

df = pd.read_csv('./data/rawdata.csv', encoding='utf-8')
cols = ['ID', 'TITLE', 'DESCRIPTION', 'CATEGORIES', 'FEATURES']
initialData = df[cols].to_dict('records')

sentences = [extract_features(data) for data in initialData]

def initialize_models():
    skipgram_model = Word2Vec(sentences=sentences, vector_size=100, window=5, min_count=1, workers=4, sg=1)
    cbow_model = Word2Vec(sentences=sentences, vector_size=100, window=5, min_count=1, workers=4, sg=0)
    skipgram_model.save("./model/skipgram_w2v.model")
    cbow_model.save("./model/cbow_w2v.model")

def update_w2v_model(tokens, path):
    model = Word2Vec.load(path)
    model.build_vocab([tokens], update=True)
    model.train([tokens], total_examples=1, epochs=1)
    model.save(path)

def vectorize_product(product, model):
    return model.wv[product] if product in model.wv else [0] * 100

def queryByTitle(product_title, path, topn=10):
    model = Word2Vec.load(path)
    top_products = model.wv.most_similar(product_title, topn=topn)
    return [product[0] for product in top_products]

def update_user_log(product):
    collection = db['ULW2V']
    doc = {'ID': product['ID'], 'TITLE': product['TITLE']}
    collection.insert_one(doc)

def get10_user_log(path, topn=10):
    collection = db['ULW2V']
    model = Word2Vec.load(path)
    products = collection.find().sort('_id', -1).limit(topn)
    embeddings = [model.wv[title] for title in (product['TITLE'] for product in products) if title in model.wv]
    return np.mean(embeddings, axis=0) if embeddings else [0] * model.vector_size

def get_all_user_log(path):
    collection = db['ULW2V']
    model = Word2Vec.load(path)
    products = collection.find()
    embeddings = [model.wv[title] for title in (product['TITLE'] for product in products) if title in model.wv]
    return np.mean(embeddings, axis=0) if embeddings else [0] * model.vector_size

def w2vsemantic_search_vector(model_path, embedding, topn=10):
    model = Word2Vec.load(model_path)
    # print(embedding)
    similars = model.wv.similar_by_vector(embedding, topn=topn)
    return [sim[0] for sim in similars]

if __name__ == '__main__':
    sample_path = './sample.txt'
    initialize_models()

    with open(sample_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    sample_data = json.loads(content)
    sample_data = {
        'ID': sample_data.get('key'),
        'TITLE': sample_data.get('value').get('TITLE'),
        'DESCRIPTION': sample_data.get('value').get('DESCRIPTION'),
        'CATEGORIES': sample_data.get('value').get('CATEGORIES'),
        'FEATURES': sample_data.get('value').get('FEATURES')
    }

    p_data = extract_features(sample_data)
    path1 = './model/cbow_w2v.model'
    path2 = './model/skipgram_w2v.model'

    update_w2v_model(p_data, path2)
    update_w2v_model(p_data, path1)

    skgmodel = Word2Vec.load(path2)
    cbowmodel = Word2Vec.load(path1)

    feature_vector = skgmodel.wv['Yêu Những Ngày Nắng Chẳng Ghét Những Ngày Mưa']
    f2 = cbowmodel.wv['Yêu Những Ngày Nắng Chẳng Ghét Những Ngày Mưa']
