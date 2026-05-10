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
            exercise_type   TEXT,
            mood            INTEGER,
            health_score    INTEGER,
            created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            username        TEXT    NOT NULL UNIQUE,
            password_hash   TEXT    NOT NULL,
            nickname        TEXT    DEFAULT '',
            avatar          TEXT    DEFAULT '',
            height          REAL    DEFAULT NULL,
            target_weight   REAL    DEFAULT NULL,
            created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS weight_records (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id         INTEGER NOT NULL,
            date            TEXT    NOT NULL,
            weight          REAL    NOT NULL,
            body_fat        REAL    DEFAULT NULL,
            created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            UNIQUE(user_id, date)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS diet_records (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id         INTEGER NOT NULL,
            date            TEXT    NOT NULL,
            meal_type       TEXT    NOT NULL,
            food_name       TEXT    NOT NULL,
            amount          REAL    DEFAULT 100,
            unit            TEXT    DEFAULT 'g',
            calories        REAL    DEFAULT 0,
            protein         REAL    DEFAULT 0,
            fat             REAL    DEFAULT 0,
            carbs           REAL    DEFAULT 0,
            created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS food_database (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            name            TEXT    NOT NULL UNIQUE,
            calories_per_100g  REAL DEFAULT 0,
            protein_per_100g   REAL DEFAULT 0,
            fat_per_100g       REAL DEFAULT 0,
            carbs_per_100g     REAL DEFAULT 0,
            unit            TEXT    DEFAULT 'g',
            category        TEXT    DEFAULT ''
        )
    """)
    conn.commit()
    conn.close()
