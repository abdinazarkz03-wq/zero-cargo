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
    ContextTypes
)

TOKEN = os.getenv("BOT_TOKEN")
WEBAPP_URL = os.getenv("WEBAPP_URL", "https://zerocargo-webapp.onrender.com")

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def get_user(telegram_id):
    try:
        response = requests.get(
            f"{WEBAPP_URL}/api/user",
            params={"telegram_id": telegram_id},
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            return data if data.get("found") else None
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"API error getting user {telegram_id}: {e}")
        return None

def get_main_keyboard(registered=False):
    if not registered:
        keyboard = [[KeyboardButton("📝 Регистрация")]]
    else:
        keyboard = [
            [KeyboardButton("📦 Мой код"), KeyboardButton("🚨 Мои посылки")],
            [KeyboardButton("📍 Адреса"), KeyboardButton("📖 Инструкция")],
            [KeyboardButton("💰 Тарифы"), KeyboardButton("📞 Контакты")]
        ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    first_name = update.effective_user.first_name
    
    user = get_user(user_id)
    
    if user:
        text = (
            f"👋 С возвращением, {first_name}!\n\n"
            f"🔑 Ваш персональный код: {user['client_code']}\n"
            f"📦 Статус: Активный клиент"
        )
        await update.message.reply_text(text, reply_markup=get_main_keyboard(True))
    else:
        text = (
            "🚛 Добро пожаловать в ZERO CARGO!\n\n"
            "Мы помогаем быстро и надёжно доставлять грузы из Китая в Бишкек.\n"
            "Нажмите «Регистрация», чтобы начать."
        )
        await update.message.reply_text(text, reply_markup=get_main_keyboard(False))

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id
    user = get_user(user_id)
    
    if text == "📝 Регистрация":
        if user:
            await update.message.reply_text(
                f"Вы уже зарегистрированы! Ваш код: {user['client_code']}",
                reply_markup=get_main_keyboard(True)
            )
            return
        
        url = f"{WEBAPP_URL}/register?user_id={user_id}"
        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton("📝 Открыть регистрацию", web_app=WebAppInfo(url=url))
        ]])
        await update.message.reply_text(
            "Нажмите кнопку, чтобы заполнить форму регистрации:",
            reply_markup=keyboard
        )
    
    elif text == "📦 Мой код":
        if not user:
            await update.message.reply_text(
                "Сначала зарегистрируйтесь!",
                reply_markup=get_main_keyboard(False)
            )
            return
        
        await update.message.reply_text(
            f"🔑 **Ваш персональный код:**\n`{user['client_code']}`\n\n"
            f"👤 {user['full_name']}\n"
            f"📱 {user['phone']}",
            parse_mode='Markdown'
        )
    
    elif text == "🚨 Мои посылки":
        if not user:
            await update.message.reply_text(
                "Сначала зарегистрируйтесь!",
                reply_markup=get_main_keyboard(False)
            )
            return
        
        url = f"{WEBAPP_URL}/parcels?code={user['client_code']}"
        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton("📦 Открыть посылки", web_app=WebAppInfo(url=url))
        ]])
        await update.message.reply_text(
            "Нажмите кнопку, чтобы посмотреть свои посылки:",
            reply_markup=keyboard
        )
    
    elif text == "📍 Адреса":
        if not user:
            await update.message.reply_text(
                "Сначала зарегистрируйтесь!",
                reply_markup=get_main_keyboard(False)
            )
            return
        
        address_text = (
            "🏠 **Наш склад в Китае:**\n\n"
            "广东省广州市白云区\n"
            "ZERO CARGO\n"
            f"收件人: VXMMM {user['client_code']}\n"
            "电话: +86 123 4567 8901\n\n"
            "⚠️ **Важно:** Всегда указывайте ваш код после VXMMM!"
        )
        await update.message.reply_text(address_text, parse_mode='Markdown')
    
    elif text == "📖 Инструкция":
        instruction = (
            "📚 **Как сделать заказ:**\n\n"
            "1. Заказываете товар на Taobao, 1688 или любом другом сайте\n"
            "2. В качестве адреса доставки указываете наш склад в Китае\n"
            "3. Обязательно добавляете свой персональный код (VXMMM******)\n"
            "4. После того, как товар придет на склад, мы внесем его в систему\n"
            "5. Отслеживайте статус в разделе «Мои посылки»\n"
            "6. Когда все посылки соберутся, мы отправим их в Бишкек\n\n"
            "Срок доставки: 7-14 дней\n"
            "Стоимость: $2.8 за кг"
        )
        await update.message.reply_text(instruction, parse_mode='Markdown')
    
    elif text == "💰 Тарифы":
        rates = (
            "💰 **Наши тарифы:**\n\n"
            "• Доставка из Китая в Бишкек: **$2.8/кг**\n"
            "• Минимальный вес: **1 кг**\n"
            "• Сроки: **7-14 дней**\n"
            "• Страховка: **5% от стоимости** (опционально)\n"
            "• Забор груза по Китаю: **от $5**\n\n"
            "Оплата при получении в Бишкеке."
        )
        await update.message.reply_text(rates, parse_mode='Markdown')
    
    elif text == "📞 Контакты":
        contacts = (
            "📞 **Наши контакты:**\n\n"
            "📍 Адрес в Бишкеке: ж/м Рухий Мурас\n"
            "📱 Телефон: +996 998 881 082\n"
            "📧 Email: info@zerocargo.kg\n"
            "🕒 Работаем: Пн-Пт 9:00-18:00\n\n"
            "📢 Наш канал: @zerocargo_kg"
        )
        await update.message.reply_text(contacts, parse_mode='Markdown')
    
    else:
        await start(update, context)

def main():
    if not TOKEN:
        logger.error("Не задан BOT_TOKEN! Установите переменную окружения.")
        return
    
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()
