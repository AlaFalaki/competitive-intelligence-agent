-- Migration: Create company_news table
CREATE TABLE IF NOT EXISTS company_news (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_name TEXT,
    news_summary TEXT, -- AI-generated summaries of recent news
    session_id TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(company_name, session_id)
);
