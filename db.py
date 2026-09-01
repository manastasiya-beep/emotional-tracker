import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone

DB_PATH = os.getenv("DB_PATH", "trecker.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    telegram_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    active_start INTEGER NOT NULL DEFAULT 9,
    active_end INTEGER NOT NULL DEFAULT 21,
    paused INTEGER NOT NULL DEFAULT 0,
    last_reminder_at TEXT,
    timezone_name TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER NOT NULL,
    created_at TEXT NOT NULL,
    zone TEXT NOT NULL,
    emotion TEXT NOT NULL,
    focus_tag TEXT,
    FOREIGN KEY (telegram_id) REFERENCES users (telegram_id)
);

CREATE TABLE IF NOT EXISTS daily_reflections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER NOT NULL,
    question_type TEXT NOT NULL,
    answer_text TEXT NOT NULL,
    created_at TEXT NOT NULL,
    expires_at TEXT,
    FOREIGN KEY (telegram_id) REFERENCES users (telegram_id)
);

CREATE TABLE IF NOT EXISTS user_daily_focus (
    telegram_id INTEGER PRIMARY KEY,
    question_type TEXT,
    enabled INTEGER NOT NULL DEFAULT 0,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (telegram_id) REFERENCES users (telegram_id)
);

CREATE TABLE IF NOT EXISTS weekly_rewards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER NOT NULL,
    given_at TEXT NOT NULL,
    dominant_zone TEXT NOT NULL,
    painting_id INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS painting_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER NOT NULL,
    painting_id INTEGER NOT NULL,
    zone TEXT NOT NULL,
    kind TEXT NOT NULL,
    shown_at TEXT NOT NULL,
    FOREIGN KEY (telegram_id) REFERENCES users (telegram_id)
);
"""


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
        conn.executescript(SCHEMA)
        for column in ("last_mosaic_date TEXT", "last_painting_id INTEGER", "timezone_name TEXT"):
            try:
                conn.execute(f"ALTER TABLE users ADD COLUMN {column}")
            except sqlite3.OperationalError:
                pass


def upsert_user(telegram_id, name):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO users (telegram_id, name, created_at) VALUES (?, ?, ?) "
            "ON CONFLICT(telegram_id) DO UPDATE SET name=excluded.name",
            (telegram_id, name, datetime.now(timezone.utc).isoformat()),
        )


def set_active_hours(telegram_id, start, end):
    with get_conn() as conn:
        conn.execute(
            "UPDATE users SET active_start=?, active_end=? WHERE telegram_id=?",
            (start, end, telegram_id),
        )


def get_user(telegram_id):
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM users WHERE telegram_id=?", (telegram_id,)).fetchone()
        return dict(row) if row else None


def set_paused(telegram_id, paused: bool):
    with get_conn() as conn:
        conn.execute("UPDATE users SET paused=? WHERE telegram_id=?", (int(paused), telegram_id))


def all_active_users():
    with get_conn() as conn:
        rows = conn.execute("SELECT * FROM users WHERE paused=0").fetchall()
        return [dict(r) for r in rows]


def update_last_reminder(telegram_id, when_iso):
    with get_conn() as conn:
        conn.execute("UPDATE users SET last_reminder_at=? WHERE telegram_id=?", (when_iso, telegram_id))


def set_timezone_name(telegram_id, timezone_name):
    with get_conn() as conn:
        conn.execute(
            "UPDATE users SET timezone_name=? WHERE telegram_id=?",
            (timezone_name, telegram_id),
        )


def add_entry(telegram_id, zone, emotion, focus_tag=None):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO entries (telegram_id, created_at, zone, emotion, focus_tag) VALUES (?, ?, ?, ?, ?)",
            (telegram_id, datetime.now(timezone.utc).isoformat(), zone, emotion, focus_tag),
        )


def set_daily_focus(telegram_id, question_type=None):
    now_iso = datetime.now(timezone.utc).isoformat()
    enabled = 0 if question_type is None else 1
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO user_daily_focus (telegram_id, question_type, enabled, updated_at) VALUES (?, ?, ?, ?) "
            "ON CONFLICT(telegram_id) DO UPDATE SET question_type=excluded.question_type, enabled=excluded.enabled, updated_at=excluded.updated_at",
            (telegram_id, question_type, enabled, now_iso),
        )


def get_daily_focus(telegram_id):
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM user_daily_focus WHERE telegram_id=?",
            (telegram_id,),
        ).fetchone()
        return dict(row) if row else None


def add_daily_reflection(telegram_id, question_type, answer_text):
    with get_conn() as conn:
        expires_at = (datetime.now(timezone.utc) + timedelta(days=90)).isoformat()
        conn.execute(
            "INSERT INTO daily_reflections (telegram_id, question_type, answer_text, created_at, expires_at) VALUES (?, ?, ?, ?, ?)",
            (telegram_id, question_type, answer_text, datetime.now(timezone.utc).isoformat(), expires_at),
        )


def daily_reflections_since(telegram_id, since_iso):
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM daily_reflections WHERE telegram_id=? AND created_at >= ? ORDER BY created_at",
            (telegram_id, since_iso),
        ).fetchall()
        return [dict(r) for r in rows]


def should_send_daily_painting(telegram_id, today_str):
    with get_conn() as conn:
        row = conn.execute(
            "SELECT last_mosaic_date FROM users WHERE telegram_id=?", (telegram_id,)
        ).fetchone()
        return not row or row["last_mosaic_date"] != today_str


def mark_daily_painting_sent(telegram_id, today_str):
    with get_conn() as conn:
        conn.execute(
            "UPDATE users SET last_mosaic_date=? WHERE telegram_id=?", (today_str, telegram_id)
        )


def set_last_painting(telegram_id, painting_id):
    with get_conn() as conn:
        conn.execute(
            "UPDATE users SET last_painting_id=? WHERE telegram_id=?", (painting_id, telegram_id)
        )


def add_painting_history(telegram_id, painting_id, zone, kind="daily"):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO painting_history (telegram_id, painting_id, zone, kind, shown_at) VALUES (?, ?, ?, ?, ?)",
            (telegram_id, painting_id, zone, kind, datetime.now(timezone.utc).isoformat()),
        )


def painting_history_since(telegram_id, since_iso):
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM painting_history WHERE telegram_id=? AND shown_at >= ? ORDER BY shown_at",
            (telegram_id, since_iso),
        ).fetchall()
        return [dict(row) for row in rows]


def entries_since(telegram_id, since_iso):
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM entries WHERE telegram_id=? AND created_at >= ? ORDER BY created_at",
            (telegram_id, since_iso),
        ).fetchall()
        return [dict(r) for r in rows]


def last_weekly_reward(telegram_id):
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM weekly_rewards WHERE telegram_id=? ORDER BY given_at DESC LIMIT 1",
            (telegram_id,),
        ).fetchone()
        return dict(row) if row else None


def record_weekly_reward(telegram_id, dominant_zone, painting_id):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO weekly_rewards (telegram_id, given_at, dominant_zone, painting_id) VALUES (?, ?, ?, ?)",
            (telegram_id, datetime.now(timezone.utc).isoformat(), dominant_zone, painting_id),
        )
