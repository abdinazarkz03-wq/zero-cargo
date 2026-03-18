import os
import json
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, WebAppInfo
from database import Database  # Подключаем класс

# Данные из Render
TOKEN = os.getenv("BOT_TOKEN")
WEBAPP_URL = os.getenv("WEBAPP_URL")
ADMIN_ID = os.getenv("ADMIN_ID")

bot = Bot(token=TOKEN)
dp = Dispatcher()
db = Database() # Создаем связь с базой

def get_main_keyboard():
    # Важно: ссылка должна вести на /register
    url = f"{WEBAPP_URL}/register" if not WEBAPP_URL.endswith('/register') else WEBAPP_URL
    kb = [[types.InlineKeyboardButton(text="📝 Регистрация", web_app=WebAppInfo(url=url))]]
    return types.InlineKeyboardMarkup(inline_keyboard=kb)

@dp.message(CommandStart())
async def command_start_handler(message: Message):
    user = db.get_user(message.from_user.id)
    if user:
        await message.answer(
            f"🌟 **С возвращением, {user['full_name']}!**\n\n"
            f"🆔 Ваш ID: `{user['client_code']}`\n"
            f"📞 Ваш номер: `{user['phone']}`\n\n"
            "Вы можете проверить статус посылок в меню.",
            parse_mode="Markdown"
        )
    else:
        await message.answer(
            "🚀 **ZERO CARGO 312** 🚚\n"
            "_________________________________\n\n"
            "Доставляем грузы из Китая быстро и надежно!\n\n"
            "💎 **Тарифы:** 2.5$ — 2.8$ за кг\n"
            "⏱ **Сроки:** 7–12 дней\n"
            "📍 **Адрес:** ж/м Рухий Мурас\n"
            "_________________________________\n\n"
            "Пожалуйста, пройдите регистрацию 👇",
            reply_markup=get_main_keyboard(),
            parse_mode="Markdown"
        )

@dp.message(Command("users"))
async def show_users(message: Message):
    if str(message.from_user.id) == str(ADMIN_ID):
        users = db.get_all_users()
        if not users:
            await message.answer("Список пользователей пока пуст.")
            return
        text = "👥 **Список клиентов:**\n\n"
        for u in users:
            text += f"👤 {u['full_name']} | 📞 {u['phone']} | ID: `{u['client_code']}`\n"
        await message.answer(text, parse_mode="Markdown")

# Этот блок теперь просто ловит уведомление, а саму запись делает WebApp
@dp.message(F.content_type == "web_app_data")
async def web_app_data_handler(message: Message):
    await message.answer("✅ Данные получены! Проверяем...")

def get_bot_instance(): return bot
def get_dispatcher_instance(): return dp
