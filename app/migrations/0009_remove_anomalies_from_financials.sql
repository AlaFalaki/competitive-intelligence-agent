-- Migration: Recreate company_financials table without anomalies_and_notes
DROP TABLE IF EXISTS company_financials;
CREATE TABLE company_financials (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_name TEXT,
    cik TEXT,
    filing_data_json TEXT, -- JSON containing list of the last two filings with extracted metrics
    session_id TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(company_name, session_id)
);
