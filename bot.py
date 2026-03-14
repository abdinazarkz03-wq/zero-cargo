import os
import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler, CallbackQueryHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")


def gen_client_code(user_id: int) -> str:
    h = abs(user_id)
    h = ((h >> 16) ^ h) * 0x45d9f3b
    h = ((h >> 16) ^ h) * 0x45d9f3b
    h = (h >> 16) ^ h
    base = (abs(h) % 9000) + 1000
    seq = (abs(user_id) % 9) + 1
    return f"{base}-{seq}"


MAIN_MENU = ReplyKeyboardMarkup([
    [KeyboardButton("👤 Профиль"), KeyboardButton("📍 Адреса"), KeyboardButton("📦 Мои посылки")],
    [KeyboardButton("📖 Инструкция"), KeyboardButton("🚫 Запрещённое"), KeyboardButton("⚙️ Поддержка")],
    [KeyboardButton("✅ Добавить трек")],
], resize_keyboard=True)

CANCEL_MENU = ReplyKeyboardMarkup([[KeyboardButton("⬅️ Отмена")]], resize_keyboard=True)

WAITING_TRACK = 1


async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    code = gen_client_code(user.id)

    await update.message.reply_text(
        f"👋 Добро пожаловать, {user.full_name}!\n\n"
        f"🚚 *Zero Cargo312* — доставка из Китая в Бишкек\n"
        f"📦 Тариф: *2.8$ / кг* • Срок: *7–14 дней*\n\n"
        f"🪪 Ваш персональный код: *VXMMM {code}*\n"
        f"*Используйте его в примечании при заказе*",
        parse_mode="Markdown",
        reply_markup=MAIN_MENU
    )


async def profile(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    code = gen_client_code(user.id)

    username = f"@{user.username}" if user.username else "—"

    await update.message.reply_text(
        f"📋 *Ваш профиль*\n\n"
        f"🪪 Персональный КОД: *VXMMM {code}*\n"
        f"👤 Имя: *{user.full_name}*\n"
        f"📱 Username: {username}\n\n"
        f"*Ваш код не меняется — он привязан к Telegram аккаунту*",
        parse_mode="Markdown",
        reply_markup=MAIN_MENU
    )


async def addresses(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    code = gen_client_code(user.id)

    await update.message.reply_text(
        f"📬 *Адрес склада в Китае 🇨🇳*\n\n"
        f"`收件人：VXMMM\n"
        f"电话：13545100875\n"
        f"广东省佛山市南海区里广路洲村工业区飞机场13-2号\n"
        f"（TSL КАРГО）VXMMM {code}`\n\n"
        f"⚠️ Обязательно укажите код *VXMMM {code}* в примечании продавцу!",
        parse_mode="Markdown",
        reply_markup=MAIN_MENU
    )


async def my_parcels(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🚛 В пути", callback_data="parcels_transit")],
        [InlineKeyboardButton("✅ В офисе", callback_data="parcels_office")],
    ])

    await update.message.reply_text("📦 *Мои посылки:*", parse_mode="Markdown", reply_markup=kb)


async def instruction(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🛒 Пиндуодуо", callback_data="inst_pdd")],
        [InlineKeyboardButton("🛍 Таобао", callback_data="inst_taobao")],
        [InlineKeyboardButton("📦 1688", callback_data="inst_1688")],
    ])

    await update.message.reply_text(
        "📖 *Инструкция*\n\nВыберите маркетплейс:",
        parse_mode="Markdown",
        reply_markup=kb
    )


async def forbidden(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🚫 *Запрещённые к перевозке товары:*\n\n"
        "🔴 Наркотические и психотропные вещества\n"
        "🔴 Легковоспламеняющиеся, взрывоопасные вещества\n"
        "🔴 Острые, колющие, режущие предметы\n"
        "🔴 Оружие, имитация оружия\n"
        "🔴 Предметы военного характера\n"
        "🔴 Жидкие, сыпучие, порошковые вещества\n"
        "🔴 Электронные сигареты\n\n"
        "❓ Сомневаетесь — напишите нам в поддержку.\n\n"
        "⚠️ Штраф за нарушение: *10–50 тысяч* сом.",
        parse_mode="Markdown",
        reply_markup=MAIN_MENU
    )


