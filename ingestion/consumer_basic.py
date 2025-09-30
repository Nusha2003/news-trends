from kafka import KafkaConsumer
import json

consumer = KafkaConsumer(
    "raw_posts",
    bootstrap_servers = "localhost:9092",
    value_deserializer = lambda v: json.loads(v.decode("utf-8")),
    auto_offset_reset = "earliest",
    enable_auto_commit=True
)

print("Listening for messages")
for message in consumer:
    print(message.value)