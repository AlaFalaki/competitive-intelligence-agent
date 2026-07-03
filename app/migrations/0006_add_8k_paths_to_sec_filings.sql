-- Migration: Add file paths for raw 8-K filings (stored as a JSON array of file paths)
ALTER TABLE sec_filings ADD COLUMN latest_8k_file_paths TEXT;
