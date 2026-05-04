import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path("data.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS measurements (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT    NOT NULL,
            topic     TEXT    NOT NULL,
            value     REAL    NOT NULL
        );
        """
    )
    conn.commit()
    conn.close()
    print("[DB] Database ready")


def log_measurement(topic: str, payload: str):
    try:
        value = float(payload)
    except ValueError:
        return
    ts = datetime.utcnow().isoformat(timespec="seconds")
    conn = get_connection()
    conn.execute(
        "INSERT INTO measurements (timestamp, topic, value) VALUES (?, ?, ?)",
        (ts, topic, value),
    )
    conn.commit()
    conn.close()


def get_recent_measurements(topic: str, limit: int = 200):
    conn = get_connection()
    cur = conn.execute(
        """
        SELECT timestamp, value FROM measurements
        WHERE topic = ?
        ORDER BY id DESC LIMIT ?
        """,
        (topic, limit),
    )
    rows = cur.fetchall()
    conn.close()
    return list(reversed(rows))