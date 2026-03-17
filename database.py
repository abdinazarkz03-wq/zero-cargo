import sqlite3
import os
from datetime import datetime

DB_PATH = os.getenv("DB_PATH", "zerocargo.db")

class Database:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_tables()

    def _init_tables(self):
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
        """)
        self.conn.commit()

    def _generate_code(self):
        cursor = self.conn.execute("SELECT COUNT(*) as cnt FROM users")
        count = cursor.fetchone()["cnt"]
        return f"ZC-{1000 + count + 1}"

    def register_user(self, telegram_id, full_name, phone):
        code = self._generate_code()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            self.conn.execute(
                "INSERT INTO users (telegram_id, full_name, phone, client_code, created_at) VALUES (?,?,?,?,?)",
                (telegram_id, full_name, phone, code, now)
            )
            self.conn.commit()
            return code
        except sqlite3.IntegrityError:
            return None

    def get_user(self, telegram_id):
        cursor = self.conn.execute("SELECT * FROM users WHERE telegram_id=?", (telegram_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_user_by_code(self, code):
        cursor = self.conn.execute("SELECT * FROM users WHERE client_code=?", (code,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def update_language(self, telegram_id, lang):
        self.conn.execute("UPDATE users SET language=? WHERE telegram_id=?", (lang, telegram_id))
        self.conn.commit()

    def get_all_users(self):
        cursor = self.conn.execute("SELECT * FROM users ORDER BY created_at DESC")
        return [dict(row) for row in cursor.fetchall()]

    def get_parcels_by_code(self, client_code):
        cursor = self.conn.execute(
            "SELECT * FROM parcels WHERE client_code=? ORDER BY created_at DESC", (client_code,)
        )
        return [dict(row) for row in cursor.fetchall()]

    def add_parcel(self, client_code, track_number, description, weight, status="В обработке"):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.conn.execute(
            "INSERT INTO parcels (client_code, track_number, description, weight, status, created_at, updated_at) VALUES (?,?,?,?,?,?,?)",
            (client_code, track_number, description, weight, status, now, now)
        )
        self.conn.commit()

    def update_parcel_status(self, parcel_id, status):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.conn.execute(
            "UPDATE parcels SET status=?, updated_at=? WHERE id=?", (status, now, parcel_id)
        )
        self.conn.commit()

    def delete_parcel(self, parcel_id):
        self.conn.execute("DELETE FROM parcels WHERE id=?", (parcel_id,))
        self.conn.commit()

    def get_all_parcels(self):
        cursor = self.conn.execute("SELECT * FROM parcels ORDER BY created_at DESC")
        return [dict(row) for row in cursor.fetchall()]

    def search_parcel_by_track(self, track_number):
        cursor = self.conn.execute(
            "SELECT * FROM parcels WHERE track_number LIKE ?", (f"%{track_number}%",)
        )
        return [dict(row) for row in cursor.fetchall()]

    def get_stats(self):
        users = self.conn.execute("SELECT COUNT(*) as cnt FROM users").fetchone()["cnt"]
        parcels = self.conn.execute("SELECT COUNT(*) as cnt FROM parcels").fetchone()["cnt"]
        return {"users": users, "parcels": parcels}
