import sqlite3
import threading
from datetime import date

conn = sqlite3.connect("tasks.db", check_same_thread=False)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()
_db_lock = threading.Lock()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    timezone TEXT DEFAULT 'Europe/Moscow'
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    text TEXT,
    task_date TEXT,
    remind_time TEXT,
    completed INTEGER DEFAULT 0,
    edited_at TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS digest_settings (
    user_id INTEGER,
    time TEXT
)
""")

conn.commit()

def add_user(user_id: int):
    with _db_lock:
        cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
        conn.commit()

def set_user_timezone(user_id, tz):
    with _db_lock:
        cursor.execute("UPDATE users SET timezone=? WHERE user_id=?", (tz, user_id))
        conn.commit()

def get_user_timezone(user_id):
    with _db_lock:
        cursor.execute("SELECT timezone FROM users WHERE user_id=?", (user_id,))
        r = cursor.fetchone()
        return r["timezone"] if r else None

def set_digest_times(user_id, times):
    with _db_lock:
        cursor.execute("DELETE FROM digest_settings WHERE user_id=?", (user_id,))
        cursor.executemany(
            "INSERT INTO digest_settings VALUES (?, ?)",
            [(user_id, t) for t in times]
        )
        conn.commit()

def get_user_digest_times(user_id):
    with _db_lock:
        cursor.execute("SELECT time FROM digest_settings WHERE user_id=? ORDER BY time", (user_id,))
        return [r["time"] for r in cursor.fetchall()]

def get_all_users_with_timezone():
    with _db_lock:
        cursor.execute("SELECT user_id, timezone FROM users")
        return cursor.fetchall()

def get_today_tasks_texts(user_id, today_iso):
    with _db_lock:
        cursor.execute("""
            SELECT text FROM tasks
            WHERE user_id=? AND task_date=? AND completed=0
        """, (user_id, today_iso))
        return [r["text"] for r in cursor.fetchall()]

def is_digest_time_for_user(user_id, time_str):
    with _db_lock:
        cursor.execute(
            "SELECT 1 FROM digest_settings WHERE user_id=? AND time=?",
            (user_id, time_str)
        )
        return cursor.fetchone() is not None


def get_tasks_for_reminder(user_id, today_iso, time_str):
    """Задачи на указанную дату с напоминанием в указанное время (не выполнены)."""
    with _db_lock:
        cursor.execute("""
            SELECT id, text, task_date, remind_time FROM tasks
            WHERE user_id=? AND task_date=? AND remind_time=? AND completed=0
        """, (user_id, today_iso, time_str))
        return cursor.fetchall()

def add_task(user_id, text, task_date, remind_time):
    with _db_lock:
        cursor.execute("""
            INSERT INTO tasks (user_id, text, task_date, remind_time)
            VALUES (?, ?, ?, ?)
        """, (user_id, text, task_date, remind_time))
        conn.commit()

def get_tasks(user_id):
    with _db_lock:
        cursor.execute("SELECT * FROM tasks WHERE user_id=? ORDER BY task_date", (user_id,))
        return cursor.fetchall()

def get_today_tasks_full(user_id, today_iso):
    """today_iso — дата «сегодня» в таймзоне пользователя (YYYY-MM-DD)."""
    with _db_lock:
        cursor.execute("SELECT * FROM tasks WHERE user_id=? AND task_date=?", (user_id, today_iso))
        return cursor.fetchall()

def get_task_by_id(user_id, task_id):
    with _db_lock:
        cursor.execute("SELECT * FROM tasks WHERE id=? AND user_id=?", (task_id, user_id))
        return cursor.fetchone()

def update_task(user_id, task_id, text, task_date, remind_time):
    with _db_lock:
        cursor.execute("""
            UPDATE tasks SET text=?, task_date=?, remind_time=?, edited_at=datetime('now')
            WHERE id=? AND user_id=?
        """, (text, task_date, remind_time, task_id, user_id))
        conn.commit()

def complete_task(user_id, task_id):
    with _db_lock:
        cursor.execute("UPDATE tasks SET completed=1 WHERE id=? AND user_id=?", (task_id, user_id))
        conn.commit()

def delete_task(user_id, task_id):
    with _db_lock:
        cursor.execute("DELETE FROM tasks WHERE id=? AND user_id=?", (task_id, user_id))
        conn.commit()
