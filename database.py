import sqlite3
import os
import threading
from datetime import datetime

DB_PATH = os.getenv("DB_PATH", "zerocargo.db")


class Database:
    def __init__(self):
        self.lock = threading.Lock()
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_tables()

    def _init_tables(self):
        with self.lock:
            self.conn.executescript("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    telegram_id INTEGER UNIQUE NOT NULL,
                    full_name TEXT NOT NULL,
                    phone TEXT NOT NULL,
                    client_code TEXT UNIQUE NOT NULL,
                    language TEXT DEFAULT 'ru',
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS parcels (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    client_code TEXT NOT NULL,
                    track_number TEXT NOT NULL,
                    description TEXT,
                    weight REAL,
                    status TEXT DEFAULT 'В обработке',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (client_code) REFERENCES users(client_code)
                );

                CREATE INDEX IF NOT EXISTS idx_users_telegram_id 
                ON users(telegram_id);

                CREATE INDEX IF NOT EXISTS idx_parcels_code 
                ON parcels(client_code);

                CREATE INDEX IF NOT EXISTS idx_parcels_track 
                ON parcels(track_number);
            """)
            self.conn.commit()

    # ✅ Генерация уникального кода
    def _generate_code(self):
        cursor = self.conn.execute("SELECT MAX(id) as max_id FROM users")
        max_id = cursor.fetchone()["max_id"] or 0
        return f"ZC-{1000 + max_id + 1}"

    # ================= USERS =================

    def register_user(self, telegram_id, full_name, phone):
        with self.lock:
            code = self._generate_code()
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            try:
                self.conn.execute(
                    """INSERT INTO users 
                    (telegram_id, full_name, phone, client_code, created_at)
                    VALUES (?,?,?,?,?)""",
                    (telegram_id, full_name, phone, code, now)
                )
                self.conn.commit()
                return code
            except sqlite3.IntegrityError:
                return None

    def get_user(self, telegram_id):
        cursor = self.conn.execute(
            "SELECT * FROM users WHERE telegram_id=?",
            (telegram_id,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_user_by_code(self, code):
        cursor = self.conn.execute(
            "SELECT * FROM users WHERE client_code=?",
            (code,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None

    def update_language(self, telegram_id, lang):
        with self.lock:
            self.conn.execute(
                "UPDATE users SET language=? WHERE telegram_id=?",
                (lang, telegram_id)
            )
            self.conn.commit()

    def get_all_users(self):
        cursor = self.conn.execute(
            "SELECT * FROM users ORDER BY created_at DESC"
        )
        return [
