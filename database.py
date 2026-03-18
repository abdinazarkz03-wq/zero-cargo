import sqlite3
import os

class Database:
    def __init__(self):
        # Храним базу в текущей папке проекта
        self.db_path = "zerocargo.db"
        self.create_tables()

    def get_connection(self):
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def create_tables(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
            telegram_id TEXT PRIMARY KEY,
            full_name TEXT,
            phone TEXT,
            client_code TEXT UNIQUE
        )''')
        conn.commit()
        conn.close()

    def create_user(self, tid, name, phone):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT client_code FROM users WHERE telegram_id = ?", (str(tid),))
        res = cursor.fetchone()
        if res:
            code = res['client_code']
        else:
            cursor.execute("SELECT COUNT(*) as cnt FROM users")
            count = cursor.fetchone()['cnt']
            code = f"ZC-{1001 + count}"
            cursor.execute("INSERT INTO users (telegram_id, full_name, phone, client_code) VALUES (?, ?, ?, ?)",
                           (str(tid), name, phone, code))
            conn.commit()
        
        conn.close()
        return code
