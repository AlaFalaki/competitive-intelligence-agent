-- Migration: Create sec_filings table
CREATE TABLE IF NOT EXISTS sec_filings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_name TEXT,
    cik TEXT,
    latest_10k_summary TEXT,
    latest_10q_summary TEXT,
    latest_8k_filings TEXT, -- JSON or text list of recent 8-K filings
    anomalies_and_notes TEXT, -- Identified anomalies or noticeable items
    session_id TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(company_name, session_id)
);
