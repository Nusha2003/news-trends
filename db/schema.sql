CREATE TABLE IF NOT EXISTS posts (
    id SERIAL PRIMARY KEY,
    source VARCHAR(50) NOT NULL,
    title TEXT NOT NULL,
    link TEXT UNIQUE NOT NULL,
    published TIMESTAMP NULL,
    summary TEXT
);
