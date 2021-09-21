import grpc
import location_pb2
import location_pb2_grpc




print("Sending sample location payload...")

channel = grpc.insecure_channel("localhost:5005")
stub = location_pb2_grpc.LocationServiceStub(channel)

location1 = location_pb2.LocationMessage(
    person_id="9",
    latitude=22.8888,
    longitude=10.5432
)
print("Sending first location...")
stub.Create(location1)


location2 = location_pb2.LocationMessage(
    person_id="1",
    latitude=32.5641,
    longitude=109.3342
)
print("Sending second location...")
stub.Create(location2)

print("Finished")