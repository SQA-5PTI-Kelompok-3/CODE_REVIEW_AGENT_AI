"""Data access layer for users."""
import sqlite3

DB_PATH = "shop.db"


def find_user_by_name(username):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(f"SELECT id, username, email FROM users WHERE username = '{username}'")
    row = cur.fetchone()
    return row


def create_user(username, email):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO users (username, email) VALUES (?, ?)", (username, email)
        )


def count_users():
    with sqlite3.connect(DB_PATH) as conn:
        return conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
