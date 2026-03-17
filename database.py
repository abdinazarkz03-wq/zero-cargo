import sqlite3
import random
import string
from datetime import datetime
import threading
import logging

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_path="zerocargo.db"):
        self.db_path = db_path
        self.lock = threading.Lock()
        self.init_db()
    
    def init_db(self):
        """Создание таблиц, если их нет"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    telegram_id INTEGER UNIQUE NOT NULL,
                    client_code TEXT UNIQUE NOT NULL,
                    full_name TEXT NOT NULL,
                    phone TEXT NOT NULL,
                    username TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    last_active TEXT,
                    is_active INTEGER DEFAULT 1
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS parcels (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    client_code TEXT NOT NULL,
                    track_number TEXT UNIQUE NOT NULL,
                    description TEXT,
                    weight REAL,
                    status TEXT DEFAULT 'В пути',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    estimated_delivery TEXT,
                    notes TEXT,
                    FOREIGN KEY (client_code) REFERENCES users(client_code)
                )
            ''')
            
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_telegram_id ON users(telegram_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_client_code ON users(client_code)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_parcels_client_code ON parcels(client_code)')
            
            conn.commit()
            conn.close()
    
    def _generate_client_code(self):
        """Генерация уникального кода клиента"""
        while True:
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            if not self.get_user_by_code(code):
                return code
    
    def get_user(self, telegram_id):
        """Получить пользователя по telegram_id"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM users WHERE telegram_id = ?",
                (telegram_id,)
            )
            row = cursor.fetchone()
            conn.close()
            return dict(row) if row else None
    
    def get_user_by_code(self, client_code):
        """Получить пользователя по client_code"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM users WHERE client_code = ?",
                (client_code,)
            )
            row = cursor.fetchone()
            conn.close()
            return dict(row) if row else None
    
    def register_user(self, telegram_id, full_name, phone, username=None):
        """Регистрация нового пользователя"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            
            existing = conn.execute(
                "SELECT client_code FROM users WHERE telegram_id = ?",
                (telegram_id,)
            ).fetchone()
            if existing:
                conn.close()
                return existing['client_code']
            
            client_code = self._generate_client_code()
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            conn.execute('''
                INSERT INTO users 
                (telegram_id, client_code, full_name, phone, username, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (telegram_id, client_code, full_name, phone, username, now, now))
            
            conn.commit()
            conn.close()
            return client_code
    
    def get_parcels(self, client_code):
        """Получить все посылки клиента"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM parcels WHERE client_code = ? ORDER BY created_at DESC",
                (client_code,)
            )
            rows = cursor.fetchall()
            conn.close()
            return [dict(row) for row in rows]
    
    def add_parcel(self, client_code, track_number, description="", weight=None, status="В обработке", estimated_delivery=None):
        """Добавить новую посылку"""
        with self.lock:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            conn = sqlite3.connect(self.db_path)
            try:
                conn.execute('''
                    INSERT INTO parcels 
                    (client_code, track_number, description, weight, status, created_at, updated_at, estimated_delivery)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (client_code, track_number, description, weight, status, now, now, estimated_delivery))
                conn.commit()
            except sqlite3.IntegrityError:
                # Трек-номер уже существует
                pass
            finally:
                conn.close()
    
    def update_parcel_status(self, track_number, status):
        """Обновить статус посылки"""
        with self.lock:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            conn = sqlite3.connect(self.db_path)
            conn.execute('''
                UPDATE parcels 
                SET status = ?, updated_at = ?
                WHERE track_number = ?
            ''', (status, now, track_number))
            conn.commit()
            conn.close()
    
    def get_all_users(self):
        """Получить всех пользователей (для админа)"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM users ORDER BY created_at DESC"
            )
            rows = cursor.fetchall()
            conn.close()
            return [dict(row) for row in rows]
