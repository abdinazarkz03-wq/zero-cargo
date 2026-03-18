import os
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, WebAppInfo, ReplyKeyboardMarkup, KeyboardButton, BotCommand
from database import Database

# Настройки (подгружаются из переменных окружения Render)
TOKEN = os.getenv("BOT_TOKEN")
WEBAPP_URL = os.getenv("WEBAPP_URL")
ADMIN_ID = os.getenv("ADMIN_ID")

bot = Bot(token=TOKEN)
dp = Dispatcher()
db = Database()

# --- 1. ГЛАВНОЕ МЕНЮ (8 кнопок) ---
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
            f"🌟 **С возвращением, {user['full_name']}!**\n\n"
            f"🆔 Ваш ID: `{user['client_code']}`\n\n"
            "Воспользуйтесь меню ниже для работы с посылками:",
            reply_markup=get_main_keyboard(),
            parse_mode="Markdown"
        )
    else:
        reg_kb = types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text="📝 Регистрация", web_app=WebAppInfo(url=f"{WEBAPP_URL}/register"))]
        ])
        await message.answer(
            "🚀 **Вас приветствует ZERO CARGO!**\n"
            "Доставляем ваши грузы из Китая быстро и надежно.\n\n"
            "Для начала работы, пожалуйста, пройдите регистрацию 👇",
            reply_markup=reg_kb
        )

# --- 3. ОБРАБОТКА КНОПОК МЕНЮ ---

@dp.message(F.text == "📦 Мой код")
async def show_code(message: Message):
    user = db.get_user(message.from_user.id)
    if user:
        await message.answer(f"🆔 Ваш персональный код: `{user['client_code']}`", parse_mode="Markdown")
    else:
        await message.answer("❌ Вы не зарегистрированы.")

@dp.message(F.text == "📍 Адреса")
async def show_address(message: Message):
    user = db.get_user(message.from_user.id)
    if not user:
        await message.answer("❌ Сначала пройдите регистрацию!")
        return
    
    code = user['client_code']
    address_text = (
        f"📍 **Актуальный адрес склада в Китае:**\n\n"
        f"**收件人 (Получатель):** VXMMM {code}\n"
        f"**电话 (Телефон):** 13545100875\n"
        f"**地址 (Адрес):** 广东省佛山市南海区里广路洲村工业区飞机场13-2号\n"
        f"**（TSL КАРГО）** VXMMM {code}\n\n"
        f"Для копирования:\n`广东省佛山市南海区里广路洲村工业区飞机场13-2号 VXMMM {code}`"
    )
    await message.answer(address_text, parse_mode="Markdown")

@dp.message(F.text == "🚩 Мои посылки")
async def my_parcels(message: Message):
    # Показываем список посылок прямо в чате
    parcels = db.get_user_parcels(message.from_user.id)
    if not parcels:
        return await message.answer("📦 У вас пока нет посылок в системе.")
    
    text = "🚩 **Ваши текущие посылки:**\n\n"
    for p in parcels:
        text += f"🔢 `{p['track_number']}`\n⚖️ {p['weight']} кг | 📍 {p['status']}\n───────────────\n"
    await message.answer(text, parse_mode="Markdown")

@dp.message(F.text == "👤 Профиль")
async def show_profile(message: Message):
    user = db.get_user(message.from_user.id)
    if user:
        text = (
            f"👤 **Ваш профиль:**\n\n"
            f"🎫 Код: `{user['client_code']}`\n"
            f"👤 ФИО: {user['full_name']}\n"
            f"📱 Тел: {user['phone']}"
        )
        await message.answer(text, parse_mode="Markdown")

@dp.message(F.text == "🚫 Запрещенные грузы")
async def forbidden(message: Message):
    text = (
        "🚫 **Запрещено к перевозке:**\n\n"
        "❌ Жидкости, порошки, БАДы\n"
        "❌ Оружие, ножи, имитации\n"
        "❌ Электронные сигареты, аккумуляторы\n\n"
        "⚠️ Попытка отправки запрещенного груза ведет к штрафу!"
    )
    await message.answer(text)

@dp.message(F.text == "💬 Поддержка")
async def support(message: Message):
    kb = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="Написать в WhatsApp", url="https://wa.me/996505600542")],
        [types.InlineKeyboardButton(text="Написать в Telegram", url="https://t.me/твой_ник")] # ЗАМЕНИ НА СВОЙ НИК
    ])
    await message.answer("📞 Наш менеджер поможет вам по любым вопросам:", reply_markup=kb)

@dp.message(F.text == "📖 Инструкция")
async def guide(message: Message):
    text = (
        "📖 **Краткая инструкция:**\n\n"
        "1. Скопируйте адрес из раздела '📍 Адреса'.\n"
        "2. Вставьте его в Taobao/Pinduoduo.\n"
        "3. Ждите уведомление от бота о прибытии товара на склад.\n"
        "4. Все данные появятся в разделе 'Мои посылки'."
    )
    await message.answer(text)

@dp.message(Command("admin"))
async def admin_panel(message: Message):
    if str(message.from_user.id) == str(ADMIN_ID):
        kb = types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text="⚙️ Админ-панель (Excel)", web_app=WebAppInfo(url=f"{WEBAPP_URL}/admin"))]
        ])
        await message.answer("👨‍💻 Доступ разрешен:", reply_markup=kb)

# --- 4. ЗАПУСК БОТА ---
async def main():
    await bot.set_my_commands([BotCommand(command="/start", description="Запустить бота")])
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
