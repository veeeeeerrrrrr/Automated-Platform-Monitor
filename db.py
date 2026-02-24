import sqlite3
from datetime import datetime


def init_db():
    conn = sqlite3.connect("metrics.db")
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS api_metrics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT,
        status TEXT,
        latency REAL,
        timestamp TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT,
        alert_type TEXT,
        message TEXT,
        timestamp TEXT
    )
    """)

    conn.commit()
    conn.close()


def insert_metric(url, status, latency):
    conn = sqlite3.connect("metrics.db")
    c = conn.cursor()

    c.execute("""
    INSERT INTO api_metrics (url, status, latency, timestamp)
    VALUES (?, ?, ?, ?)
    """, (url, status, latency, datetime.utcnow().isoformat()))

    conn.commit()
    conn.close()


def insert_alert(url, alert_type, message):
    conn = sqlite3.connect("metrics.db")
    c = conn.cursor()

    c.execute("""
    INSERT INTO alerts (url, alert_type, message, timestamp)
    VALUES (?, ?, ?, ?)
    """, (url, alert_type, message, datetime.utcnow().isoformat()))

    conn.commit()
    conn.close()


def fetch_history():
    conn = sqlite3.connect("metrics.db")
    c = conn.cursor()

    c.execute("SELECT url, status, latency, timestamp FROM api_metrics")
    rows = c.fetchall()

    conn.close()
    return rows


def fetch_alerts():
    conn = sqlite3.connect("metrics.db")
    c = conn.cursor()

    c.execute("SELECT url, alert_type, message, timestamp FROM alerts ORDER BY timestamp DESC")
    rows = c.fetchall()

    conn.close()
    return rows