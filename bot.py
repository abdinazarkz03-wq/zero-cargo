import os
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, WebAppInfo, ReplyKeyboardMarkup, KeyboardButton, BotCommand
from database import Database

TOKEN = os.getenv("BOT_TOKEN")
WEBAPP_URL = os.getenv("WEBAPP_URL")
# Очищаем ID админа от возможных пробелов
ADMIN_ID = str(os.getenv("ADMIN_ID", "")).strip()

bot = Bot(token=TOKEN)
dp = Dispatcher()
db = Database()

# Универсальная клавиатура, которая всегда под рукой
def get_main_keyboard(user_id):
    user = db.get_user(user_id)
    
    # Кнопки, которые видят все
    kb = [
        [KeyboardButton(text="📦 Мой код"), KeyboardButton(text="🚩 Мои посылки")],
        [KeyboardButton(text="📍 Адреса"), KeyboardButton(text="📖 Инструкция")],
        [KeyboardButton(text="👤 Профиль"), KeyboardButton(text="🚫 Запрещенные грузы")]
    ]
    
    # Если пользователь НЕ зарегистрирован, добавляем кнопку регистрации ПЕРВОЙ
    if not user:
        kb.insert(0, [KeyboardButton(text="📝 Регистрация", web_app=WebAppInfo(url=f"{WEBAPP_URL}/register"))])
    
    # Если это админ, добавляем кнопку управления
    if str(user_id) == ADMIN_ID:
        kb.append([KeyboardButton(text="⚙️ Управление посылками", web_app=WebAppInfo(url=f"{WEBAPP_URL}/admin"))])
        
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

@dp.message(CommandStart())
async def start_handler(message: Message):
    user = db.get_user(message.from_user.id)
    if user:
        await message.answer(
            f"🌟 **С возвращением!**\nВаш личный код: `{user['client_code']}`", 
            reply_markup=get_main_keyboard(message.from_user.id), 
            parse_mode="Markdown"
        )
    else:
        await message.answer(
            "🚀 **ZERO CARGO**\n\nДля начала работы, пожалуйста, пройдите регистрацию. Нажмите кнопку ниже 👇", 
            reply_markup=get_main_keyboard(message.from_user.id)
        )

@dp.message(F.text == "📦 Мой код")
async def show_code(message: Message):
    user = db.get_user(message.from_user.id)
    if user: 
        await message.answer(f"🆔 Ваш код: `{user['client_code']}`", parse_mode="Markdown")
    else:
        await message.answer("❌ Вы еще не зарегистрированы! Нажмите кнопку «Регистрация» в меню.")

@dp.message(F.text == "📍 Адреса")
async def show_address(message: Message):
    user = db.get_user(message.from_user.id)
    code = user['client_code'] if user else "ВАШ_КОД"
    address_text = (
        f"📍 **Актуальный адрес склада в Китае:**\n\n"
        f"`广东省佛山市南海区里广路洲村工业区飞机场13-2号 VXMMM {code}`\n\n"
        f"⚠️ **Важно:** Обязательно указывайте ваш код `{code}` в конце имени получателя!"
    )
    await message.answer(address_text, parse_mode="Markdown")

@dp.message(F.text == "🚩 Мои посылки")
async def my_parcels(message: Message):
    parcels = db.get_user_parcels(message.from_user.id)
    if not parcels: 
        return await message.answer("📦 У вас пока нет зарегистрированных посылок.")
    
    res = "🚩 **ВАШИ ПОСЫЛКИ:**\n\n"
    for p in parcels: 
        res += f"🔢 `{p['track_number']}`\n⚖️ {p['weight']} кг | 📍 {p['status']}\n\n"
    await message.answer(res, parse_mode="Markdown")

# Заглушки для остальных кнопок, чтобы бот не молчал
@dp.message(F.text == "📖 Инструкция")
async def info(message: Message):
    await message.answer("📖 Здесь будет инструкция по заказу товаров из Китая.")

@dp.message(F.text == "👤 Профиль")
async def profile(message: Message):
    user = db.get_user(message.from_user.id)
    if user:
        text = f"👤 **Профиль:**\n\nИмя: {user['full_name']}\nТел: {user['phone']}\nКод: {user['client_code']}"
        await message.answer(text)
    else:
        await message.answer("Вы не зарегистрированы.")

@dp.message(F.text == "🚫 Запрещенные грузы")
async def forbidden(message: Message):
    await message.answer("🚫 Список запрещенных грузов: оружие, наркотики, горючие жидкости...")

async def main():
    await bot.set_my_commands([BotCommand(command="/start", description="Запуск")])
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
