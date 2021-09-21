import psycopg2, logging, os, json
from kafka import KafkaConsumer
from dotenv import load_dotenv
logging.basicConfig(level=logging.INFO)

KAFKA_SERVER_URL = "kafka-service:9092"
KAFKA_TOPIC_NAME = "locations"

load_dotenv()

DB_NAME = os.environ["DB_NAME"]
DB_USERNAME = os.environ["DB_USERNAME"]
DB_PASSWORD = os.environ["DB_PASSWORD"]
DB_HOST = os.environ["DB_HOST"]
DB_PORT = os.environ["DB_PORT"]

def save_to_db(location_data):
    db_conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USERNAME,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )

    cursor = db_conn.cursor()
    person_id = int(location_data["person_id"])
    latitude = float(location_data["latitude"])
    longitude = float(location_data["longitude"])
    sql = "INSERT INTO location (person_id, coordinate) VALUES ({}, ST_Point({}, {}))".format(person_id, latitude, longitude)
    cursor.execute(sql)
    db_conn.commit()
    cursor.close()
    db_conn.close()



consumer = KafkaConsumer(KAFKA_TOPIC_NAME, bootstrap_servers=[KAFKA_SERVER_URL])

for location in consumer:
    message = location.value.decode('utf-8')
    logging.info('{}'.format(message))
    location_data = json.loads(message)
    logging.info("Saving to database")
    save_to_db(location_data)
    logging.info("Saved to Database")