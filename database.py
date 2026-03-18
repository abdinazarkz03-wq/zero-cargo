import sqlite3

class Database:
    def __init__(self):
        self.db_path = "zerocargo.db"
        self.create_tables()

    def get_connection(self):
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def create_tables(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                telegram_id TEXT PRIMARY KEY,
                full_name TEXT,
                phone TEXT,
                client_code TEXT UNIQUE
            )''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS parcels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id TEXT,
                tracking_number TEXT,
                description TEXT,
                status TEXT DEFAULT 'В обработке',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (telegram_id) REFERENCES users(telegram_id)
            )''')
            conn.commit()

    def get_user(self, tid):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE telegram_id = ?", (str(tid),))
            return cursor.fetchone()

    def create_user(self, tid, name, phone):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT client_code FROM users WHERE telegram_id = ?", (str(tid),))
            res = cursor.fetchone()
            if res:
                return res['client_code']
            cursor.execute("SELECT COUNT(*) as cnt FROM users")
            count = cursor.fetchone()['cnt']
            code = f"ZC-{1001 + count}"
            cursor.execute(
                "INSERT INTO users (telegram_id, full_name, phone, client_code) VALUES (?, ?, ?, ?)",
                (str(tid), name, phone, code)
            )
            conn.commit()
            return code

    def get_parcels(self, tid):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM parcels WHERE telegram_id = ? ORDER BY created_at DESC",
                (str(tid),)
            )
            return cursor.fetchall()

    def add_parcel(self, tid, tracking_number, description):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO parcels (telegram_id, tracking_number, description) VALUES (?, ?, ?)",
                (str(tid), tracking_number, description)
            )
            conn.commit()

    def get_all_users(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users ORDER BY rowid DESC")
            return cursor.fetchall()

    def get_all_parcels(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM parcels ORDER BY created_at DESC")
            return cursor.fetchall()
