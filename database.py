import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "travel_deals.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS seen_travel_deals (
            deal_id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            source TEXT,
            price TEXT,
            url TEXT,
            discovered_at TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def is_deal_seen(deal_id: str, title: str = None) -> bool:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    if title:
        cursor.execute("SELECT 1 FROM seen_travel_deals WHERE deal_id = ? OR LOWER(TRIM(title)) = LOWER(TRIM(?))", (deal_id, title))
    else:
        cursor.execute("SELECT 1 FROM seen_travel_deals WHERE deal_id = ?", (deal_id,))
    exists = cursor.fetchone() is not None
    conn.close()
    return exists

def save_deal(deal_id: str, title: str, source: str, price: str, url: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT OR IGNORE INTO seen_travel_deals 
            (deal_id, title, source, price, url, discovered_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (deal_id, title, source, price, url, datetime.utcnow()))
        conn.commit()
    finally:
        conn.close()

def get_stats():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM seen_travel_deals")
    count = cursor.fetchone()[0]
    conn.close()
    return {"total_deals": count}

init_db()