async def support(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("💬 WhatsApp", url="https://wa.me/996505600542")],
        [InlineKeyboardButton("📸 Instagram", url="https://instagram.com/zero_cargo.312")],
    ])

    await update.message.reply_text(
        "⚙️ *Поддержка*\n\n"
        "📞 WhatsApp: +996 505 600 542\n"
        "📸 Instagram: @zero_cargo.312",
        parse_mode="Markdown",
        reply_markup=kb
    )


async def add_track_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✅ *Добавить трек-код*\n\n"
        "Отправьте трек-код для отслеживания\n\n"
        "❗ Можно несколько через запятую:\n"
        "*(YT1111 носки, 67899876 куртка)*",
        parse_mode="Markdown",
        reply_markup=CANCEL_MENU
    )
    return WAITING_TRACK


async def add_track_receive(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if text == "⬅️ Отмена":
        await update.message.reply_text("Вы отменили последнюю операцию.", reply_markup=MAIN_MENU)
        return ConversationHandler.END

    tracks = [t.strip() for t in text.split(",") if t.strip()]
    lines = "\n".join([f"✅ {t}" for t in tracks])

    await update.message.reply_text(
        f"📦 *Трек-коды добавлены:*\n\n{lines}\n\n"
        f"Мы уведомим вас когда посылка прибудет в Бишкек.",
        parse_mode="Markdown",
        reply_markup=MAIN_MENU
    )

    return ConversationHandler.END


async def cancel(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Вы отменили последнюю операцию.", reply_markup=MAIN_MENU)
    return ConversationHandler.END


async def callback_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    if q.data == "parcels_transit":
        await q.edit_message_text("🚛 *Посылки в пути:*\n\nПока нет посылок в пути.", parse_mode="Markdown")

    elif q.data == "parcels_office":
        await q.edit_message_text("✅ *Посылки в офисе:*\n\nПока нет посылок в офисе.", parse_mode="Markdown")

    elif q.data == "inst_pdd":
        await q.edit_message_text(
            "🛒 *Пиндуодуо:*\n\n"
            "1. Найдите товар → Купить\n"
            "2. Введите адрес склада\n"
            "3. В примечании укажите ВАШ КОД\n"
            "4. Оплатите и добавьте трек в бота",
            parse_mode="Markdown"
        )

    elif q.data == "inst_taobao":
        await q.edit_message_text(
            "🛍 *Таобао:*\n\n"
            "1. Найдите товар, выберите размер\n"
            "2. Введите адрес склада\n"
            "3. В примечании укажите ВАШ КОД\n"
            "4. Добавьте трек в бота",
            parse_mode="Markdown"
        )

    elif q.data == "inst_1688":
        await q.edit_message_text(
            "📦 *1688:*\n\n"
            "1. Найдите товар, свяжитесь с продавцом\n"
            "2. Укажите адрес склада\n"
            "3. В примечании укажите ВАШ КОД\n"
            "4. Добавьте трек в бота",
            parse_mode="Markdown"
        )


def main():
    app = Application.builder().token(TOKEN).build()

    track_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^✅ Добавить трек$"), add_track_start)],
        states={
            WAITING_TRACK: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_track_receive)]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(track_conv)

    app.add_handler(MessageHandler(filters.Regex("^👤 Профиль$"), profile))
    app.add_handler(MessageHandler(filters.Regex("^📍 Адреса$"), addresses))
    app.add_handler(MessageHandler(filters.Regex("^📦 Мои посылки$"), my_parcels))
    app.add_handler(MessageHandler(filters.Regex("^📖 Инструкция$"), instruction))
    app.add_handler(MessageHandler(filters.Regex("^🚫 Запрещённое$"), forbidden))
    app.add_handler(MessageHandler(filters.Regex("^⚙️ Поддержка$"), support))

    app.add_handler(CallbackQueryHandler(callback_handler))

    logger.info("Zero Cargo312 бот запущен!")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
