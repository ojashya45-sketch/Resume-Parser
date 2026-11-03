import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "resume_parser.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS candidates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                phone TEXT NOT NULL,
                skills TEXT NOT NULL,
                education TEXT NOT NULL,
                experience TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

def add_candidate(data):
    with get_connection() as conn:
        cursor = conn.execute("""
            INSERT INTO candidates
            (filename, name, email, phone, skills, education, experience)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            data["filename"], data["name"], data["email"], data["phone"],
            data["skills"], data["education"], data["experience"]
        ))
        return cursor.lastrowid

def get_candidates(query=""):
    with get_connection() as conn:
        if query:
            pattern = f"%{query}%"
            rows = conn.execute("""
                SELECT * FROM candidates
                WHERE name LIKE ? OR email LIKE ? OR skills LIKE ?
                ORDER BY created_at DESC
            """, (pattern, pattern, pattern)).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM candidates ORDER BY created_at DESC"
            ).fetchall()
        return [dict(row) for row in rows]

def get_candidate(candidate_id):
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM candidates WHERE id = ?", (candidate_id,)
        ).fetchone()
        return dict(row) if row else None

def delete_candidate(candidate_id):
    with get_connection() as conn:
        conn.execute("DELETE FROM candidates WHERE id = ?", (candidate_id,))

def get_dashboard_stats():
    with get_connection() as conn:
        total = conn.execute("SELECT COUNT(*) FROM candidates").fetchone()[0]
        skills = conn.execute(
            "SELECT COUNT(*) FROM candidates WHERE skills != 'Not detected'"
        ).fetchone()[0]
        return {"total": total, "with_skills": skills}
