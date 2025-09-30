import feedparser
import yaml
import json
import time
from kafka import KafkaProducer

with open("/Users/anusha/news-trends/ingestion/feeds.yaml", "r") as f:
    config = yaml.safe_load(f)
feeds = config["feeds"]
producer = KafkaProducer(
    bootstrap_servers = "localhost:9092",
    value_serializer = lambda v: json.dumps(v).encode("utf-8")
)

seen_links = set()
def poll_feeds():
    """Fetch new entries from all feeds and push to Kafka"""
    for feed in feeds:
        parsed = feedparser.parse(feed["url"])
        for entry in parsed.entries:
            if entry.link not in seen_links:
                event = {
                    "source": feed["name"],
                    "title": entry.title,
                    "link": entry.link,
                    "published": entry.get("published", None),
                    "summary": entry.get("summary", "")
                }
                producer.send("raw_posts", event)
                seen_links.add(entry.link)
                print(f"[{feed['name']}] Produced: {entry.title}")

if __name__ == "__main__":
    print("Starting RSS Producer...")
    while True:
        poll_feeds()
        time.sleep(300)