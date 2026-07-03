-- Migration: Add file paths for raw 10-K and 10-Q filings
ALTER TABLE sec_filings ADD COLUMN latest_10k_file_path TEXT;
ALTER TABLE sec_filings ADD COLUMN latest_10q_file_path TEXT;
