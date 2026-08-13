import os
import sqlite3
import pandas as pd
from typing import List, Dict, Any, Optional
from database.models import ALL_TABLE_STATEMENTS

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "sales_forecasting.db")

def get_db_connection():
    """Establish connection to SQLite database with high-performance WAL and memory pragmas."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA synchronous = NORMAL;")
    conn.execute("PRAGMA temp_store = MEMORY;")
    return conn

def init_db():
    """Initialize database tables using schema statements in models.py."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        for statement in ALL_TABLE_STATEMENTS:
            cursor.execute(statement)
        conn.commit()
    finally:
        conn.close()

def query_db(query: str, params: tuple = ()) -> List[Dict[str, Any]]:
    """Execute SQL query and return results as list of dictionaries."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()

def query_db_one(query: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
    """Execute SQL query and return single dictionary result or None."""
    results = query_db(query, params)
    return results[0] if results else None

def query_df(query: str, params: tuple = ()) -> pd.DataFrame:
    """Execute SQL query and return Pandas DataFrame."""
    conn = get_db_connection()
    try:
        return pd.read_sql_query(query, conn, params=params)
    finally:
        conn.close()

def execute_db(query: str, params: tuple = ()) -> int:
    """Execute INSERT/UPDATE/DELETE statement with parameters."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        return cursor.lastrowid
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def execute_many_db(query: str, params_list: List[tuple]) -> int:
    """Execute batch INSERT/UPDATE/DELETE statement with parameters list."""
    if not params_list:
        return 0
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.executemany(query, params_list)
        conn.commit()
        return cursor.rowcount
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def log_audit_event(username: str, action: str, details: str = "", user_id: Optional[int] = None) -> int:
    """Log audit event to SQLite audit_logs table."""
    sql = "INSERT INTO audit_logs (user_id, username, action, details) VALUES (?, ?, ?, ?);"
    return execute_db(sql, (user_id, username, action, details))
