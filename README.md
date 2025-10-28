# 📰 News Trends Dashboard

A real-time news trends dashboard built with Streamlit that analyzes news articles and displays trends, keyword frequencies, and source distributions.

## Features

- 📊 **Real-time News Analysis**: Track trending topics and keywords
- 📈 **Interactive Charts**: Visualize article counts by source and time
- 🔍 **Keyword Frequency**: See what topics are trending
- 📰 **Latest Headlines**: Browse recent news articles
- 🌐 **Cloud Ready**: Deploy easily on Streamlit Cloud

## Demo

The app works in demo mode with sample data when no database is connected. To see real news trends, connect to a PostgreSQL database.

## Local Development

### Prerequisites

- Python 3.8+
- PostgreSQL database (optional for demo mode)

### Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd news-trends
```

2. Install dependencies:
```bash
# For minimal deployment (demo mode only)
pip install -r requirements_minimal.txt

# For full functionality with database support
pip install -r requirements_streamlit.txt
```

3. Set up environment variables (optional):
```bash
# Create a .env file
DB_HOST=localhost
DB_PORT=5432
DB_NAME=newsdb
DB_USER=your_username
DB_PASSWORD=your_password
```

4. Run the application:
```bash
streamlit run dashboard.py
```

## Database Setup

If you want to connect to a real database, you'll need:

1. A PostgreSQL database with the following schema:
```sql
CREATE TABLE IF NOT EXISTS posts (
    id SERIAL PRIMARY KEY,
    source VARCHAR(50) NOT NULL,
    title TEXT NOT NULL,
    link TEXT UNIQUE NOT NULL,
    published TIMESTAMP NULL,
    summary TEXT,
    keywords TEXT
);
```

2. Set the environment variables for your database connection.

## Deployment on Streamlit Cloud

### Option 1: Deploy with Sample Data (No Database Required)

1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click "New app"
4. Connect your GitHub repository
5. Set the main file path to `dashboard.py`
6. Click "Deploy!"

The app will work with sample data and doesn't require any database setup.

### Option 2: Deploy with Real Database

1. Set up a cloud PostgreSQL database (e.g., on Heroku, AWS RDS, or Supabase)
2. Push your code to GitHub
3. Go to [share.streamlit.io](https://share.streamlit.io)
4. Click "New app"
5. Connect your GitHub repository
6. Set the main file path to `dashboard.py`
7. Add your database credentials as secrets in Streamlit Cloud:
   - Go to your app settings
   - Click "Secrets"
   - Add your database environment variables:
   ```
   DB_HOST=your-database-host
   DB_PORT=5432
   DB_NAME=your-database-name
   DB_USER=your-username
   DB_PASSWORD=your-password
   ```
8. Click "Deploy!"

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DB_HOST` | Database host | localhost |
| `DB_PORT` | Database port | 5432 |
| `DB_NAME` | Database name | newsdb |
| `DB_USER` | Database username | anusha |
| `DB_PASSWORD` | Database password | password |

## Project Structure

```
news-trends/
├── dashboard.py              # Main Streamlit application
├── requirements_streamlit.txt # Minimal dependencies for deployment
├── requirements.txt          # Full development dependencies
├── environment.yml          # Conda environment file
├── docker-compose.yml       # Local development setup
├── db/
│   └── schema.sql          # Database schema
└── ingestion/              # News ingestion pipeline
    ├── app.py
    ├── consumer_basic.py
    ├── consumer_postgres.py
    ├── feeds.yaml
    └── rss_producer.py
```

## Troubleshooting

### psycopg2 Import Error

If you encounter a `psycopg2` import error on Streamlit Cloud:

1. **Use the minimal requirements**: Use `requirements_minimal.txt` instead of `requirements_streamlit.txt`
2. **The app will automatically run in demo mode** with sample data
3. **No database connection required** for basic functionality

The app is designed to gracefully handle missing database dependencies and will show sample data instead.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test locally
5. Submit a pull request

## License

This project is open source and available under the MIT License.
