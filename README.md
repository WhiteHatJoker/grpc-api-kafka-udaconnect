# UdaConnect: Monolith to Microservices with gRPC and Kafka on Kubernetes

UdaConnect helps conference attendees find people they were physically close to, using location data from their phones. This project refactors the original monolithic Flask app into independently deployable microservices built to absorb a large inflow of location data, and runs them on Kubernetes.

![Python](https://img.shields.io/badge/Python-Flask--RESTX-yellow) ![gRPC](https://img.shields.io/badge/gRPC-protobuf-244c5a) ![Kafka](https://img.shields.io/badge/Kafka-message%20queue-231f20) ![Postgres](https://img.shields.io/badge/PostgreSQL-PostGIS-336791) ![Kubernetes](https://img.shields.io/badge/Kubernetes-k3s-326ce5)

## Architecture

```
                      ┌────────────────────┐
  Browser ──────────► │ Frontend (React)   │ :30000
                      └─────────┬──────────┘
                                │ REST
              ┌─────────────────┴──────────────────┐
              ▼                                    ▼
   ┌──────────────────────┐           ┌──────────────────────┐
   │ Person API (REST)    │ :30001    │ Location API (REST)  │ :30002
   │ persons + connections│           │ read locations       │
   └──────────┬───────────┘           └──────────┬───────────┘
              │                                  │
              └──────────────┬───────────────────┘
                             ▼
                  ┌───────────────────────┐
                  │ PostgreSQL + PostGIS  │
                  └───────────▲───────────┘
                              │ writes
  Mobile devices ──gRPC──► ┌──┴───────────────────┐
                    :30003 │ Location Producer    │──► Kafka topic "locations"
                           │ (gRPC server)        │          │
                           └──────────────────────┘          ▼
                                              ┌──────────────────────┐
                                              │ Location Consumer    │ :30004
                                              └──────────────────────┘
```

## Design decisions

- **Two domain services, Persons and Locations.** Connections are an action on a person (`/persons/<id>/connection`), so they live in the Person service. Locations are split out because they receive by far the most traffic and need to scale independently.
- **gRPC for ingesting locations.** Mobile clients send small, strongly typed messages at high volume, which is where gRPC's binary protocol pays off. REST is kept for everything the frontend and third parties consume, since it is easier to integrate and test.
- **Kafka between ingestion and storage.** The gRPC server only publishes to Kafka and returns, so bursts of location data are queued instead of overloading the database, and no data is lost if the consumer is slow or restarting.

The full reasoning is in [`docs/architecture_decisions.txt`](docs/architecture_decisions.txt).

## Services

| Service | Path | Tech | NodePort |
|---------|------|------|----------|
| Frontend | `modules/frontend` | React | 30000 |
| Person API | `modules/person-api` | Flask-RESTX, SQLAlchemy, GeoAlchemy2 | 30001 |
| Location API | `modules/location-api` | Flask-RESTX, SQLAlchemy, GeoAlchemy2 | 30002 |
| Location Producer | `modules/location-producer-grpc` | gRPC server + kafka-python producer | 30003 |
| Location Consumer | `modules/location-consumer` | kafka-python consumer → PostGIS insert (psycopg2) | 30004 |
| Kafka + Zookeeper | `deployment/kafka-broker.yaml` | wurstmeister/kafka | internal |
| Database | `deployment/postgres.yaml` | PostGIS 12 | internal |

The gRPC contract ([`location.proto`](modules/location-producer-grpc/app/location.proto)):

```proto
message LocationMessage {
    string person_id = 1;
    float latitude = 2;
    float longitude = 3;
}

service LocationService {
    rpc Create (LocationMessage) returns (LocationMessage);
}
```

## REST endpoints

| Method | Path | Service |
|--------|------|---------|
| GET / POST | `/api/persons` | Person API |
| GET | `/api/persons/<person_id>` | Person API |
| GET | `/api/persons/<person_id>/connection?start_date=&end_date=&distance=` | Person API |
| GET / POST | `/api/locations` | Location API |
| GET | `/api/locations/<location_id>` | Location API |

The OpenAPI spec is in [`docs/openapi.yaml`](docs/openapi.yaml) and a Postman collection in [`docs/postman.json`](docs/postman.json). gRPC usage notes are in [`docs/grpc.txt`](docs/grpc.txt).

## Run it

Requirements: Vagrant and VirtualBox (or any Kubernetes cluster), `kubectl`.

```bash
# 1. Start a VM with k3s installed (see Vagrantfile), then point kubectl at it
vagrant up
vagrant ssh                       # kubectl is available inside the VM

# 2. Deploy everything
kubectl apply -f deployment/

# 3. Seed the database (pass the postgres pod name)
sh scripts/run_db_command.sh $(kubectl get pods -l app=postgres -o jsonpath='{.items[0].metadata.name}')
```

Then open the frontend at `http://localhost:30000`.

To send a test location over gRPC:

```bash
kubectl exec -it <location-producer-grpc-pod> -- python app/grpc-location-client.py
```

## Repository layout

```
deployment/   Kubernetes manifests for every service, Kafka, Zookeeper and PostGIS
modules/      Source and Dockerfile for each service
db/           Schema and seed data
docs/         Architecture decisions, OpenAPI spec, gRPC notes, Postman collection
scripts/      Database seeding helper
```

Container images are published on Docker Hub under `rkhudoyberdiev/`.

---

Built as part of the Udacity Cloud Native Application Architecture Nanodegree. Author: Ravshan Khudoyberdiev.
