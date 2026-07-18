"""SQLite persistence for analysis history — survives app restarts."""

import sqlite3
import json
from datetime import datetime
from contextlib import contextmanager

DB_PATH = "deallens.db"


@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_name TEXT,
                investor_score INTEGER,
                verdict TEXT,
                model_used TEXT,
                data_json TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)


def save_analysis(data: dict, model_used: str = "openai/gpt-oss-20b") -> int:
    """Saves an analysis result. Returns the new row id."""
    with get_conn() as conn:
        cursor = conn.execute(
            """INSERT INTO analyses (company_name, investor_score, verdict, model_used, data_json, created_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (
                data.get("company_name", "Untitled"),
                data.get("investor_score", 0),
                data.get("verdict", "WATCH"),
                model_used,
                json.dumps(data),
                datetime.now().isoformat(),
            ),
        )
        return cursor.lastrowid


def load_all_analyses() -> list:
    """Returns all saved analyses, most recent last, as list of {id, data, timestamp}."""
    with get_conn() as conn:
        rows = conn.execute("SELECT * FROM analyses ORDER BY id ASC").fetchall()
    result = []
    for row in rows:
        result.append({
            "id": row["id"],
            "data": json.loads(row["data_json"]),
            "timestamp": datetime.fromisoformat(row["created_at"]).strftime("%b %d, %H:%M"),
            "model_used": row["model_used"],
        })
    return result


def delete_analysis(analysis_id: int):
    with get_conn() as conn:
        conn.execute("DELETE FROM analyses WHERE id = ?", (analysis_id,))


def clear_all():
    with get_conn() as conn:
        conn.execute("DELETE FROM analyses")