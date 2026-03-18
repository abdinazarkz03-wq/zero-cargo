import os
import json
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, WebAppInfo, ReplyKeyboardMarkup, KeyboardButton, BotCommand
from database import Database

# Данные из настроек Render
TOKEN = os.getenv("BOT_TOKEN")
WEBAPP_URL = os.getenv("WEBAPP_URL")
ADMIN_ID = os.getenv("ADMIN_ID")

bot = Bot(token=TOKEN)
dp = Dispatcher()
db = Database()

# --- 1. ГЛАВНОЕ МЕНЮ (Кнопки внизу экрана) ---
def get_main_keyboard():
    kb = [
        [KeyboardButton(text="📦 Мой код"), KeyboardButton(text="🚩 Мои посылки")],
        [KeyboardButton(text="📍 Адреса"), KeyboardButton(text="📖 Инструкция")],
        [KeyboardButton(text="👤 Профиль"), KeyboardButton(text="🚫 Запрещенные грузы")],
        [KeyboardButton(text="💬 Поддержка"), KeyboardButton(text="🌐 Язык")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

# --- 2. КОМАНДА /START ---
@dp.message(CommandStart())
async def start_handler(message: Message):
    user = db.get_user(message.from_user.id)
    if user:
        await message.answer(
            f"👋 **Добро пожаловать в ZERO CARGO, {user['full_name']}!**\n\n"
            f"Ваш персональный код: `{user['client_code']}`\n"
            "Используйте меню ниже для работы с грузами.",
            reply_markup=get_main_keyboard(),
            parse_mode="Markdown"
        )
    else:
        # Кнопка регистрации для новых клиентов
        reg_kb = types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text="📝 Пройти регистрацию", web_app=WebAppInfo(url=f"{WEBAPP_URL}/register"))]
        ])
        await message.answer(
            "🚀 **Вас приветствует ZERO CARGO 312!**\n"
            "_________________________________\n\n"
            "Чтобы получить личный код и адрес склада в Китае, пожалуйста, зарегистрируйтесь 👇",
            reply_markup=reg_kb,
            parse_mode="Markdown"
        )

# --- 3. ОБРАБОТКА КНОПОК МЕНЮ ---

@dp.message(F.text == "📦 Мой код")
async def show_my_code(message: Message):
    user = db.get_user(message.from_user.id)
    if user:
        await message.answer(f"📦 **Ваш код клиента:**\n\n`{user['client_code']}`", parse_mode="Markdown")

@dp.message(F.text == "📍 Адреса")
async def show_address(message: Message):
    user = db.get_user(message.from_user.id)
    code = user['client_code'] if user else "VXMMM" # Если не зарегистрирован, даем общий код
    
    address_text = (
        f"📍 **Актуальный адрес склада в Китае:**\n\n"
        f"**收件人:** VXMMM {code}\n"
        f"**电话:** 13545100875\n"
        f"**地址:** 广东省佛山市南海区里广路洲村工业区飞机场13-2号\n"
        f"**（TSL КАРГО）** {code}\n\n"
        f"⚠️ **Внимание:** Обязательно добавляйте `{code}` к имени получателя!"
    )
    await message.answer(address_text, parse_mode="Markdown")

@dp.message(F.text == "🚩 Мои посылки")
async def view_parcels(message: Message):
    # Открываем мини-приложение со списком посылок
    url = f"{WEBAPP_URL}/parcels?user_id={message.from_user.id}"
    kb = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="🔎 Посмотреть мои грузы", web_app=WebAppInfo(url=url))]
    ])
    await message.answer("Нажмите на кнопку ниже, чтобы проверить статус ваших посылок:", reply_markup=kb)

@dp.message(F.text == "👤 Профиль")
async def view_profile(message: Message):
    user = db.get_user(message.from_user.id)
    if user:
        text = (
            f"👤 **Ваш профиль:**\n\n"
            f"🎫 Код: `{user['client_code']}`\n"
            f"👤 ФИО: {user['full_name']}\n"
            f"📞 Тел: {user['phone']}\n"
            f"🌐 Язык: {user['language']}"
        )
        await message.answer(text, parse_mode="Markdown")

@dp.message(F.text == "📖 Инструкция")
async def show_help(message: Message):
    text = (
        "📖 **Краткая инструкция:**\n\n"
        "1. Скопируйте адрес из раздела '📍 Адреса'.\n"
        "2. Вставьте его в приложении Taobao/Pinduoduo.\n"
        "3. В поле 'Имя' обязательно укажите ваш код.\n"
        "4. Как только посылка придет на склад, она появится в '🚩 Мои посылки'."
    )
    await message.answer(text, parse_mode="Markdown")

@dp.message(F.text == "🚫 Запрещенные грузы")
async def forbidden_items(message: Message):
    text = (
        "🚫 **Что нельзя отправлять:**\n\n"
        "• Оружие, ножи, газовые баллончики.\n"
        "• Наркотики и психотропные вещества.\n"
        "• Легковоспламеняющиеся жидкости (духи, лаки).\n"
        "• Аккумуляторы и повербанки (уточнять).\n"
        "• Животные и растения."
    )
    await message.answer(text)

@dp.message(F.text == "💬 Поддержка")
async def contact_support(message: Message):
    kb = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="Написать менеджеру", url="https://wa.me/996505600542")]
    ])
    await message.answer("📞 По всем вопросам обращайтесь в службу поддержки:", reply_markup=kb)

# --- 4. АДМИН-ПАНЕЛЬ ---
@dp.message(Command("admin"))
async def admin_command(message: Message):
    if str(message.from_user.id) == str(ADMIN_ID):
        kb = types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text="⚙️ Открыть Админку", web_app=WebAppInfo(url=f"{WEBAPP_URL}/admin"))]
        ])
        await message.answer("👨‍💻 **Вы зашли как администратор.**\nИспользуйте кнопку ниже для добавления посылок:", reply_markup=kb)

# --- 5. УСТАНОВКА МЕНЮ КОМАНД ---
async def set_main_menu(bot: Bot):
    commands = [
        BotCommand(command="/start", description="Запустить бота"),
        BotCommand(command="/admin", description="Панель администратора")
    ]
    await bot.set_my_commands(commands)

def get_bot_instance(): return bot
def get_dispatcher_instance(): return dp
