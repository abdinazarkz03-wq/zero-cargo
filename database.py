import sqlite3
import os
from datetime import datetime

DB_PATH = os.environ.get("DB_PATH", "zerocargo.db")

class Database:
    def __init__(self):
        self.init_db()

    def get_conn(self):
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        conn = self.get_conn()
        cursor = conn.cursor()
        cursor.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER UNIQUE NOT NULL,
                full_name TEXT NOT NULL,
                phone TEXT NOT NULL,
                client_code TEXT UNIQUE NOT NULL,
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS parcels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                client_code TEXT NOT NULL,
                track_number TEXT,
                description TEXT,
                weight REAL,
                status TEXT DEFAULT 'На складе',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            );
        """)
        conn.commit()
        conn.close()

    def get_user(self, telegram_id):
        conn = self.get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    def create_user(self, telegram_id, full_name, phone):
        conn = self.get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as cnt FROM users")
        row = cursor.fetchone()
        count = row["cnt"] if row else 0
        client_code = f"ZC-{1001 + count}"
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            cursor.execute(
                "INSERT INTO users (telegram_id, full_name, phone, client_code, created_at) VALUES (?, ?, ?, ?, ?)",
                (telegram_id, full_name, phone, client_code, now)
            )
            conn.commit()
        except:
            pass
        finally:
            conn.close()
        return client_code

    def get_user_by_code(self, client_code):
        conn = self.get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT telegram_id FROM users WHERE client_code = ?", (client_code,))
        row = cursor.fetchone()
        conn.close()
        return {"telegram_id": row["telegram_id"]} if row else None

    def get_user_parcels(self, telegram_id):
        conn = self.get_conn()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM parcels 
            WHERE user_id = (SELECT id FROM users WHERE telegram_id = ?) 
            ORDER BY created_at DESC
        """, (telegram_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def add_parcel(self, client_code, track_number, description, weight, status="На складе"):
        conn = self.get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE client_code = ?", (client_code,))
        user = cursor.fetchone()
        if not user:
            conn.close()
            return False
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            "INSERT INTO parcels (user_id, client_code, track_number, description, weight, status, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (user["id"], client_code, track_number, description, weight, status, now, now)
        )
        conn.commit()
        conn.close()
        return True
