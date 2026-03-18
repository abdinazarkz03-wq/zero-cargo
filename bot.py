import os
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
            f"🆔 Ваш ID: `{user['client_code']}`\n"
            f"📞 Ваш номер: {user['phone']}\n\n"
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
        await message.answer("❌ Сначала пройдите регистрацию, чтобы получить личный код!")
        return
    
    code = user['client_code']
    
    # Формируем адрес по вашему образцу
    address_text = (
        f"📍 **Актуальный адрес склада в Китае:**\n\n"
        f"**收件人 (Получатель):** VXMMM {code}\n"
        f"**电话 (Телефон):** 13545100875\n"
        f"**地址 (Адрес):** 广东省佛山市南海区里广路洲村工业区飞机场13-2号\n"
        f"**（TSL КАРГО）** VXMMM {code}\n\n"
        f"⚠️ **Важно:** Скопируйте данные выше. Ваш личный идентификатор и метка **VXMMM** уже добавлены в нужные поля."
    )
    
    await message.answer(address_text, parse_mode="Markdown")

@dp.message(F.text == "🚩 Мои посылки")
async def my_parcels(message: Message):
    kb = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="🔎 Открыть мои посылки", web_app=WebAppInfo(url=f"{WEBAPP_URL}/parcels"))]
    ])
    await message.answer("📦 Здесь вы можете отслеживать статус своих грузов:", reply_markup=kb)

@dp.message(F.text == "👤 Профиль")
async def show_profile(message: Message):
    user = db.get_user(message.from_user.id)
    if user:
        text = (
            f"👤 **Ваш профиль:**\n\n"
            f"🎫 Код: `{user['client_code']}`\n"
            f"👤 ФИО: {user['full_name']}\n"
            f"📱 Тел: {user['phone']}\n"
            f"🌐 Язык: {user['language']}"
        )
        await message.answer(text, parse_mode="Markdown")

@dp.message(F.text == "🚫 Запрещенные грузы")
async def forbidden(message: Message):
    text = (
        "🚫 **Список запрещенных товаров:**\n\n"
        "❌ Лекарства, витамины, БАДы\n"
        "❌ Жидкости (парфюмерия, масла, лаки)\n"
        "❌ Оружие, ножи, имитация оружия\n"
        "❌ Электронные сигареты и вейпы\n\n"
        "⚠️ **Внимание!** За попытку отправки запрещенных товаров предусмотрен штраф от 10 000 до 50 000 сом!"
    )
    await message.answer(text)

@dp.message(F.text == "💬 Поддержка")
async def support(message: Message):
    kb = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="Написать в WhatsApp", url="https://wa.me/996505600542")],
        [types.InlineKeyboardButton(text="Написать в Telegram", url="https://t.me/твой_ник")]
    ])
    await message.answer("📞 Если у вас возникли вопросы, наш менеджер поможет:", reply_markup=kb)

@dp.message(F.text == "📖 Инструкция")
async def guide(message: Message):
    text = (
        "📖 **Как заказать товар:**\n\n"
        "1. Пройдите регистрацию и получите личный код.\n"
        "2. Укажите наш адрес склада в приложении (Taobao, Pinduoduo и т.д.).\n"
        "3. Обязательно проверьте наличие вашего кода в имени получателя.\n"
        "4. Следите за статусом в разделе 'Мои посылки'."
    )
    await message.answer(text)

@dp.message(F.text == "🌐 Язык")
async def language_choice(message: Message):
    kb = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru"),
         types.InlineKeyboardButton(text="🇰🇬 Кыргызча", callback_data="lang_kg")]
    ])
    await message.answer("Выберите удобный язык / Тилди тандаңыз:", reply_markup=kb)

# --- 4. АДМИН ПАНЕЛЬ ---
@dp.message(Command("admin"))
async def admin_panel(message: Message):
    if str(message.from_user.id) == str(ADMIN_ID):
        kb = types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text="⚙️ Управление посылками", web_app=WebAppInfo(url=f"{WEBAPP_URL}/admin"))]
        ])
        await message.answer("👨‍💻 Вы вошли как администратор:", reply_markup=kb)

# --- 5. СЛУЖЕБНЫЕ ФУНКЦИИ ---
async def set_main_menu(bot: Bot):
    commands = [BotCommand(command="/start", description="Главное меню / Регистрация")]
    await bot.set_my_commands(commands)

def get_bot_instance(): return bot
def get_dispatcher_instance(): return dp
