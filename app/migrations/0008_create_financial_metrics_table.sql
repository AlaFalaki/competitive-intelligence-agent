-- Migration: Create company_financials table to store structured financials for the last two years
CREATE TABLE IF NOT EXISTS company_financials (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_name TEXT,
    cik TEXT,
    filing_data_json TEXT, -- JSON containing list of the last two filings with extracted metrics
    anomalies_and_notes TEXT, -- AI-generated summaries and anomalies
    session_id TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(company_name, session_id)
);
