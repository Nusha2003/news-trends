from kafka import KafkaConsumer
import psycopg2
import json
import spacy
import re
import uuid
from openai import OpenAI
import os
from dotenv import load_dotenv
import os
from openai import OpenAI

load_dotenv()  # loads from .env
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
import os


# --- Load spaCy model ---
nlp = spacy.load("en_core_web_sm")


def get_embedding(text: str, model="text-embedding-3-small"):
    resp = client.embeddings.create(model=model, input=text)
    return resp.data[0].embedding  # returns a Python list[float]



def new_story_id():
    return str(uuid.uuid4())

def extract_keywords(title: str):
    doc = nlp(title)

    # Named entities (skip pure numbers)
    entities = [ent.text for ent in doc.ents if not ent.text.isdigit()]

    # Noun chunks: skip ones with verbs, strip numbers
    noun_chunks = []
    for chunk in doc.noun_chunks:
        if any(tok.pos_ == "VERB" for tok in chunk):  # skip verb phrases
            continue
        text = re.sub(r'\b\d+\b', '', chunk.text.lower()).strip()
        if text:
            noun_chunks.append(text)

    # Merge + dedup (case-insensitive)
    keywords = list(set([kw.lower() for kw in (entities + noun_chunks)]))

    return keywords


def assign_story_id(title, cursor):
    # Step 1: embed the title
    embedding = get_embedding(title)

    # Step 2: look for nearest neighbors in last 2 days
    cursor.execute(
        """
        SELECT id, story_id, 1 - (embedding <=> %s::vector) AS similarity
        FROM posts
        WHERE published > now() - interval '2 days'
        ORDER BY embedding <=> %s::vector
        LIMIT 1;
        """,
        (embedding, embedding)
    )
    row = cursor.fetchone()

    # Step 3: decide
    if row and row[2] > 0.40:   # if similarity > 0.65
        return row[1], embedding  # reuse existing story_id
    else:
        return str(uuid.uuid4()), embedding 

# --- Connect to Postgres ---
conn = psycopg2.connect(
    host="localhost",
    port=5432,
    dbname="newsdb",
    user="anusha",
    password="password"
)
cursor = conn.cursor()

# --- Connect to Kafka ---
consumer = KafkaConsumer(
    "raw_posts",
    bootstrap_servers="localhost:9092",
    value_deserializer=lambda v: json.loads(v.decode("utf-8")),
    auto_offset_reset="earliest",   # start from beginning if no committed offset
    enable_auto_commit=True
)

print("🚀 Listening for messages and inserting into Postgres...")

# --- Consume and insert loop ---
for message in consumer:
    data = message.value
    title = data.get("title", "")
    keywords = extract_keywords(title)

    # story assignment
    story_id, embedding = assign_story_id(title, cursor)

    try:
        cursor.execute(
            """
            INSERT INTO posts (source, title, link, published, summary, keywords, story_id, embedding)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (link) DO NOTHING;
            """,
            (
                data.get("source"),
                title,
                data.get("link"),
                data.get("published"),
                data.get("summary"),
                ", ".join(keywords) if keywords else None,
                story_id,
                embedding
            )
        )
        conn.commit()
        print(f"✅ Inserted: {title} | story_id={story_id}")
    except Exception as e:
        print(f"⚠️ Failed to insert: {e}")
        conn.rollback()
