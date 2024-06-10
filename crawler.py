import requests
import pandas as pd
from json.decoder import JSONDecodeError
import os
from bs4 import BeautifulSoup
from time import sleep
from tqdm import tqdm
from confluent_kafka import Producer
import json
import os
import shutil
import streaming

'''
from pyspark.sql import SparkSession
scala_version = '2.13'
spark_version = '3.3.0'
packages = [ f'org.apache.spark:spark-sql-kafka-0-10_{scala_version}:{spark_version}' , 'org.apache.kafka:kafka-clients:3.7.0' ]
spark = SparkSession.builder.master("local").appName("BookStreaming").config("spark.jars.packages", ",".join(packages)).getOrCreate()
spark
'''

pids = pd.read_csv('product_id.csv')
pids = pids['id'].tolist()

'''
get data line by line from the sources, then wait for them to be transferred through kafka
continue after 5 seconds
'''
def collect_id():
    # Prepare params for requests
    # These can be found in the header of the specific page
    url = "https://tiki.vn/api/personalish/v1/blocks/listings"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9,vi;q=0.8,en-GB-oxendict;q=0.7',
        'Referer': 'https://tiki.vn/sach-truyen-tieng-viet/c316',
        'x-guest-token': 'GeQTmdpCbu62Mh7H4YcrLyxOf0g9tlnz',
        'Connection': 'keep-alive',
        'TE': 'Trailers',
    }

    params = {
        'limit': '40',
        'include': 'advertisement',
        'aggregations': '2',
        'version': 'home-persionalized',
        'trackity_id': '2800160b-e67c-dbbe-acee-aa456fe56391',
        'category': '316',
        'page': '1',
        'urlKey': 'sach-truyen-tieng-viet',
    }

    # Crawl product ID
    PRODUCT_ID = []
    # Loop over pages to collect product ID
    for i in range(1, 50):
        params['page'] = i
        response = requests.get(url, headers = headers, params=params)
        if response.status_code == 200:
            #print('request success!!!')
            for record in response.json().get('data'):
                PRODUCT_ID.append({'id':record.get('id')})

    # Export to CSV
    df = pd.DataFrame(PRODUCT_ID)
    df.to_csv("product_id.csv", index = False)
    pids = df['id'].tolist()
    return pids

cookies = {
    '_trackity' : '2800160b-e67c-dbbe-acee-aa456fe56391',
    '_ga' : 'GA1.1.2143359731.1708479159',
    '_gcl_au' : '1.1.1375745338.1708479164',
    '_fbp' : 'fb.1.1708479165728.2096489545',
    '__uidac' : '0165d552c2eab78539cbe5e852e13fd9',
    'dtdz' : '1018a45a-a5c2-521e-bd51-b7d8ffb78995',
    '__iid' : '749',
    '__iid' : '749',
    '__su' : '0',
    '__su' : '0',
    'TOKENS': '{%22access_token%22:%22GeQTmdpCbu62Mh7H4YcrLyxOf0g9tlnz%22}',
    '_hjSessionUser_522327' : 'eyJpZCI6IjdhNjkxNDk5LWI2NzAtNTNkOS1hZjgyLWQ5ZTc2ZDM4YTE5MSIsImNyZWF0ZWQiOjE3MDg0NzkxNjc1NjQsImV4aXN0aW5nIjp0cnVlfQ==',
    '__R':'3',
    '__tb':'0',
    'cto_bundle': '-R6vO19QY0xuNTZweU9ONldMYVpBeTJiQXUlMkZhdlVLNkdVTlFXVE5UcWV1ZlU5SHFhWjZjJTJCSkNLM3ElMkZsckU0ZiUyQjN0dGNjSCUyRkMwQnlDZGZtZEolMkJRcVBLcVlKS1UxMTl2QiUyRmUyOSUyQjNucTZOWGZMQzYxd3AlMkZTYk93WXM5TVA3V0F6TENtSVVlN3VwTWF5ZXZRalVIRmtJamZPYWRaRjRjQ29DYlZQNnV5VXZTJTJCamF0YyUzRA',
    'TIKI_RECOMMENDATION' : '19d4cd1530f2deef46b1161777003c47',
    'TKSESSID' : '394a240f18cf08eadac2debe1413e1ab',
    '__RC' : '5',
    '__IP' : '1953376659',
    'delivery_zone' : 'Vk4wMzkwMDYwMDE=',
    'tiki_client_id' : '2143359731.1708479159',
    '_hjSession_522327': 'eyJpZCI6IjkyZTEzMmRlLTM2NTItNGExNi1iZmY4LTNjYzc5NzEzYWI5YyIsImMiOjE3MTA1OTgzMzAyNjksInMiOjAsInIiOjAsInNiIjowLCJzciI6MCwic2UiOjAsImZzIjowfQ==',
    'amp_99d374' : 'Z1PJkLzRqF6lrqU5eacXAB...1hp3ploc2.1hp3sn3p4.ch.e3.qk',
    '__uif' : '__uid%3A3681878040457665689%7C__ui%3A1%252C5%7C__create%3A1681878040',
    '_ga_S9GLR1RQFJ' : 'GS1.1.1710601502.13.0.1710601551.11.0.0',
}

