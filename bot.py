import logging, json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ConversationHandler, ContextTypes
)
from config import *
from database import connect, get_user, register_user, get_user_with_parcels, add_parcel, get_user_parcels, set_language
from database import get_all_users, get_stats

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

FULL_NAME, PHONE, ADDRESS, TRACK_CODE = range(4)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = await get_user(user_id)
    if user:
        await show_main_menu(update, user)
    else:
        keyboard = [
            [InlineKeyboardButton("📝 Пройти регистрацию", callback_data="register")],
            [InlineKeyboardButton("🇷🇺/🇰🇬 Язык", callback_data="language")]
        ]
        await update.message.reply_text(
            f"🌟 {COMPANY_NAME}\nДоставка из Китая\n💰 {PRICE_PER_KG}/кг\n⏱ {DELIVERY_TIME}\n📍 {PICKUP_ADDRESS}\n\nПройдите регистрацию",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

async def show_main_menu(update, user):
    text = f"👤 Ваш профиль\nПерсональный код: {user['personal_code']}\nКод для Китая: {user['china_code']}"
    keyboard = [[InlineKeyboardButton("📦 Посылки", callback_data="my_parcels")]]
    if update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def register_start(update, context):
    await update.callback_query.answer()
    await update.callback_query.edit_message_text("Введите ФИО:")
    return FULL_NAME

async def get_full_name(update, context):
    context.user_data['full_name'] = update.message.text
    await update.message.reply_text("Введите номер телефона:")
    return PHONE

async def get_phone(update, context):
    phone = update.message.text.strip().replace("+","").replace(" ","")
    if not phone.isdigit():
        await update.message.reply_text("Только цифры, попробуйте снова:")
        return PHONE
    context.user_data['phone'] = phone
    await update.message.reply_text("Введите адрес:")
    return ADDRESS

async def get_address(update, context):
    user_id = update.effective_user.id
    user = await register_user(user_id, context.user_data['full_name'], context.user_data['phone'], update.message.text)
    await show_main_menu(update, user)
    return ConversationHandler.END

async def handle_callback(update, context):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    user = await get_user(user_id)
    
    if query.data == "register":
        return await register_start(update, context)
    elif query.data == "my_parcels":
        parcels = await get_user_parcels(user_id)
        text = "📦 Посылки:\n" + "\n".join([p['track_code'] for p in parcels]) if parcels else "📭 Нет посылок"
        await query.edit_message_text(text)

async def handle_track(update, context):
    tracks = [t.strip() for t in update.message.text.split(",")]
    added = 0
    for t in tracks:
        if await add_parcel(update.effective_user.id, t):
            added += 1
    await update.message.reply_text(f"✅ Добавлено посылок: {added}")
    return ConversationHandler.END

async def main():
    await connect()
    app = Application.builder().token(BOT_TOKEN).build()
    
    reg_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(register_start, pattern="^register$")],
        states={
            FULL_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_full_name)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
            ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_address)],
        },
        fallbacks=[]
    )
    
    track_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.TEXT & ~filters.COMMAND, handle_track)],
        states={TRACK_CODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_track)]},
        fallbacks=[]
    )
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(reg_conv)
    app.add_handler(track_conv)
    app.add_handler(CallbackQueryHandler(handle_callback))
    
    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
