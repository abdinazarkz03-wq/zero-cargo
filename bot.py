import logging, asyncio, json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes, ConversationHandler
)
from config import *
from database import db

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Состояния
FULL_NAME, PHONE, ADDRESS, TRACK_CODE = range(4)

# ==== Главное меню ====
async def get_main_menu():
    keyboard = [
        [InlineKeyboardButton("👤 Профиль", callback_data="profile")],
        [InlineKeyboardButton("📍 Адреса", callback_data="addresses")],
        [InlineKeyboardButton("📦 Мои посылки", callback_data="my_parcels")],
        [InlineKeyboardButton("📋 Инструкция", callback_data="instructions")],
        [InlineKeyboardButton("⛔ Запрещенные товары", callback_data="prohibited")],
        [InlineKeyboardButton("💬 Поддержка", callback_data="support")],
        [InlineKeyboardButton("➕ Добавить трек", callback_data="add_track")]
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = await db.get_user(user_id)
    if user:
        await show_main_menu(update, user)
    else:
        keyboard = [
            [InlineKeyboardButton("📝 Пройти регистрацию", callback_data="register")],
            [InlineKeyboardButton("🇷🇺/🇰🇬 Язык", callback_data="language")]
        ]
        await update.message.reply_text(
            f"🌟 ZERO CARGO\n💰 {PRICE_PER_KG}/кг\n⏱ {DELIVERY_TIME}\n📍 {PICKUP_ADDRESS}\n\nПройдите регистрацию для персонального кода",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

async def show_main_menu(update, user):
    text = (
        f"👤 **Профиль**\n\n"
        f"Персональный код: `{user['personal_code']}`\n"
        f"Код для Китая: `{user['china_code']}`\n"
        f"ФИО: {user['full_name']}\n"
        f"Номер: +{user['phone']}\n"
        f"Адрес: {user['address'] or 'Не указан'}"
    )
    keyboard = [[InlineKeyboardButton("◀️ Назад", callback_data="dashboard")]]
    if update.callback_query:
        await update.callback_query.edit_message_text(text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await update.message.reply_text(text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))

# ==== Регистрация ====
async def register_start(update, context):
    await update.callback_query.answer()
    await update.callback_query.edit_message_text("📝 Введите ваше ФИО:")
    return FULL_NAME

async def get_full_name(update, context):
    context.user_data['full_name'] = update.message.text
    await update.message.reply_text("📞 Введите номер телефона:")
    return PHONE

async def get_phone(update, context):
    phone = update.message.text.strip().replace('+','').replace(' ','')
    if not phone.isdigit():
        await update.message.reply_text("❌ Введите корректный номер:")
        return PHONE
    context.user_data['phone'] = phone
    await update.message.reply_text("🏠 Введите адрес проживания:")
    return ADDRESS

async def get_address(update, context):
    user_id = update.effective_user.id
    full_name = context.user_data['full_name']
    phone = context.user_data['phone']
    address = update.message.text
    user = await db.register_user(user_id, full_name, phone, address)
    if user:
        await show_main_menu(update, user)
    else:
        await update.message.reply_text("❌ Ошибка регистрации")
    return ConversationHandler.END

# ==== Добавление треков ====
async def handle_track(update, context):
    tracks = [t.strip() for t in update.message.text.split(',')]
    added = 0
    for track in tracks:
        if await db.add_parcel(update.effective_user.id, track):
            added += 1
    await update.message.reply_text(f"✅ Добавлено посылок: {added}", reply_markup=await get_main_menu())
    return ConversationHandler.END

# ==== Callback кнопки ====
async def handle_callback(update, context):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    user = await db.get_user(user_id)
    
    if query.data == "dashboard":
        await query.edit_message_text("📱 Личный кабинет", reply_markup=await get_main_menu())
    elif query.data == "profile":
        if user: await show_main_menu(update, user)
    elif query.data == "add_track":
        await query.edit_message_text("📦 Введите трек-код (через запятую)")
        return TRACK_CODE

# ==== Запуск бота ====
async def main():
    await db.connect()
    app = Application.builder().token(BOT_TOKEN).build()
    
    reg_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(register_start, pattern="^register$")],
        states={
            FULL_NAME:[MessageHandler(filters.TEXT & ~filters.COMMAND, get_full_name)],
            PHONE:[MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
            ADDRESS:[MessageHandler(filters.TEXT & ~filters.COMMAND, get_address)]
        },
        fallbacks=[]
    )
    
    track_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(handle_callback, pattern="^add_track$")],
        states={TRACK_CODE:[MessageHandler(filters.TEXT & ~filters.COMMAND, handle_track)]},
        fallbacks=[]
    )
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(reg_conv)
    app.add_handler(track_conv)
    app.add_handler(CallbackQueryHandler(handle_callback))
    
    logger.info("🚀 Бот запущен!")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
