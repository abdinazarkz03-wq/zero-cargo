import logging
import os
import requests
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    WebAppInfo,
    ReplyKeyboardMarkup,
    KeyboardButton
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    CallbackQueryHandler
)

# ================= НАСТРОЙКИ =================

TOKEN = os.getenv("BOT_TOKEN")  # ❗ вставь токен через ENV
WEBAPP_URL = os.getenv("WEBAPP_URL", "https://zerocargo-webapp.onrender.com")

# ================= ЛОГИ =================

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ================= API =================

def get_user(telegram_id):
    try:
        r = requests.get(
            f"{WEBAPP_URL}/api/user?telegram_id={telegram_id}",
            timeout=5
        )
        data = r.json()
        return data if data.get("found") else None
    except Exception as e:
        logger.error(f"API error: {e}")
        return None

# ================= КНОПКИ =================

def main_keyboard(registered=False):
    if not registered:
        return ReplyKeyboardMarkup(
            [[KeyboardButton("📝 Регистрация")]],
            resize_keyboard=True
        )

    return ReplyKeyboardMarkup([
        [KeyboardButton("📦 Мой код"), KeyboardButton("🚨 Мои посылки")],
        [KeyboardButton("📍 Адреса"), KeyboardButton("📖 Инструкция")],
    ], resize_keyboard=True)

# ================= КОМАНДА START =================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = get_user(user_id)

    if user:
        text = f"👋 Добро пожаловать, {user['full_name']}!\n\n🔑 Код: {user['client_code']}"
        await update.message.reply_text(text, reply_markup=main_keyboard(True))
    else:
        text = "🚛 Добро пожаловать в ZERO CARGO!\n\nНажмите «Регистрация»"
        await update.message.reply_text(text, reply_markup=main_keyboard(False))

# ================= ОБРАБОТКА =================

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id
    user = get_user(user_id)

    # регистрация
    if text == "📝 Регистрация":
        url = f"{WEBAPP_URL}/register?user_id={user_id}"
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("Открыть регистрацию", web_app=WebAppInfo(url=url))]
        ])
        await update.message.reply_text("Нажмите кнопку:", reply_markup=kb)
        return

    # код
    if text == "📦 Мой код":
        if not user:
            await update.message.reply_text("Сначала зарегистрируйтесь")
            return

        await update.message.reply_text(
            f"🔑 Код: {user['client_code']}\n👤 {user['full_name']}\n📱 {user['phone']}"
        )

    # посылки
    elif text == "🚨 Мои посылки":
        if not user:
            await update.message.reply_text("Сначала зарегистрируйтесь")
            return

        url = f"{WEBAPP_URL}/parcels?code={user['client_code']}"
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("Открыть посылки", web_app=WebAppInfo(url=url))]
        ])
        await update.message.reply_text("📦 Ваши посылки:", reply_markup=kb)

    # адрес
    elif text == "📍 Адреса":
        if not user:
            await update.message.reply_text("Сначала зарегистрируйтесь")
            return

        await update.message.reply_text(
            f"📦 Адрес в Китае:\n\nVXMMM {user['client_code']}\n广东省..."
        )

    # инструкция
    elif text == "📖 Инструкция":
        await update.message.reply_text(
            "1. Закажи товар\n2. Укажи наш адрес\n3. Добавь код\n4. Жди доставку"
        )

    else:
        await start(update, context)

# ================= ЗАПУСК =================

def main():
    if not TOKEN:
        print("❌ ВСТАВЬ BOT_TOKEN В ENV!")
        return

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))

    print("✅ Бот запущен...")
    app.run_polling()

# ================= ENTRY =================

if __name__ == "__main__":
    main()
