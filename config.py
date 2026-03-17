import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
DATABASE_URL = os.getenv('DATABASE_URL')

if not BOT_TOKEN:
    raise ValueError("Нет BOT_TOKEN в переменных окружения!")
if not DATABASE_URL:
    raise ValueError("Нет DATABASE_URL в переменных окружения!")
