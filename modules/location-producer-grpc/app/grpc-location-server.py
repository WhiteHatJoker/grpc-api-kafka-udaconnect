import time, json, logging
from concurrent import futures

import grpc
import location_pb2
import location_pb2_grpc

from kafka import KafkaProducer

logging.basicConfig(level=logging.INFO)

# Initialize Kafka producer
KAFKA_SERVER_URL = "kafka-service:9092"
KAFKA_TOPIC_NAME = "locations"
logging.info('Connecting to kafka '+KAFKA_SERVER_URL+' with topic '+KAFKA_TOPIC_NAME)
producer = KafkaProducer(bootstrap_servers=KAFKA_SERVER_URL)
logging.info('Started the Kafka producer')

class LocationServicer(location_pb2_grpc.LocationServiceServicer):
    def Create(self, request, context):

        request_value = {
            'person_id': request.person_id,
            'longitude': request.longitude,
            'latitude': request.latitude
        }
        logging.info(request_value)
        kafka_request = json.dumps(request_value).encode('utf-8')
        producer.send(KAFKA_TOPIC_NAME, kafka_request)
        producer.flush()

        logging.info("Sent data successfully to Kafka")

        return location_pb2.LocationMessage(**request_value)


# Initialize gRPC server
server = grpc.server(futures.ThreadPoolExecutor(max_workers=2))
location_pb2_grpc.add_LocationServiceServicer_to_server(LocationServicer(), server)

logging.info("Server starting on port 5005...")
server.add_insecure_port("[::]:5005")
server.start()
# Keep thread alive
try:
    while True:
        time.sleep(86400)
except KeyboardInterrupt:
    server.stop(0)