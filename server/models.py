import sqlite3
from datetime import datetime

DB_PATH = 'health_records.db'


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS health_records (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            date            TEXT    NOT NULL UNIQUE,
            steps           INTEGER,
            heart_rate      INTEGER,
            hr_min          INTEGER,
            hr_avg          INTEGER,
            hr_max          INTEGER,
            sleep           REAL,
            water           INTEGER,
            exercise        INTEGER,
            mood            INTEGER,
            health_score    INTEGER,
            created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()
