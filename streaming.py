import requests
import json
import subprocess
import threading

# Create a kafka topic to remote 
def create_kafka_topic():
    url = "https://pkc-12576z.us-west2.gcp.confluent.cloud:443/kafka/v3/clusters/lkc-1d259v/topics"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Basic U1hGU0dGSTZHWklHQ1FIVjpiM1p6OEZoUXQwWWZ2U1RxYnBLWmwzK2ptczhFYlZVbmNPZm95SHhnUzlJSElRakNVaE03b0h5dEVTSkFVeEVw"
    }
    data = {
        "topic_name": "BookStreaming"
    }
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200:
        print("Kafka topic created successfully!")
    else:
        print("Failed to create Kafka topic. Status code:", response.status_code)
        print("Error message:", response.text)

def start_zookeeper():
    try:
        subprocess.run(["C:\\kafka_2.12-3.6.0\\bin\\windows\\zookeeper-server-start.bat", "C:\\kafka_2.12-3.6.0\\config\\zookeeper.properties"], shell=True, check=True)
        print("Zookeeper server started successfully!")
    except subprocess.CalledProcessError as e:
        print("Failed to start Zookeeper server:", e)

def start_kafka():
    try:
        subprocess.run(["C:\\kafka_2.12-3.6.0\\bin\\windows\\kafka-server-start.bat", "C:\\kafka_2.12-3.6.0\\config\\server.properties"], shell=True, check=True)
        print("Kafka server started successfully!")
    except subprocess.CalledProcessError as e:
        print("Failed to start Kafka server:", e)

if __name__ == '__main__':
    create_kafka_topic()
    zookeeper_thread = threading.Thread(target=start_zookeeper)
    kafka_thread = threading.Thread(target=start_kafka)

    zookeeper_thread.start()
    kafka_thread.start()

    zookeeper_thread.join()
    kafka_thread.join()
