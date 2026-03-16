import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN', 'ВАШ_ТОКЕН_ЗДЕСЬ')
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:password@localhost:5432/zero_cargo')
ADMIN_IDS = [int(id.strip()) for id in os.getenv('ADMIN_IDS', '').split(',') if id.strip()]

# Данные компании
COMPANY_NAME = "ZERO CARGO"
COMPANY_PHONE = "0505600542"
COMPANY_PHONE_FULL = "+996505600542"
COMPANY_INSTAGRAM = "@zero_cargo.312"
COMPANY_INSTAGRAM_LINK = "https://instagram.com/zero_cargo.312"
COMPANY_WHATSAPP_LINK = "https://wa.me/996505600542"

# ПВЗ
PICKUP_ADDRESS = "ж/м Рухий Мурас, Бишкек"
PICKUP_PHONE = "0505600542"
PICKUP_HOURS = "пн-сб 11:00-20:00"
PICKUP_MAP_LINK = "https://2gis.kg/bishkek/search/Рухий%20Мурас"

# Китайский склад
CHINA_PHONE_NUMBER = "13545100875"
CHINA_ADDRESS = "广东省佛山市南海区里广路洲村工业区飞机场13-2号"
CHINA_CLIENT_CODE = "VXMMM"

# Цены и сроки
PRICE_PER_KG = "2.8$"
DELIVERY_TIME = "7-14 дней"
