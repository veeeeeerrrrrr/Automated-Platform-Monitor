import sqlite3

def init_db():
    conn = sqlite3.connect("metrics.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS api_metrics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT,
        status TEXT,
        latency REAL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()

def insert_metric(url, status, latency):
    conn = sqlite3.connect("metrics.db")
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO api_metrics (url, status, latency)
    VALUES (?, ?, ?)
    """, (url, status, latency))

    conn.commit()
    conn.close()

def calculate_uptime(url):
    conn = sqlite3.connect("metrics.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT COUNT(*) FROM api_metrics WHERE url=? AND status='UP'
    """, (url,))
    up = cursor.fetchone()[0]

    cursor.execute("""
    SELECT COUNT(*) FROM api_metrics WHERE url=?
    """, (url,))
    total = cursor.fetchone()[0]

    conn.close()

    if total == 0:
        return 0
    return round((up / total) * 100, 2)   