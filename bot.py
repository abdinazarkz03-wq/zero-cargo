import os
import asyncio
import io
import pandas as pd
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message, WebAppInfo, ReplyKeyboardMarkup, KeyboardButton, BufferedInputFile
from dotenv import load_dotenv
from database import Database

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
WEBAPP_URL = os.getenv("WEBAPP_URL")
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))

if not TOKEN:
    raise ValueError("BOT_TOKEN не задан в .env")
if not WEBAPP_URL:
    raise ValueError("WEBAPP_URL не задан в .env")

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


def admin_kb():
    kb = [
        [KeyboardButton(text="👥 Все пользователи"), KeyboardButton(text="📦 Все посылки")],
        [KeyboardButton(text="📊 Статистика"), KeyboardButton(text="📥 Экспорт Excel")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


def is_admin(message: Message) -> bool:
    return message.from_user.id == ADMIN_ID


@dp.message(CommandStart())
async def start(message: Message):
    if is_admin(message):
        await message.answer("👑 Добро пожаловать, Администратор!", reply_markup=admin_kb())
    else:
        await message.answer(
            "🚀 ZERO CARGO приветствует вас! Используйте меню ниже 👇",
            reply_markup=main_kb(message.from_user.id)
        )


@dp.message(F.text == "📦 Мой код")
async def code(message: Message):
    if is_admin(message):
        return
    user = db.get_user(message.from_user.id)
    if user:
        await message.answer(f"🆔 Ваш код клиента: `{user['client_code']}`", parse_mode="Markdown")
    else:
        await message.answer("❌ Сначала зарегистрируйтесь через кнопку 📝 Регистрация")


@dp.message(F.text == "📍 Адреса")
async def addr(message: Message):
    if is_admin(message):
        return
    await message.answer(
        "📍 *Склад в Китае:*\n`广东省佛山市南海区里广路洲村工业区飞机场13-2号`",
        parse_mode="Markdown"
    )


@dp.message(F.text == "👤 Профиль")
async def profile(message: Message):
    if is_admin(message):
        return
    user = db.get_user(message.from_user.id)
    if user:
        await message.answer(
            f"👤 *Ваш профиль:*\n"
            f"📛 Имя: {user['full_name']}\n"
            f"📞 Телефон: {user['phone']}\n"
            f"🆔 Код клиента: `{user['client_code']}`",
            parse_mode="Markdown"
        )
    else:
        await message.answer("❌ Вы не зарегистрированы. Нажмите 📝 Регистрация")


# ── АДМИН ──────────────────────────────────────────────────

@dp.message(F.text == "👥 Все пользователи")
async def all_users(message: Message):
    if not is_admin(message):
        return
    users = db.get_all_users()
    if not users:
        await message.answer("📭 Пользователей пока нет")
        return
    text = "👥 *Все пользователи:*\n\n"
    for u in users:
        text += f"🆔 `{u['client_code']}` — {u['full_name']} | {u['phone']}\n"
    await message.answer(text, parse_mode="Markdown")


@dp.message(F.text == "📊 Статистика")
async def stats(message: Message):
    if not is_admin(message):
        return
    users = db.get_all_users()
    parcels = db.get_all_parcels()
    await message.answer(
        f"📊 *Статистика ZERO CARGO:*\n\n"
        f"👥 Пользователей: *{len(users)}*\n"
        f"📦 Посылок: *{len(parcels)}*",
        parse_mode="Markdown"
    )


@dp.message(F.text == "📦 Все посылки")
async def all_parcels(message: Message):
    if not is_admin(message):
        return
    parcels = db.get_all_parcels()
    if not parcels:
        await message.answer("📭 Посылок пока нет")
        return
    text = "📦 *Все посылки:*\n\n"
    for p in parcels:
        text += f"`{p['tracking_number']}` — {p['description']} | {p['status']}\n"
    await message.answer(text, parse_mode="Markdown")


@dp.message(F.text == "📥 Экспорт Excel")
async def export_excel(message: Message):
    if not is_admin(message):
        return
    users = db.get_all_users()
    if not users:
        await message.answer("📭 Нет данных для экспорта")
        return
    df = pd.DataFrame([dict(u) for u in users])
    buf = io.BytesIO()
    df.to_excel(buf, index=False)
    buf.seek(0)
    await message.answer_document(
        BufferedInputFile(buf.read(), filename="zerocargo_users.xlsx"),
        caption="📥 Список пользователей"
    )


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
