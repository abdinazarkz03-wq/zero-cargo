import os
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler, ConversationHandler

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8676654212:AAFtmReTMfPUrBMkVGSqc2XTUoBhmiwMmaU")

COMPANY_NAME = "Zero Cargo312"
PREFIX = "ZC"
WA = "https://wa.me/996505600542"
IG = "https://instagram.com/zero_cargo.313"
WEB = "https://t.me/zerocargo312_bot"

WAITING_TRACK = 1

users_db = {}

def gen_code(uid):
    chars = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    h = abs(uid * 2654435761) ^ (uid >> 16)
    code = ""
    for _ in range(4):
        code += chars[h % len(chars)]
        h = (h // len(chars)) + (h * 31)
    return PREFIX + "-" + code[:4]

def main_kb():
    return ReplyKeyboardMarkup([
        [KeyboardButton("👤 Профиль"), KeyboardButton("📋 Адреса"), KeyboardButton("📦 Мои посылки")],
        [KeyboardButton("📕 Инструкция"), KeyboardButton("🚫 Запрещённые"), KeyboardButton("⚙️ Поддержка")],
        [KeyboardButton("✅ Добавить трек")],
    ], resize_keyboard=True, persistent=True)

def cancel_kb():
    return ReplyKeyboardMarkup([[KeyboardButton("⬅️ Отмена")]], resize_keyboard=True)

def pkg_kb():
    return ReplyKeyboardMarkup([
        [KeyboardButton("🚛 В пути")],
        [KeyboardButton("✅ В офисе")],
        [KeyboardButton("⬅️ Назад")],
    ], resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    uid = user.id

    if uid not in users_db:
        users_db[uid] = {
            "code": gen_code(uid),
            "name": (user.first_name or "") + " " + (user.last_name or ""),
            "phone": "",
            "address": "",
        }

    u = users_db[uid]
    code = u["code"]

    text = (
        "👋 Добро пожаловать в " + COMPANY_NAME + "!\n\n"
        "🪪 Персональный КОД: " + code + "\n"
        "👤 ФИО: " + u["name"].strip() + "\n"
        "📞 Номер: " + (u["phone"] or "не указан") + "\n"
        "🏠 Адрес: " + (u["address"] or "не указан") + "\n\n"
        "🇨🇳 Доставка Китай → Бишкек\n"
        "💰 2.8$ / кг  •  ⏱ 7-14 дней"
    )

    btns = InlineKeyboardMarkup([
        [InlineKeyboardButton("✏️ Изменить профиль", callback_data="edit")],
        [InlineKeyboardButton("🌐 Сменить язык 🇰🇬", callback_data="lang")],
        [InlineKeyboardButton("🌍 Личный кабинет", url=WEB)],
    ])

    await update.message.reply_text(text, reply_markup=btns)
    await update.message.reply_text("👇 Выберите раздел:", reply_markup=main_kb())

async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id

    if uid not in users_db:
        await start(update, context)
        return

    u = users_db[uid]

    text = (
        "📋 Ваш профиль\n\n"
        "🪪 КОД: " + u["code"] + "\n"
        "👤 ФИО: " + u["name"].strip() + "\n"
        "📞 Номер: " + (u["phone"] or "-") + "\n"
        "🏠 Адрес: " + (u["address"] or "-") + "\n\n"
        "📍 ПВЗ: Рухий Мурас\n"
        "📞 +996 505 600 542\n"
        "🕐 10:00 - 19:00"
    )

    await update.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🌍 Личный кабинет", url=WEB)],
            [InlineKeyboardButton("🇰🇬 Тилди алмаштыруу", callback_data="lang")],
        ])
    )

async def addresses(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    code = users_db.get(uid, {}).get("code", "ZC-XXXX")

    await update.message.reply_text("📬 Адрес склада в Китае 🇨🇳:")

    await update.message.reply_text(
        "广东省佛山市南海区里广路洲村工业区飞机场13-2号\n"
        "收件人: VXMMM\n"
        "电话: 135 4510 0875\n"
        "TSL КАРГО - " + code + "\n\n"
        "⚠️ Напишите код " + code + " в примечании!"
    )

    await update.message.reply_text(
        "🇰🇬 Выдача в Бишкеке:\n\n"
        "📍 ПВЗ: Рухий Мурас\n"
        "📞 +996 505 600 542\n"
        "🕐 10:00 - 19:00",
        reply_markup=main_kb()
    )

async def my_packages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📦 Мои посылки:\n\nВыберите статус:",
        reply_markup=pkg_kb()
    )

