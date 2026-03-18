import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from database import Database

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0"))
WEBAPP_URL = os.environ.get("WEBAPP_URL")
WHATSAPP = "996505600542"

db = Database()
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

def main_kb(uid):
    u = db.get_user(uid)
    lang = u.get("language", "ru") if u else "ru"
    if lang == "ru":
        return ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(text="📦 Мой код"), KeyboardButton(text="📮 Мои посылки")],
            [KeyboardButton(text="📍 Адреса"), KeyboardButton(text="📖 Инструкция")],
            [KeyboardButton(text="👤 Профиль"), KeyboardButton(text="🚫 Запрещённые грузы")],
            [KeyboardButton(text="💬 Поддержка"), KeyboardButton(text="🌐 Язык")],
        ], resize_keyboard=True)
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="📦 Менин кодум"), KeyboardButton(text="📮 Менин посылкаларым")],
        [KeyboardButton(text="📍 Даректер"), KeyboardButton(text="📖 Нускама")],
        [KeyboardButton(text="👤 Профиль"), KeyboardButton(text="🚫 Тыюу салынган жүктөр")],
        [KeyboardButton(text="💬 Колдоо"), KeyboardButton(text="🌐 Тил")],
    ], resize_keyboard=True)

def reg_kb():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="📝 Регистрация", web_app=WebAppInfo(url=f"{WEBAPP_URL}/register"))]
    ], resize_keyboard=True)

@dp.message(CommandStart())
async def start(message: types.Message):
    u = db.get_user(message.from_user.id)
    if u:
        await message.answer(f"👋 С возвращением, <b>{u['full_name']}</b>!\n🔑 Код: <b>{u['client_code']}</b>", 
                           parse_mode="HTML", reply_markup=main_kb(message.from_user.id))
    else:
        await message.answer("👋 Добро пожаловать в <b>ZERO CARGO</b> 🚛📦\nНажмите регистрацию:", 
                           parse_mode="HTML", reply_markup=reg_kb())

@dp.message(Command("admin"))
async def admin(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔧 Админ-панель", web_app=WebAppInfo(url=f"{WEBAPP_URL}/admin"))]])
        await message.answer("🔧 Управление карго:", reply_markup=kb)

@dp.message(F.text.in_(["📦 Мой код", "📦 Менин кодум"]))
async def code(message: types.Message):
    u = db.get_user(message.from_user.id)
    if u: await message.answer(f"🔑 Ваш код: <b>{u['client_code']}</b>", parse_mode="HTML")

@dp.message(F.text.in_(["📮 Мои посылки", "📮 Менин посылкаларым"]))
async def parcels(message: types.Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔍 Посылки", web_app=WebAppInfo(url=f"{WEBAPP_URL}/parcels?user_id={message.from_user.id}"))]])
    await message.answer("📦 Ваши грузы:", reply_markup=kb)

@dp.message(F.text.in_(["🌐 Язык", "🌐 Тил"]))
async def lang(message: types.Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇷🇺 Рус", callback_data="lang_ru"), InlineKeyboardButton(text="🇰🇬 Кырг", callback_data="lang_ky")]
    ])
    await message.answer("Выберите язык:", reply_markup=kb)

@dp.callback_query(F.data.startswith("lang_"))
async def set_lang(call: types.CallbackQuery):
    db.update_language(call.from_user.id, call.data.split("_")[1])
    await call.message.answer("✅", reply_markup=main_kb(call.from_user.id))
    await call.answer()

async def bot_start():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
