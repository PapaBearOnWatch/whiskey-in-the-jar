import sqlite3
from contextlib import contextmanager
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATABASE_PATH = PROJECT_ROOT / "whiskey.db"

_active_database_path = DATABASE_PATH


def set_database_path(path):
    global _active_database_path
    _active_database_path = Path(path)


@contextmanager
def get_connection():
    connection = sqlite3.connect(_active_database_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")

    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def initialize_database():
    with get_connection() as connection:

        connection.executescript("""
            CREATE TABLE IF NOT EXISTS emails (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id TEXT,
                sender TEXT,
                recipient TEXT,
                subject TEXT,
                received_at TEXT,
                raw_email BLOB NOT NULL,
                sha256 TEXT NOT NULL UNIQUE,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS indicators (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email_id INTEGER NOT NULL,
                indicator_type TEXT NOT NULL,
                indicator_value TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (email_id)
                    REFERENCES emails(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS analysis_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email_id INTEGER NOT NULL,
                risk_level TEXT,
                findings TEXT,
                analyzed_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (email_id)
                    REFERENCES emails(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS campaigns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                campaign_name TEXT NOT NULL,
                description TEXT,
                first_seen TEXT,
                last_seen TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS campaign_emails (
                campaign_id INTEGER NOT NULL,
                email_id INTEGER NOT NULL,
                PRIMARY KEY (campaign_id, email_id),
                FOREIGN KEY (campaign_id)
                    REFERENCES campaigns(id) ON DELETE CASCADE,
                FOREIGN KEY (email_id)
                    REFERENCES emails(id) ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS idx_emails_sender
                ON emails(sender);

            CREATE INDEX IF NOT EXISTS idx_indicators_value
                ON indicators(indicator_value);

            CREATE INDEX IF NOT EXISTS idx_analysis_email
                ON analysis_results(email_id);
        """)

    print("Whiskey in the Jar database initialized.")
    print(f"Database location: {_active_database_path}")


if __name__ == "__main__":
    initialize_database()
