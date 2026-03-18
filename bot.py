import os
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.types import Message, WebAppInfo, ReplyKeyboardMarkup, KeyboardButton
from database import Database

TOKEN = os.getenv("BOT_TOKEN")
WEBAPP_URL = os.getenv("WEBAPP_URL")

bot = Bot(token=TOKEN)
dp = Dispatcher()
db = Database()

def main_kb(user_id):
    user = db.get_user(user_id)
    kb = [
        [KeyboardButton(text="📦 Мой код"), KeyboardButton(text="🚩 Посылки", web_app=WebAppInfo(url=f"{WEBAPP_URL}/parcels"))],
        [KeyboardButton(text="📍 Адреса"), KeyboardButton(text="👤 Профиль")]
    ]
    if not user:
        kb.insert(0, [KeyboardButton(text="📝 Регистрация", web_app=WebAppInfo(url=f"{WEBAPP_URL}/register"))])
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer("🚀 ZERO CARGO: Используйте меню ниже", reply_markup=main_kb(message.from_user.id))

@dp.message(F.text == "📦 Мой код")
async def code(message: Message):
    user = db.get_user(message.from_user.id)
    if user: await message.answer(f"Ваш код: `{user['client_code']}`", parse_mode="Markdown")
    else: await message.answer("Сначала зарегистрируйтесь!")

@dp.message(F.text == "📍 Адреса")
async def addr(message: Message):
    await message.answer("📍 Склад Китай:\n`广东省佛山市南海区里广路洲村工业区飞机场13-2号`", parse_mode="Markdown")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
