import streamlit as st
import pandas as pd
import psycopg2
import plotly.express as px

# --- Connect to Postgres ---
@st.cache_data(ttl=60)
def load_data():
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        dbname="newsdb",
        user="anusha",
        password="password"
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

df = load_data()

st.title("📰 Real-Time News Trends Dashboard")

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
