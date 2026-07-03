-- Migration to create the master_reports table for storing consolidated reports
CREATE TABLE IF NOT EXISTS master_reports (
    session_id TEXT PRIMARY KEY,
    report_json TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
