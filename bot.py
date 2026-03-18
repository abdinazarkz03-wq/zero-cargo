import os
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.types import Message, WebAppInfo, ReplyKeyboardMarkup, KeyboardButton
from database import Database

# Загружаем данные из настроек Render
TOKEN = os.getenv("BOT_TOKEN")
WEBAPP_URL = os.getenv("WEBAPP_URL")

bot = Bot(token=TOKEN)
dp = Dispatcher()
db = Database()

def get_keyboard(user_id):
    user = db.get_user(user_id)
    # Кнопки меню
    buttons = [
        [KeyboardButton(text="📦 Мой код"), KeyboardButton(text="🚩 Мои посылки", web_app=WebAppInfo(url=f"{WEBAPP_URL}/parcels"))],
        [KeyboardButton(text="📍 Адреса"), KeyboardButton(text="📖 Инструкция")]
    ]
    # Если не зарегистрирован — добавляем кнопку регистрации
    if not user:
        buttons.insert(0, [KeyboardButton(text="📝 Регистрация", web_app=WebAppInfo(url=f"{WEBAPP_URL}/register"))])
    
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        "🚀 **ZERO CARGO приветствует вас!**\nДля работы используйте меню ниже 👇",
        reply_markup=get_keyboard(message.from_user.id),
        parse_mode="Markdown"
    )

@dp.message(F.text == "📦 Мой код")
async def show_code(message: Message):
    user = db.get_user(message.from_user.id)
    if user:
        await message.answer(f"🆔 Ваш код клиента: `{user['client_code']}`", parse_mode="Markdown")
    else:
        await message.answer("❌ Вы не зарегистрированы. Нажмите «Регистрация» в меню.")

@dp.message(F.text == "📍 Адреса")
async def show_address(message: Message):
    await message.answer("📍 **Адрес склада в Китае:**\nГуанчжоу, р-н Байюнь...")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
