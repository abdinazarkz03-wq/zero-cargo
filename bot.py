import os
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, WebAppInfo, ReplyKeyboardMarkup, KeyboardButton, BotCommand
from database import Database

# Настройки
TOKEN = os.getenv("BOT_TOKEN")
WEBAPP_URL = os.getenv("WEBAPP_URL")
ADMIN_ID = os.getenv("ADMIN_ID")

bot = Bot(token=TOKEN)
dp = Dispatcher()
db = Database()

# --- МЕНЮ (8 КНОПОК) ---
def get_main_keyboard():
    kb = [
        [KeyboardButton(text="📦 Мой код"), KeyboardButton(text="🚩 Мои посылки")],
        [KeyboardButton(text="📍 Адреса"), KeyboardButton(text="📖 Инструкция")],
        [KeyboardButton(text="👤 Профиль"), KeyboardButton(text="🚫 Запрещенные грузы")],
        [KeyboardButton(text="💬 Поддержка"), KeyboardButton(text="🌐 Язык")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

# --- СТАРТ ---
@dp.message(CommandStart())
async def start_handler(message: Message):
    user = db.get_user(message.from_user.id)
    if user:
        await message.answer(
            f"🌟 **С возвращением, {user['full_name']}!**\n\nВаш персональный код: `{user['client_code']}`",
            reply_markup=get_main_keyboard(),
            parse_mode="Markdown"
        )
    else:
        reg_kb = types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text="📝 Регистрация", web_app=WebAppInfo(url=f"{WEBAPP_URL}/register"))]
        ])
        await message.answer("🚀 **Добро пожаловать в ZERO CARGO!**\nДля начала работы пройдите регистрацию 👇", reply_markup=reg_kb)

# --- ОБРАБОТКА КНОПОК ---

@dp.message(F.text == "📦 Мой код")
async def show_code(message: Message):
    user = db.get_user(message.from_user.id)
    if user:
        await message.answer(f"🆔 Ваш персональный код: `{user['client_code']}`", parse_mode="Markdown")

@dp.message(F.text == "📍 Адреса")
async def show_address(message: Message):
    user = db.get_user(message.from_user.id)
    if not user: return await message.answer("Сначала зарегистрируйтесь!")
    
    code = user['client_code']
    text = (
        f"📍 **Адрес склада в Китае (VXMMM):**\n\n"
        f"**收件人:** VXMMM {code}\n"
        f"**电话:** 13545100875\n"
        f"**地址:** 广东省佛山市南海区里广路洲村工业区飞机场13-2号\n"
        f"**（TSL КАРГО）** VXMMM {code}\n\n"
        f"Нажмите, чтобы скопировать:\n`广东省佛山市南海区里广路洲村工业区飞机场13-2号 VXMMM {code}`"
    )
    await message.answer(text, parse_mode="Markdown")

@dp.message(F.text == "🚩 Мои посылки")
async def my_parcels(message: Message):
    parcels = db.get_user_parcels(message.from_user.id)
    if not parcels:
        return await message.answer("📦 У вас пока нет добавленных посылок.")
    
    res = "🚩 **ВАШИ ПОСЫЛКИ:**\n\n"
    for p in parcels:
        res += f"🔢 `{p['track_number']}`\n⚖️ {p['weight']} кг | 📍 {p['status']}\n───────────────\n"
    await message.answer(res, parse_mode="Markdown")

@dp.message(F.text == "👤 Профиль")
async def show_profile(message: Message):
    user = db.get_user(message.from_user.id)
    if user:
        text = (f"👤 **Профиль:**\n\n🎫 Код: `{user['client_code']}`\n👤 ФИО: {user['full_name']}\n📱 Тел: {user['phone']}")
        await message.answer(text, parse_mode="Markdown")

@dp.message(F.text == "🚫 Запрещенные грузы")
async def forbidden(message: Message):
    text = ("🚫 **Запрещено:**\n\n❌ Жидкости, БАДы, Оружие\n❌ Электронные сигареты\n\n⚠️ Штраф за нарушение!")
    await message.answer(text)

@dp.message(F.text == "💬 Поддержка")
async def support(message: Message):
    kb = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="WhatsApp", url="https://wa.me/996505600542")],
        [types.InlineKeyboardButton(text="Telegram", url="https://t.me/твой_ник")]
    ])
    await message.answer("📞 Наш менеджер на связи:", reply_markup=kb)

@dp.message(F.text == "📖 Инструкция")
async def guide(message: Message):
    text = ("📖 **Инструкция:**\n\n1. Скопируйте адрес склада.\n2. Укажите его в приложении.\n3. Ждите уведомления о прибытии.")
    await message.answer(text)

@dp.message(F.text == "🌐 Язык")
async def lang_info(message: Message):
    await message.answer("Бот работает только на русском языке.")

# --- АДМИНКА ---
@dp.message(Command("admin"))
async def admin_panel(message: Message):
    if str(message.from_user.id) == str(ADMIN_ID):
        kb = types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text="⚙️ Управление (Excel)", web_app=WebAppInfo(url=f"{WEBAPP_URL}/admin"))]
        ])
        await message.answer("👨‍💻 Админ-панель:", reply_markup=kb)

# --- ЗАПУСК ---
async def main():
    await bot.set_my_commands([BotCommand(command="/start", description="Запуск")])
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
