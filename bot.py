import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

BOT_TOKEN = os.environ.get("BOT_TOKEN")
WEB_APP_URL = "https://abdinazarkz03-wq.github.io/zero-cargo/"

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    name = message.from_user.first_name or "друг"
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(
        "🚛 Открыть Zero Cargo312",
        web_app=WebAppInfo(url=WEB_APP_URL)
    ))
    bot.send_message(
        message.chat.id,
        f"👋 Привет, {name}!\n\n🇨🇳 *Zero Cargo312* — доставка из Китая в Бишкек\n\n📦 Тариф: 2.8$ за кг\n⏱ Срок: 7–14 дней\n✅ Предоплата: 0%\n\n👇 Нажмите кнопку:",
        parse_mode="Markdown",
        reply_markup=markup
    )

@bot.message_handler(func=lambda m: True)
def echo(message):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(
        "🚛 Открыть приложение",
        web_app=WebAppInfo(url=WEB_APP_URL)
    ))
    bot.send_message(message.chat.id, "👇 Нажмите кнопку:", reply_markup=markup)

bot.polling(none_stop=True)
