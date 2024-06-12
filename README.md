# Book Streaming

## About the project

In this project, I implemented a basic ETL and streaming pipeline, making use of several Viet NLP techniques to clean and preprocess the data before saving to MongoDB. Also, I made use of logistic regression, KeyBERT and transfer learning model to analyze 3 aspects of a book based on its metadata and descriptions. 
Throughout the project, I was able to give content based recommendations for specific book in the database. 

This is the high-level presentation of the processing flow:

https://drive.google.com/file/d/1D7URvyL28PRY3QJG_dChUlpDF7lQOhjx/view?usp=drive_link

The course reports associated with this project:

[ERP](https://drive.google.com/file/d/1haCMTEdgZPSc6AzD8AlaNa6CsbfmF-qp/view?usp=sharing)

[BigData]()

If you do not have much of time, check this demo video:

[Demo](https://drive.google.com/file/d/1DqAQWNrxSuS-Gn5PxfilrIvVFs26qCQY/view?usp=sharing)

The API key is temporarily open for demo. I will close it soon after though you may not able to access my resources.

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
