# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import glob
import os
import sqlite3

# Define the DB path relative to the app directory
DB_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "competitive_intelligence.db"
)
MIGRATIONS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "migrations")


def get_db_connection() -> sqlite3.Connection:
    """Returns a connection to the SQLite database."""
    return sqlite3.connect(DB_PATH)


def run_migrations() -> None:
    """Discovers and runs any unapplied SQL migrations."""
    os.makedirs(MIGRATIONS_DIR, exist_ok=True)

    conn = get_db_connection()
    cursor = conn.cursor()

    # Ensure migrations tracking table exists
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version TEXT PRIMARY KEY,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()

    # Find and sort all SQL files in the migrations directory
    migration_files = sorted(glob.glob(os.path.join(MIGRATIONS_DIR, "*.sql")))

    for file_path in migration_files:
        filename = os.path.basename(file_path)

        # Check if this migration was already applied
        cursor.execute("SELECT 1 FROM schema_migrations WHERE version = ?", (filename,))
        if cursor.fetchone():
            continue

        print(f"Applying database migration: {filename}")
        with open(file_path) as f:
            sql = f.read()

        try:
            cursor.executescript(sql)
            cursor.execute(
                "INSERT INTO schema_migrations (version) VALUES (?)",
                (filename,),
            )
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"Failed to apply migration {filename}: {e}")
            raise e
        finally:
            pass

    conn.close()
