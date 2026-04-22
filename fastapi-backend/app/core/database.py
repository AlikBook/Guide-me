from contextlib import contextmanager
import sqlite3
import os


DEFAULT_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "database", "transport_data.db")
DB_PATH = os.getenv("DATABASE_PATH", DEFAULT_PATH)

def get_db_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  
    return conn

@contextmanager
def db_cursor():
    """Context manager to handle open/close of connection and cursor automatically."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        yield cursor
    finally:
        conn.close()