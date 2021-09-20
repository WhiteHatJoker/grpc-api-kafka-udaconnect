import grpc
import location_pb2
import location_pb2_grpc




print("Sending sample location payload...")

channel = grpc.insecure_channel("localhost:5005")
stub = location_pb2_grpc.LocationServiceStub(channel)

location1 = location_pb2.LocationMessage(
    person_id="9",
    latitude=47.0707,
    longitude=15.4395
)
print("Sending first location...")
stub.Create(location1)


location2 = location_pb2.LocationMessage(
    person_id="1",
    latitude=37.7749,
    longitude=122.4194
)
print("Sending second location...")
stub.Create(location2)

print("Finished")

