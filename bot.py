import os
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, WebAppInfo, ReplyKeyboardMarkup, KeyboardButton, BotCommand
from database import Database

TOKEN = os.getenv("BOT_TOKEN")
WEBAPP_URL = os.getenv("WEBAPP_URL")
ADMIN_ID = os.getenv("ADMIN_ID")

bot = Bot(token=TOKEN)
dp = Dispatcher()
db = Database()

def get_main_keyboard():
    kb = [
        [KeyboardButton(text="📦 Мой код"), KeyboardButton(text="🚩 Мои посылки")],
        [KeyboardButton(text="📍 Адреса"), KeyboardButton(text="📖 Инструкция")],
        [KeyboardButton(text="👤 Профиль"), KeyboardButton(text="🚫 Запрещенные грузы")],
        [KeyboardButton(text="💬 Поддержка"), KeyboardButton(text="🌐 Язык")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

@dp.message(CommandStart())
async def start_handler(message: Message):
    user = db.get_user(message.from_user.id)
    if user:
        await message.answer(f"🌟 **С возвращением!**\nВаш код: `{user['client_code']}`", reply_markup=get_main_keyboard(), parse_mode="Markdown")
    else:
        reg_kb = types.InlineKeyboardMarkup(inline_keyboard=[[types.InlineKeyboardButton(text="📝 Регистрация", web_app=WebAppInfo(url=f"{WEBAPP_URL}/register"))]])
        await message.answer("🚀 **ZERO CARGO**\nПройдите регистрацию 👇", reply_markup=reg_kb)

@dp.message(F.text == "📦 Мой код")
async def show_code(message: Message):
    user = db.get_user(message.from_user.id)
    if user: await message.answer(f"🆔 Ваш код: `{user['client_code']}`", parse_mode="Markdown")

@dp.message(F.text == "📍 Адреса")
async def show_address(message: Message):
    user = db.get_user(message.from_user.id)
    if user:
        code = user['client_code']
        await message.answer(f"📍 **Склад Китай:**\n`广东省佛山市南海区里广路洲村工业区飞机场13-2号 VXMMM {code}`", parse_mode="Markdown")

@dp.message(F.text == "🚩 Мои посылки")
async def my_parcels(message: Message):
    parcels = db.get_user_parcels(message.from_user.id)
    if not parcels: return await message.answer("📦 Посылок нет.")
    res = "🚩 **ВАШИ ПОСЫЛКИ:**\n\n"
    for p in parcels: res += f"🔢 `{p['track_number']}` | ⚖️ {p['weight']}кг | 📍 {p['status']}\n"
    await message.answer(res, parse_mode="Markdown")

@dp.message(Command("admin"))
async def admin_panel(message: Message):
    if str(message.from_user.id) == str(ADMIN_ID):
        kb = types.InlineKeyboardMarkup(inline_keyboard=[[types.InlineKeyboardButton(text="⚙️ Админка", web_app=WebAppInfo(url=f"{WEBAPP_URL}/admin"))]])
        await message.answer("👨‍💻 Вход в панель:", reply_markup=kb)

async def main():
    await bot.set_my_commands([BotCommand(command="/start", description="Запуск")])
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