url = 'https://tiki.vn/api/v2/products/{}'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.9,vi;q=0.8,en-GB-oxendict;q=0.7',
    'Referer': 'https://tiki.vn/de-men-phieu-luu-ky-p10920495.html?itm_campaign=CTP_YPD_TKA_PLA_UNK_ALL_UNK_UNK_UNK_UNK_X.287385_Y.1869705_Z.3921146_CN.AUTO---De-Men-Phieu-Luu-Ky---2024%2F02%2F22-10%3A55%3A45&itm_medium=CPC&itm_source=tiki-ads&spid=10920496',
    'x-guest-token': 'GeQTmdpCbu62Mh7H4YcrLyxOf0g9tlnz',
    'Connection': 'keep-alive',
    'TE': 'Trailers',
}

params = {
    'platform': 'web',
    'spid': 187266106,
}


def create_img_dir():
    directory = "./website/static/book_img" # website\static\book_img

    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Directory '{directory}' created successfully.")
    else:
        print(f"Directory '{directory}' already exists.")
        shutil.rmtree(directory)
        os.makedirs(directory)

from requests.exceptions import RequestException

def parse_description(html):
    # Parse the HTML content
    soup = BeautifulSoup(html, 'html.parser')
    # Extract the text without HTML tags
    text = soup.get_text(separator='', strip=True)
    return text

# Function to parse comments from JSON
def parse_comment(json_data):
    comments = []
    data = json_data.get('data')
    if data:
        for dt in data:
            try:
                comment = {
                    'CommentID': dt.get('id'),
                    'CommentTitle': dt.get('title'),
                    'Content': parse_description(dt.get('content')),
                    'rating': dt.get('rating'),
                    'thank_count': dt.get('thank_count'),
                    'User': dt.get('created_by', {}).get('full_name'),
                    'ProductID': dt.get('product_id')
                }
                comments.append(comment)
            except AttributeError as e:
                print(f"Attribute error: {e} in data: {dt}")
                comment = {
                    'CommentID': dt.get('id'),
                    'CommentTitle': dt.get('title'),
                    'Content': parse_description(dt.get('content')),
                    'rating': dt.get('rating'),
                    'thank_count': dt.get('thank_count'),
                    'User': 'Người dùng ẩn danh',
                    'ProductID': dt.get('product_id')
                }
                comments.append(comment)
    return comments

