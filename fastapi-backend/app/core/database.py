from contextlib import contextmanager
import sqlite3
import os

DATABASE_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "database")
DB_PATH = os.path.join(DATABASE_DIR, "transport_data.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  
    return conn

@contextmanager
def db_cursor():
    """Context manager to handle open/close of connection and cursor automatically."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    try:
        yield cursor
    finally:
        conn.close()