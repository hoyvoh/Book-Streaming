from confluent_kafka import Consumer
import json
import sys
from pymongo.mongo_client import MongoClient
from json.decoder import JSONDecodeError
import processing
# import similarity_matrix
import vectorizer
import numpy as np
import wordtovec
import glove

def get_mongo():
    # uri = "mongodb+srv://[USERNAME]:[PASSWORD]@cluster0.nex3ywa.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0&tls=true"
    uri = 'mongodb://localhost:27017/'
    # Create a new client and connect to the server tlsCAFile=isrgrootx1.pem
    client = MongoClient(uri) # , server_api=ServerApi('1')

    # Send a ping to confirm a successful connection
    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)
    return client

def read_config():
    config = {}
    try:
        with open("client.properties") as fh:
            for line in fh:
                line = line.strip()
                if len(line) != 0 and line[0] != "#":
                    parameter, value = line.strip().split('=', 1)
                    config[parameter] = value.strip()
    except FileNotFoundError:
        print("Configuration file 'client.properties' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading configuration file: {e}")
        sys.exit(1)
    return config

def convert_numpy_types(data):
    if isinstance(data, dict):
        return {k: convert_numpy_types(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_numpy_types(v) for v in data]
    elif isinstance(data, np.int64):
        return int(data)
    elif isinstance(data, np.float64):
        return float(data)
    else:
        return data

# matrix = similarity_matrix.Similarity_Matrix()
import pandas as pd
def consume_messages():
    config = read_config()
    wordtovec.initialize_models()
    skgpath = './model/skipgram_w2v.model'
    cbowpath = './model/cbow_w2v.model'
    glove_model = glove.GloveBatchTraining()

    if not config:
        print("Configuration could not be read. Exiting.")
        return

    topic = "BookStreaming"
    # sets the consumer group ID and offset  
    config["group.id"] = "python-group-2"
    config["auto.offset.reset"] = "earliest"

    alldata = []

    # creates a new consumer and subscribes to your topic
    consumer = Consumer(config)
    consumer.subscribe([topic])
    
    client = get_mongo()
    db = client['BookDatabase']
    collection = db['BookCollection']
    collection.drop()
    book_feature = db['BookFeatureIndexing']
    book_feature.drop()
    print("collection renewed!")
    
    import copy
    try:
      while True:
        # consumer polls the topic and prints any incoming messages
        # sleep(2)
        msg = consumer.poll(1.0)
        #print(msg)
        if msg is not None and msg.error() is None:
            key = msg.key().decode("utf-8")
            value = msg.value().decode("utf-8")
            # print(f"Consumed message from topic {topic}: key = {key} value = {value}")
            
            try:
                value_dict = json.loads(value)

                value_dict_2 = copy.deepcopy(value_dict)
                # test_pid = key
                # test_title = value_dict['TITLE']
                # test_auth = value_dict['AUTHORS']
                # print(value_dict['TITLE'])

                features, document = processing.main(value_dict_2)
                value_dict['FEATURES'] = features
                print(value_dict['TITLE'])
            

                # alldata.append({
                #      'ID': value_dict['ID'],
                #      'TITLE': value_dict['TITLE'],
                #      'DESCRIPTION': value_dict['DESCRIPTION'],
                #      'CATEGORIES' : value_dict['CATEGORIES'],
                #      'FEATURES': value_dict['FEATURES']
                # })

                # Use similarity matrix
                # similarity_matrix.main(document, matrix)
                # recommended = matrix.similarity_evaluator(test_pid)
                # print(f'Recommend for {test_pid} | {test_title} | {test_auth}: ', recommended)
                # value_dict['RECOMMENDED'] = recommended
                
                doc = {
                    'key':key,
                    'value': convert_numpy_types(value_dict)
                }
                # insert product
                collection.insert_one(doc)
                print("insert {} successfully.".format(doc['key']))

                # Use dynamic vector indexing
                # load 1 to vector database
                vectorizer.load_vector_database(doc, db)
                print(skgpath, 'starts learning', value_dict.get('TITLE'))
                wordtovec.update_w2v_model(value_dict, skgpath)
                print(cbowpath, 'starts learning', value_dict.get('TITLE'))
                wordtovec.update_w2v_model(value_dict, cbowpath)
                print('GloVe starts learning', value_dict.get('TITLE'))
                glove_model.collect_batch_data(
                    title=value_dict.get('TITLE'),
                    description=value_dict.get('DESCRITION'),
                    categories=value_dict.get('CATEGORIES'),
                    features=value_dict['FEATURES']
                )

                
            except JSONDecodeError as e:
                print(e)
    except KeyboardInterrupt:
      pass
    finally:
      # closes the consumer connection
        # df = pd.DataFrame(alldata)
        # df.to_csv('./data/rawdata.csv')
        consumer.close()

if __name__ == '__main__':
    print("Starting the Kafka consumer...")
    consume_messages()
    print("Kafka consumer stopped.")