def fetch_comments(pid, page):
    c_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9,vi;q=0.8,en-GB-oxendict;q=0.7',
        'Referer': 'https://tiki.vn/sach-truyen-tieng-viet/c316',
        'x-guest-token': 'GeQTmdpCbu62Mh7H4YcrLyxOf0g9tlnz',
        'Connection': 'keep-alive',
        'TE': 'Trailers',
    }

    c_cookies = {
        '_trackity': '2800160b-e67c-dbbe-acee-aa456fe56391', 
        '_ga': 'GA1.1.2143359731.1708479159', 
        '_gcl_au': '1.1.1375745338.1708479164', 
        '_fbp': 'fb.1.1708479165728.2096489545', 
        '__uidac': '0165d552c2eab78539cbe5e852e13fd9', 
        'dtdz': '1018a45a-a5c2-521e-bd51-b7d8ffb78995', 
        '__iid': '749', 
        '__iid': '749', 
        '__su': '0', 
        '__su': '0', 
        'TOKENS': '{"access_token":"GeQTmdpCbu62Mh7H4YcrLyxOf0g9tlnz"}', 
        '_hjSessionUser_522327': 'eyJpZCI6IjdhNjkxNDk5LWI2NzAtNTNkOS1hZjgyLWQ5ZTc2ZDM4YTE5MSIsImNyZWF0ZWQiOjE3MDg0NzkxNjc1NjQsImV4aXN0aW5nIjp0cnVlfQ==', 
        '__R': '3', 
        '__tb': '0', 
        'cto_bundle': '-R6vO19QY0xuNTZweU9ONldMYVpBeTJiQXUlMkZhdlVLNkdVTlFXVE5UcWV1ZlU5SHFhWjZjJTJCSkNLM3ElMkZsckU0ZiUyQjN0dGNjSCUyRkMwQnlDZGZtZEolMkJRcVBLcVlKS1UxMTl2QiUyRmUyOSUyQjNucTZOWGZMQzYxd3AlMkZTYk93WXM5TVA3V0F6TENtSVVlN3VwTWF5ZXZRalVIRmtJamZPYWRaRjRjQ29DYlZQNnV5VXZTJTJCamF0YyUzRA', 
        'TIKI_RECOMMENDATION': '19d4cd1530f2deef46b1161777003c47', 
        'TKSESSID': '394a240f18cf08eadac2debe1413e1ab', 
        '__RC': '5', 
        '__IP': '1953376659', 
        'delivery_zone': 'Vk4wMzkwMDYwMDE=', 
        'tiki_client_id': '2143359731.1708479159', 
        '_hjSession_522327': 'eyJpZCI6IjkyZTEzMmRlLTM2NTItNGExNi1iZmY4LTNjYzc5NzEzYWI5YyIsImMiOjE3MTA1OTgzMzAyNjksInMiOjAsInIiOjAsInNiIjowLCJzciI6MCwic2UiOjAsImZzIjowfQ==',
        'amp_99d374': 'Z1PJkLzRqF6lrqU5eacXAB...1hp3ploc2.1hp3sn3p4.ch.e3.qk', 
        '__uif': '__uid%3A3681878040457665689%7C__ui%3A1%252C5%7C__create%3A1681878040', 
        '_ga_S9GLR1RQFJ': 'GS1.1.1710601502.13.0.1710601551.11.0.0',
    }

    c_url = 'https://tiki.vn/api/v2/reviews'
    
    c_params = {
        'limit': '20',
        'include': 'comments,contribute_info,attribute_vote_summary',
        'page': str(page),
        'product_id': str(pid),
        'spid': str(pid),
        'seller_id': '1'
    }
    retries = 3
    while retries > 0:
        try:
            response = requests.get(c_url, headers=c_headers, params=c_params, cookies=c_cookies, timeout=10)
            response.raise_for_status()
            return parse_comment(response.json())
        except RequestException as e:
            print(f"Request error for product {pid} page {page}: {e}. Retrying...")
            retries -= 1
            # time.sleep(5)  # wait before retrying
        except json.JSONDecodeError as e:
            print(f"JSON decode error for product {pid} page {page}: {e}. Skipping...")
            return []
    return []

def get_comment(pid):
    comments = []
    for page in range(1, 5):
        comment = fetch_comments(pid, page)
        comments.append(comment)
    
    comments = [c for comment in comments for c in comment]
    return comments

