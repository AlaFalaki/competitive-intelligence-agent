-- Migration: Add session_id to existing tables and create pricing_information table
ALTER TABLE company_profiles ADD COLUMN session_id TEXT;
ALTER TABLE competitors ADD COLUMN session_id TEXT;

CREATE TABLE IF NOT EXISTS pricing_information (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_name TEXT,
    pricing_page_url TEXT,
    raw_page_content TEXT,
    plans_json TEXT, -- Extracted pricing plans and prices in JSON format
    session_id TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(company_name, session_id)
);
