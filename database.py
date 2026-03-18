import sqlite3
import os

class Database:
    def __init__(self):
        # Используем абсолютный путь, чтобы Render точно видел файл
        db_path = os.getenv("DB_PATH", "zerocargo.db")
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
            telegram_id TEXT PRIMARY KEY,
            full_name TEXT,
            phone TEXT,
            client_code TEXT UNIQUE
        )''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS parcels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_code TEXT,
            track_number TEXT,
            description TEXT,
            status TEXT DEFAULT 'В пути',
            weight REAL DEFAULT 0.0
        )''')
        self.conn.commit()

    def create_user(self, tid, name, phone):
        cursor = self.conn.cursor()
        cursor.execute("SELECT client_code FROM users WHERE telegram_id = ?", (str(tid),))
        res = cursor.fetchone()
        if res:
            return res['client_code']
        
        # Генерация кода: ищем последний ID и прибавляем 1
        cursor.execute("SELECT COUNT(*) as cnt FROM users")
        count = cursor.fetchone()['cnt']
        new_code = f"ZC-{1001 + count}"
        
        cursor.execute("INSERT INTO users (telegram_id, full_name, phone, client_code) VALUES (?, ?, ?, ?)",
                       (str(tid), name, phone, new_code))
        self.conn.commit()
        return new_code

    def get_user_by_code(self, code):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM users WHERE client_code = ?", (code,))
        return cursor.fetchone()

    def add_parcel(self, code, track, desc, weight):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO parcels (client_code, track_number, description, weight) VALUES (?, ?, ?, ?)",
                       (code, track, desc, weight))
        self.conn.commit()
        return True

    def get_user_parcels(self, tid):
        cursor = self.conn.cursor()
        cursor.execute("SELECT client_code FROM users WHERE telegram_id = ?", (str(tid),))
        user = cursor.fetchone()
        if not user: return []
        cursor.execute("SELECT * FROM parcels WHERE client_code = ?", (user['client_code'],))
        return [dict(row) for row in cursor.fetchall()]
