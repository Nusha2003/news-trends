import streamlit as st
import psycopg2
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
from dotenv import load_dotenv
import os
from database_utils import get_db_connection, get_latest_news, get_news_by_source, get_trending_stories, get_news_by_keyword, get_news_stats

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="News Trends Dashboard",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #667eea;
    }
    .news-card {
        background-color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        border-left: 4px solid #667eea;
    }
    .source-badge {
        background-color: #667eea;
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        font-size: 0.8rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Header
    st.markdown('<h1 class="main-header">📰 News Trends Dashboard</h1>', unsafe_allow_html=True)
    
    # Sidebar for navigation and filters
    with st.sidebar:
        st.header("🔍 Filters & Controls")
        
        # Date range filter
        st.subheader("📅 Date Range")
        days_back = st.selectbox(
            "Show news from last:",
            [1, 3, 7, 14, 30],
            index=2,
            format_func=lambda x: f"{x} day{'s' if x > 1 else ''}"
        )
        
        # Source filter
        st.subheader("📺 News Sources")
        sources = st.multiselect(
            "Select sources:",
            ["NYT", "Fox", "BBC", "CBS", "ABC"],
            default=["NYT", "Fox", "BBC", "CBS", "ABC"]
        )
        
        # Refresh button
        if st.button("🔄 Refresh Data", type="primary"):
            st.rerun()
    
    # Main content area
    try:
        # Get database connection
        conn = get_db_connection()
        
        if conn is None:
            st.error("❌ Unable to connect to database. Please check your database configuration.")
            return
        
        # Overview metrics
        st.subheader("📊 Overview")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_news = get_news_stats(conn, days_back, sources)
            st.metric("Total Articles", total_news['total_articles'])
        
        with col2:
            st.metric("Unique Stories", total_news['unique_stories'])
        
        with col3:
            st.metric("Sources", total_news['active_sources'])
        
        with col4:
            st.metric("Avg Articles/Day", f"{total_news['avg_per_day']:.1f}")
        
        # Charts section
        st.subheader("📈 Trends & Analytics")
        
        # Source distribution chart
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📺 Articles by Source")
            source_data = get_news_by_source(conn, days_back, sources)
            if not source_data.empty:
                fig = px.pie(source_data, values='count', names='source', 
                           color_discrete_sequence=px.colors.qualitative.Set3)
                fig.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No data available for the selected filters.")
        
        with col2:
            st.subheader("📅 Articles Over Time")
            time_data = get_news_stats(conn, days_back, sources, by_time=True)
            if not time_data.empty:
                fig = px.line(time_data, x='date', y='count', 
                            title='Articles Published Over Time',
                            color_discrete_sequence=['#667eea'])
                fig.update_layout(xaxis_title="Date", yaxis_title="Number of Articles")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No data available for the selected filters.")
        
        # Trending stories section
        st.subheader("🔥 Trending Stories")
        trending_stories = get_trending_stories(conn, days_back, sources, limit=5)
        
        if not trending_stories.empty:
            for _, story in trending_stories.iterrows():
                with st.container():
                    st.markdown(f"""
                    <div class="news-card">
                        <h4>{story['title']}</h4>
                        <p><span class="source-badge">{story['source']}</span> • 
                        {story['article_count']} article{'s' if story['article_count'] > 1 else ''} • 
                        {story['latest_published'].strftime('%Y-%m-%d %H:%M')}</p>
                        <p><strong>Keywords:</strong> {story['keywords'][:100]}{'...' if len(story['keywords']) > 100 else ''}</p>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("No trending stories found for the selected filters.")
        
        # Latest news section
        st.subheader("📰 Latest News")
        
        # Search functionality
        search_term = st.text_input("🔍 Search articles by keyword:", placeholder="Enter keywords to search...")
        
        if search_term:
            search_results = get_news_by_keyword(conn, search_term, days_back, sources)
            news_data = search_results
            st.info(f"Found {len(search_results)} articles matching '{search_term}'")
        else:
            news_data = get_latest_news(conn, days_back, sources, limit=20)
        
        if not news_data.empty:
            for _, article in news_data.iterrows():
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.markdown(f"""
                        <div class="news-card">
                            <h4><a href="{article['link']}" target="_blank">{article['title']}</a></h4>
                            <p><span class="source-badge">{article['source']}</span> • 
                            {article['published'].strftime('%Y-%m-%d %H:%M') if article['published'] else 'No date'}</p>
                            {f'<p>{article["summary"][:200]}{"..." if len(article["summary"]) > 200 else ""}</p>' if article["summary"] else ''}
                            {f'<p><strong>Keywords:</strong> {article["keywords"]}</p>' if article["keywords"] else ''}
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        if article['summary']:
                            with st.expander("📄 Full Summary"):
                                st.write(article['summary'])
        
        conn.close()
        
    except Exception as e:
        st.error(f"❌ An error occurred: {str(e)}")
        st.info("Please check your database connection and try again.")

if __name__ == "__main__":
    main()
