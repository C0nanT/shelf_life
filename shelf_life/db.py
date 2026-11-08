import sqlite3

SCHEMA = """
CREATE TABLE IF NOT EXISTS food (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    normalized_name TEXT NOT NULL UNIQUE,
    unit TEXT NOT NULL,
    warning_milestones TEXT
);
CREATE TABLE IF NOT EXISTS purchase (
    id INTEGER PRIMARY KEY,
    food_id INTEGER NOT NULL REFERENCES food(id),
    quantity TEXT NOT NULL,            -- exact decimal, stored as text
    expiry_date TEXT,                  -- ISO date; last day of month for month precision
    expiry_precision TEXT CHECK (expiry_precision IN ('day', 'month')),
    "group" TEXT NOT NULL CHECK ("group" IN ('Pantry', 'Reserve')),
    recorded_date TEXT NOT NULL,
    last_warned_milestone INTEGER
);
"""


def connect(path):
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(path):
    conn = connect(path)
    with conn:
        conn.executescript(SCHEMA)
    conn.close()