def parser_product(json):
    # Define a dictionary of columns to return
    d = dict()
    # Append each key and value parsing from json file
    d['ID'] = str(json.get('id'))
    d['STOCK_KEEPING_UNIT'] = json.get('sku')
    d['TITLE'] = json.get('name')
    # Since there are many authors, we have to loop by each to extract their name
    authors = json.get('authors')
    if authors:
        author_names = ', '.join(author.get('name') for author in authors)
        d['AUTHORS'] = author_names
    else:
        d['AUTHORS'] = ''
    d['PRICE'] = str(json.get('price'))
    d['ORIGINAL_PRICE'] = str(json.get('original_price'))
    d['RATING_AVERAGE'] = str(json.get('rating_average'))
    d['REVIEW_COUNT'] = str(json.get('review_count'))
    d['INVENTORY_STATUS'] = str(json.get('inventory_status'))
    d['all_time_quantity_sold'] = str(json.get('all_time_quantity_sold'))
    d['DESCRIPTION'] = parse_description(json.get('description'))
    breadcrums = json.get('breadcrumbs')
    cats = []
    for b in breadcrums:
        if b.get('category_id') == "8322" or b.get('category_id') == '0':
            continue
        else:
            cats.append(b.get('name'))
    d['CATEGORIES'] = ", ".join(cats)

    current_seller = json.get('current_seller')
    if current_seller:
        d['SELLER_ID'] = current_seller.get('id')
        d['SELLER_NAME'] = current_seller.get('name')
    else:
        d['SELLER_ID'] = ''
        d['SELLER_NAME'] = ''
    
    # list of 20 top comments per product
    d['COMMENTS'] =  get_comment(json.get('id'))

    images = json.get('images')[0]
    # it = 1
    # for img in images:
    #     url = img.get('medium_url')
    #     response = requests.get(url)
    #     if response.content:
    #         filename = f"./website/static/book_img/{json.get('id')}_{it}.jpg" # website\static\book_img
    #         with open(filename, 'wb') as f:
    #             f.write(response.content)
    #         #print(f"Image downloaded successfully to: {id}_{it}.jpg")
    #         it = it+1
    #     else:
    #         print(f"Failed to download image from {url}")
    uri = images.get('medium_url')
    response = requests.get(uri)
    if response.content:
        filename = f"./website/static/book_img/{json.get('id')}.jpg" # website\static\book_img
        with open(filename, 'wb') as f:
            f.write(response.content)
        #print(f"Image downloaded successfully to: {id}_{it}.jpg")
    else:
        print(f"Failed to download image from {uri}")

    
    return d


def read_config():
  # reads the client configuration from client.properties
  # and returns it as a key-value map
  config = {}
  with open("client.properties") as fh:
    for line in fh:
      line = line.strip()
      if len(line) != 0 and line[0] != "#":
        parameter, value = line.strip().split('=', 1)
        config[parameter] = value.strip()
  return config

'''
# produces a sample message
    key = "key"
    value = "value"
    producer.produce(topic, key=key, value=value)
    print(f"Produced message to topic {topic}: key = {key:12} value = {value:12}")
'''

def main():
    streaming.create_kafka_topic()
    config = read_config()
    topic = "BookStreaming"
    
    # creates a new producer instance
    producer = Producer(config)

    # create_img_dir()
    for pid in tqdm(pids, total = len(pids)):
        response = requests.get(url.format(pid), headers=headers, params=params, cookies = cookies)
        if response.status_code == 200 and response.text:
            sleep(2)
            try:
                result = parser_product(response.json())
                #print(result)
                # print(list(result.values()))
                # values = str('///'.join(list(result.values())))
                # print(values)
                
                key = str(pid)
                value = json.dumps(result)
                # print(value)
                
                producer.produce(topic, key=key, value=value)
                #result.append(parser_product(response.json()))
            except JSONDecodeError as e:
                print("Error parsing JSON:", e)
        else:
            print('Failed request for product ID:', pid)
    
    # send any outstanding or buffered messages to the Kafka broker
    producer.flush()

def collect_all():
    results = []
    create_img_dir()
    for pid in tqdm(pids, total = len(pids)):
        response = requests.get(url.format(pid), headers=headers, params=params, cookies = cookies)

        if response.status_code == 200 and response.text:
            sleep(5)
            try:
                result = parser_product(response.json())
                print(result)
                results.append(result)
                #result.append(parser_product(response.json()))
            except JSONDecodeError as e:
                print("Error parsing JSON:", e)
        else:
            print('Failed request for product ID:', pid)

if __name__ == '__main__':
    # test
    main()