async def in_transit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🚛 Посылки в пути:\n\nДля деталей нажмите ✅ Добавить трек",
        reply_markup=main_kb()
    )

async def in_office(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✅ Посылки в офисе:\n\n📍 Рухий Мурас\n📞 +996 505 600 542",
        reply_markup=main_kb()
    )

async def track_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✅ Отправьте трек код\n\n"
        "❗ Можно через запятую:\n"
        "YT1111 носки, 67899876 куртка",
        reply_markup=cancel_kb()
    )
    return WAITING_TRACK

async def track_process(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if text == "⬅️ Отмена":
        await update.message.reply_text("Отменено", reply_markup=main_kb())
        return ConversationHandler.END

    await update.message.reply_text(
        "🔍 Трек-код " + text + " принят!\n\nСвяжитесь с менеджером для уточнения статуса.",
        reply_markup=main_kb()
    )

    return ConversationHandler.END

async def forbidden(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🚫 Запрещённые товары:\n\n"
        "🔴 Лекарства, наркотики\n"
        "🔴 Взрывчатые вещества\n"
        "🔴 Жидкие и сыпучие\n"
        "🔴 Электронные сигареты\n"
        "🔴 Острые предметы\n\n"
        "❗ Штраф: 10-50 тысяч сом",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("💬 Спросить менеджера", url=WA)]
        ]),
    )

    await update.message.reply_text("👇 Меню:", reply_markup=main_kb())

async def instruction(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    code = users_db.get(uid, {}).get("code", "ZC-XXXX")

    await update.message.reply_text(
        "📕 Выберите маркетплейс:",
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton("Пиндуодуо", url="https://www.pinduoduo.com"),
                InlineKeyboardButton("Таобао", url="https://www.taobao.com")
            ],
            [
                InlineKeyboardButton("1688", url="https://www.1688.com"),
                InlineKeyboardButton("JD", url="https://www.jd.com")
            ],
        ])
    )

    await update.message.reply_text(
        "📖 Инструкция:\n\n"
        "1️⃣ Выберите товар\n"
        "2️⃣ Укажите адрес склада\n"
        "3️⃣ Напишите код: " + code + "\n"
        "4️⃣ Добавьте трек через бот\n"
        "5️⃣ Уведомим о прибытии",
        reply_markup=main_kb()
    )

async def support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "⚙️ Поддержка " + COMPANY_NAME + "\n\n"
        "💬 WhatsApp: +996 505 600 542\n"
        "📸 Instagram: @zero_cargo.313\n"
        "🕐 09:00 - 20:00",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("💬 WhatsApp", url=WA)],
            [InlineKeyboardButton("📸 Instagram", url=IG)],
        ])
    )

    await update.message.reply_text("👇 Меню:", reply_markup=main_kb())

async def back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👇 Меню:", reply_markup=main_kb())

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❓ Используйте кнопки меню 👇", reply_markup=main_kb())

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("✅ Добавить трек"), track_start)],
        states={
            WAITING_TRACK: [MessageHandler(filters.TEXT, track_process)]
        },
        fallbacks=[MessageHandler(filters.Regex("⬅️ Отмена"), back)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv)

    app.add_handler(MessageHandler(filters.Regex("👤 Профиль"), profile))
    app.add_handler(MessageHandler(filters.Regex("📋 Адреса"), addresses))
    app.add_handler(MessageHandler(filters.Regex("📦 Мои посылки"), my_packages))
    app.add_handler(MessageHandler(filters.Regex("🚛 В пути"), in_transit))
    app.add_handler(MessageHandler(filters.Regex("✅ В офисе"), in_office))
    app.add_handler(MessageHandler(filters.Regex("📕 Инструкция"), instruction))
    app.add_handler(MessageHandler(filters.Regex("🚫 Запрещённые"), forbidden))
    app.add_handler(MessageHandler(filters.Regex("⚙️ Поддержка"), support))

    app.add_handler(MessageHandler(filters.Regex("⬅️ Назад|⬅️ Отмена"), back))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, unknown))

    print("Бот запущен!")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
