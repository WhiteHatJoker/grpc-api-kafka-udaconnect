import psycopg2
from kafka import KafkaConsumer
import os
import json
from kafka import KafkaConsumer

KAFKA_SERVER_URL = "kafka-service:9092"
KAFKA_TOPIC_NAME = "locations"


consumer = KafkaConsumer(KAFKA_TOPIC_NAME, bootstrap_servers=[KAFKA_SERVER_URL])
for location in consumer:
    message = location.value.decode('utf-8')
    print('{}'.format(message))