import psycopg2
from psycopg2.extras import RealDictCursor
import config

def get_connection():
    """Подключение к базе данных"""
    return psycopg2.connect(config.DATABASE_URL)

def init_db():
    """Создание таблиц при первом запуске"""
    conn = get_connection()
    cur = conn.cursor()
    
    # Таблица пользователей
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            user_id BIGINT UNIQUE NOT NULL,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            created_at TIMESTAMP DEFAULT NOW()
        )
    """)
    
    # Таблица сообщений
    cur.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id SERIAL PRIMARY KEY,
            user_id BIGINT REFERENCES users(user_id) ON DELETE CASCADE,
            message_text TEXT,
            chat_id BIGINT,
            sent_at TIMESTAMP DEFAULT NOW()
        )
    """)
    
    conn.commit()
    cur.close()
    conn.close()
    print("✅ База данных готова")

def add_user(user_id, username, first_name=None, last_name=None):
    """Добавить или обновить пользователя"""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO users (user_id, username, first_name, last_name)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (user_id) 
            DO UPDATE SET 
                username = EXCLUDED.username,
                first_name = EXCLUDED.first_name,
                last_name = EXCLUDED.last_name
        """, (user_id, username, first_name, last_name))
        conn.commit()
        return True
    except Exception as e:
        print(f"❌ Ошибка добавления пользователя: {e}")
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()

def log_message(user_id, message_text, chat_id):
    """Сохранить сообщение в историю"""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO messages (user_id, message_text, chat_id)
            VALUES (%s, %s, %s)
        """, (user_id, message_text, chat_id))
        conn.commit()
    except Exception as e:
        print(f"❌ Ошибка сохранения сообщения: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

def get_user_stats():
    """Получить статистику пользователей"""
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("""
        SELECT 
            COUNT(*) as total_users,
            COUNT(DISTINCT user_id) as unique_users,
            DATE(MIN(created_at)) as first_user_date
        FROM users
    """)
    stats = cur.fetchone()
    cur.close()
    conn.close()
    return stats

# Инициализация при импорте
init_db()
