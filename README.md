# Book Streaming

## Abstract

The expansion of the online marketplace has amplified the need for effective recommender systems to connect consumers with relevant products. This report explores and compares various product2vec strategies for embedding and recommending books. We implemented three key recommendation strategies: static vector, ten past products, and all past products, using vectorization techniques such as Bert-based embeddings, Continuous Bag of Words (CBOW), continuous skip-gram, and global vectors (GloVe). To improve feature extraction, we applied Natural Language Processing (NLP) techniques to book data before vectorization. More importantly, we implemented inference on three types of training techniques, the pre-trained BERT is only for inference, the online training for Word2Vec models, and the batch training strategy for GloVe, to deal with the streaming data using Confluent directly from Tiki.vn website. Our study presents a comparative analysis of 12 different recommendation approaches, highlighting their effectiveness in predicting ten books for each user. The findings aim to enhance recommender system research and development, offering valuable insights into optimizing recommendation accuracy and relevance.

*Keywords:* Recommender system, vector, vector-based, book, NLP, GloVe, BERT, word2vec

The course reports associated with this project:

[ERP](https://drive.google.com/file/d/1haCMTEdgZPSc6AzD8AlaNa6CsbfmF-qp/view?usp=sharing)

[BigData](https://www.overleaf.com/read/kcjcgxnpttnd#7d29a3)

The API key is temporarily open for demo. I will close it soon after though you may not be able to access my resources.

## Environment

Python3.12

Visual Studio C++ build tools
- MSVC v143 - VS 2022 C++ x64/x86 build tool
- C++ CMake tool for Windows
- C++ AddressSanitizer
- C++ Modules for v143 - VS 2022 C++ x64/x86
- Windows 10/11 SDK

## Usage tutorial

*Note that the tutorial is written for Windows users*

### Step 1: Install MongoDB and Config a Confluent Kafka

Check this link: https://www.mongodb.com/try/download/community

Create "BookDatabase", and "BookCollection" in your MongoCompass.

Register a Confluent Kafka: https://confluent.cloud/

### Step 2: Clone the project

```
git clone https://github.com/hoyvoh/Book-Streaming.git
```

### Step 3: Activate venv and install required packages

```
python -m venv env

./env/Scripts/activate

pip install -r requirements.txt
```

# Step 4: Run the demo

Open 3 terminal, each of them, run one command.

```
python crawler.py
```

```
python consumer.py
```

```
python app.py
```
