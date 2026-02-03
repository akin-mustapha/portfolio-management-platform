from confluent_kafka import Producer
import json

# Connect to your Kafka broker
producer = Producer({
    "bootstrap.servers": "localhost:9092"
})

# Example message
event = {
    "asset_id": "AAPL",
    "source": "yfinance",
    "as_of": "2026-02-02"
}

def delivery_report(err, msg):
    print(msg.topic())
    print(msg.partition())
    print(err)
    if err is not None:
        print(f"Message delivery failed: {err}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition()}] at offset {msg.offset()}")

# Update produce call
producer.produce("asset", json.dumps(event), callback=delivery_report)
producer.poll(3.0) # Serve delivery reports
producer.flush()


print("Message produced ✅")