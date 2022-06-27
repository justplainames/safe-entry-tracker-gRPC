#Specifying the base image
FROM python:3.10

COPY reproducible_data.csv .
COPY safeEntry.csv .
COPY safeEntry.proto .
COPY safeEntry_client.py .
COPY safeEntry_pb2.py .
COPY safeEntry_pb2_grpc.py .
COPY safeEntry_server.py .

RUN python -m pip install grpcio
RUN python -m pip install grpcio-tools
RUN python -m pip install pandas

ENTRYPOINT ["tail", "-f", "/dev/null"]




