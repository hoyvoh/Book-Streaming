'''
GLOVE BATCH LEARNING
- Initial training
- Save Model

- Collect/track batch data {batch_id:1, item_id:0} 
- Train model if item_id==49, reset item_id to 0 and iterate batch_id and save model

- Record list of key:ID, value:title to DB

- Get 10 last seen titles, convert to embedding, mean of them is the user vector

- Get all seen titles, convert to embedding, mean of them is the user vector
'''
import numpy as np
from gensim.models import Word2Vec
from pymongo import MongoClient
from wordtovec import extract_features
from pandas import read_csv

df = read_csv('./data/rawdata.csv', encoding='utf-8')
cols = ['ID', 'TITLE', 'DESCRIPTION', 'CATEGORIES', 'FEATURES']
initialData = df[cols].to_dict('records')

sentences = [extract_features(data) for data in initialData]

client = MongoClient('localhost', 27017)
db = client['BookDatabase']

class GloveBatchTraining:
    def __init__(self, embedding_size=100):
        self.embedding_size = embedding_size
        self.path = './model/glove_embedding.model'
        self.model = Word2Vec.load(self.path)
        self.batch_data = []
        self.batch_id = 1
        self.item_id = 0
        self.collection = db['ULW2V']
    
    def initial_training(self, features=sentences):
        self.model = Word2Vec(sentences=features, vector_size=self.embedding_size, window=5, min_count=1, workers=4)
        self.model.save(self.path)
    
    def collect_batch_data(self, title, description, categories, features):
        if title and description and categories and features:
            text_data = title.split() + description.split() + categories.split() + features.split()
            self.batch_data.append(text_data)
            self.item_id += 1
            if self.item_id == 50:
                self.item_id = 0
                self.batch_id += 1
                self.train_model()
                #self.save_model(self.path)
    
    def train_model(self):
        if not self.model:
            print('GloVe initialized.')
            self.initial_training()

        self.model.build_vocab(self.batch_data, update=True)
        self.model.train(self.batch_data, total_examples=self.model.corpus_count, epochs=self.model.epochs)
        self.model.save(self.path)
        self.batch_data = []

    def refresh_model(self):
        print('GloVe Refreshed')
        self.model = Word2Vec.load(self.path)

    def get_embedding(self, title):
        # self.refresh_model()
        return self.model.wv[title] if title in self.model.wv else np.zeros(self.embedding_size)

    def get_user_vector(self, last_n=10):
        self.refresh_model()
        cursor = self.collection.find().sort([('_id', -1)]).limit(last_n)
        embeddings = [self.get_embedding(doc.get('TITLE')) for doc in cursor]
        # print('User vector 10')
        # print(embeddings)
        return np.mean(embeddings, axis=0) if embeddings else np.zeros(self.embedding_size)

    def get_user_vector_all(self):
        self.refresh_model()
        cursor = self.collection.find()
        embeddings = [self.get_embedding(doc.get('TITLE')) for doc in cursor]
        # print('User vectors all')
        # print(embeddings)

        return np.mean(embeddings, axis=0) if embeddings else np.zeros(self.embedding_size)

    def get_most_similars(self, embedding):
        self.refresh_model()
        # print('search similar')
        # print(embedding)
        titles = self.model.wv.similar_by_vector(embedding)
        titles = [title[0] for title in titles]
        return titles

if __name__ == '__main__':
    glove = GloveBatchTraining()
    glove.initial_training()
