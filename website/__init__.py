from flask import Flask
from pymongo import MongoClient


def get_mongo():
    # uri = "mongodb+srv://general_user:MongoUser123@cluster0.nex3ywa.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0&tls=true"
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

'''
Run crawler.py: data -> kafka
Run consumer.py: kafka -> pymongo -> similarity matrix -> recommendations
Run Flask app to display all products being added and for each, a detail page
'''

client = get_mongo()
db = client['BookDatabase']
collection = db['BookCollection']

def init_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'thisisasecretkey' # Encrypt session data
    
    from .products import product

    app.register_blueprint(product, url_prefix='/')
    # create and export mongo database
    return app
    

def run_flask(app):
    app.run(debug=True)

if __name__ == '__main__':
    """with ThreadPoolExecutor() as executor:
        executor.submit(crawler.main)
        executor.submit(consumer.consume_messages)
        executor.submit(run_flask)
        while True:
            time.sleep(1)"""
    
    app = init_app()
    run_flask(app)



