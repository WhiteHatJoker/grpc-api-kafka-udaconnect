FROM python:3.8

WORKDIR .

ENV GRPC_TRACE 'transport_security,tsi'
ENV GRPC_VERBOSITY 'DEBUG'

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

EXPOSE 5000

COPY . .

ENTRYPOINT [ "python", "app/grpc-location-server.py" ]