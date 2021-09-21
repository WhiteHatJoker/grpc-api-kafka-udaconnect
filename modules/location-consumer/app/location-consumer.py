import psycopg2, logging, os, json
from kafka import KafkaConsumer
from kafka import KafkaConsumer

logging.basicConfig(level=logging.INFO)

KAFKA_SERVER_URL = "kafka-service:9092"
KAFKA_TOPIC_NAME = "locations"


consumer = KafkaConsumer(KAFKA_TOPIC_NAME, bootstrap_servers=[KAFKA_SERVER_URL])
for location in consumer:
    message = location.value.decode('utf-8')
    logging.info('{}'.format(message))