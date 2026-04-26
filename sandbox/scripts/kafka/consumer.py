from confluent_kafka import Consumer
import json

consumer = Consumer(
    {
        "bootstrap.servers": "localhost:9092",
        "group.id": "discovery-group-1",
        # "auto.offset.reset": "earliest",
        "enable.auto.commit": True,
    }
)

consumer.subscribe(["asset.ingestion"])

print("Listening for messages…")
while True:
    msg = consumer.poll(3.0)  # 1 second timeout
    print(msg)
    if msg is None:
        continue
    if msg.error():
        print("Error:", msg.error())
        continue
    event = json.loads(msg.value().decode())
    print("Received:", event)
