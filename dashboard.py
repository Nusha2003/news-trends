import streamlit as st
import pandas as pd
import psycopg2
import plotly.express as px
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- Connect to Postgres ---
@st.cache_data(ttl=60)
def load_data():
    try:
        # Use environment variables for database connection
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", "5432"),
            dbname=os.getenv("DB_NAME", "newsdb"),
            user=os.getenv("DB_USER", "anusha"),
            password=os.getenv("DB_PASSWORD", "password")
        )
        query = """
            SELECT id, source, title, published, keywords
            FROM posts
            WHERE published IS NOT NULL
            ORDER BY published DESC
            LIMIT 500;
        """
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Database connection failed: {str(e)}")
        # Return sample data for demonstration
        return create_sample_data()

def create_sample_data():
    """Create sample data when database is not available"""
    import datetime
    import random
    
    sources = ["BBC News", "CNN", "Reuters", "The Guardian", "NPR"]
    keywords_list = ["technology", "politics", "business", "health", "sports", "entertainment", "science", "world"]
    
    data = []
    for i in range(50):
        data.append({
            'id': i + 1,
            'source': random.choice(sources),
            'title': f"Sample News Article {i + 1}",
            'published': datetime.datetime.now() - datetime.timedelta(hours=random.randint(0, 24)),
            'keywords': ', '.join(random.sample(keywords_list, random.randint(2, 4)))
        })
    
    return pd.DataFrame(data)

df = load_data()

st.title("📰 Real-Time News Trends Dashboard")

# Check if we're using sample data
if len(df) > 0 and df.iloc[0]['title'].startswith("Sample News Article"):
    st.info("🔍 **Demo Mode**: Currently showing sample data. Connect to a PostgreSQL database to see real news trends!")

# --- Latest Headlines ---
st.subheader("Latest Headlines")
st.dataframe(df[['published', 'source', 'title', 'keywords']].head(20))

# --- Articles per Source ---
st.subheader("Articles per Source")
source_counts = df['source'].value_counts().reset_index()
source_counts.columns = ['source', 'count']
st.plotly_chart(px.bar(source_counts, x='source', y='count', title="Articles per Source"))

# --- Keyword Frequency ---
st.subheader("Top Keywords")
all_keywords = (
    df['keywords'].dropna()
    .str.split(', ')
    .explode()
    .value_counts()
    .reset_index()
)

all_keywords.columns = ['keyword', 'frequency']

st.plotly_chart(px.bar(all_keywords.head(20), x='keyword', y='frequency', title="Top 20 Keywords"))

st.subheader("Articles Over Time")
df['hour'] = pd.to_datetime(df['published']).dt.floor('H')
time_counts = df.groupby(['hour','source']).size().reset_index(name='count')
st.plotly_chart(px.line(time_counts, x='hour', y='count', color='source', title="Articles Over Time"))
