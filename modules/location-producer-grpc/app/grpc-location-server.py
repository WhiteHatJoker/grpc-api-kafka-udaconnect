import time, json
from concurrent import futures

import grpc
import location_pb2
import location_pb2_grpc

from kafka import KafkaProducer

# Initialize Kafka producer
KAFKA_SERVER_URL = "kafka-service:9092"
KAFKA_TOPIC_NAME = "locations"
print('Connecting to kafka '+KAFKA_SERVER_URL+' with topic '+KAFKA_TOPIC_NAME)
producer = KafkaProducer(bootstrap_servers=KAFKA_SERVER_URL)
print('Started the Kafka producer')

class LocationServicer(location_pb2_grpc.LocationServiceServicer):
    def Create(self, request, context):

        request_value = {
            'person_id': request.person_id,
            'longitude': request.longitude,
            'latitude': request.latitude
        }
        print("Sending data to Kafka: " +request_value)


        kafka_request = json.dumps(request_value).encode('utf-8')
        producer.send(KAFKA_TOPIC_NAME, kafka_request)
        producer.flush()

        print("Sent data successfully")

        return location_pb2.LocationMessage(**request_value)


# Initialize gRPC server
server = grpc.server(futures.ThreadPoolExecutor(max_workers=2))
location_pb2_grpc.add_LocationServiceServicer_to_server(LocationServicer(), server)

print("Server starting on port 5005...")
server.add_insecure_port("[::]:5005")
server.start()
# Keep thread alive
try:
    while True:
        time.sleep(86400)
except KeyboardInterrupt:
    server.stop(0)





