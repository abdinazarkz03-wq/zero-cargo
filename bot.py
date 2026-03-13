import os
from telegram import (
Update, ReplyKeyboardMarkup, KeyboardButton,
InlineKeyboardMarkup, InlineKeyboardButton
)
from telegram.ext import (
Application, CommandHandler, MessageHandler,
filters, ContextTypes, CallbackQueryHandler, ConversationHandler
)

BOT_TOKEN = os.environ.get(“BOT_TOKEN”, “8676654212:AAGEM9nhV2uP0a3NwAaBksFqwvSx37a5TsY”)

COMPANY_NAME = “Zero Cargo312”
PERSONAL_CODE_PREFIX = “ZC”
WHATSAPP_LINK = “https://wa.me/996505600542”
INSTAGRAM_LINK = “https://instagram.com/zero_cargo.313”
WEBAPP_LINK = “https://t.me/zerocargo312_bot”
PRICE_PER_KG = 2.8
DELIVERY_DAYS = “7-14”

WAITING_TRACK = 1

packages_db = {
“ZC-2024-08821”: {
“status”: “🚛 В пути”,
“weight”: “12 кг”,
“type”: “Электроника”,
“steps”: [
(“✅”, “Принят на склад Гуанчжоу”, “15 янв 2025”),
(“✅”, “Отправлен со склада”, “18 янв 2025”),
(“✅”, “Прибыл на КПП Торугарт”, “22 янв 2025”),
(“⏳”, “Таможенное оформление”, “ожидается…”),
(“⬜”, “Склад Бишкек”, “-”),
(“⬜”, “Доставлен получателю”, “-”),
]
}
}

users_db = {}

def gen_client_code(user_id: int) -> str:
chars = ‘ABCDEFGHJKLMNPQRSTUVWXYZ23456789’
h = abs(user_id * 2654435761) ^ (user_id >> 16)
code = ‘’
for _ in range(4):
code += chars[h % len(chars)]
h = (h // len(chars)) + (h * 31)
return f”{PERSONAL_CODE_PREFIX}-{code[:4]}”

def main_keyboard():
keyboard = [
[KeyboardButton(“👤 Профиль”), KeyboardButton(“📋 Адреса”), KeyboardButton(“📦 Мои посылки”)],
[KeyboardButton(“📕 Инструкция”), KeyboardButton(“🚫 Запрещённые”), KeyboardButton(“⚙️ Поддержка”)],
[KeyboardButton(“✅ Добавить трек”)],
]
return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, persistent=True)

def cancel_keyboard():
return ReplyKeyboardMarkup([[KeyboardButton(“⬅️ Отмена”)]], resize_keyboard=True)

def packages_keyboard():
return ReplyKeyboardMarkup([
[KeyboardButton(“🚛 В пути”)],
[KeyboardButton(“✅ В офисе”)],
[KeyboardButton(“⬅️ Назад”)],
], resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
user = update.effective_user
uid = user.id
if uid not in users_db:
users_db[uid] = {
“code”: gen_client_code(uid),
“name”: f”{user.first_name} {user.last_name or ‘’}”.strip(),
“phone”: “”,
“address”: “”,
}
u = users_db[uid]
code = u[“code”]
welcome_text = (
f”👋 Добро пожаловать в *{COMPANY_NAME}*!\n\n”
f”🪪 Персональный КОД: *{code}*\n”
f”👤 ФИО: {u[‘name’]}\n”
f”📞 Номер: {u[‘phone’] or ‘не указан’}\n”
f”🏠 Адрес: {u[‘address’] or ‘не указан’}\n\n”
f”🇨🇳➡️🇰🇬 Доставка Китай → Бишкек\n”
f”💰 *{PRICE_PER_KG}$ / кг* • ⏱ *{DELIVERY_DAYS} дней*”
)
inline_buttons = InlineKeyboardMarkup([
[InlineKeyboardButton(“✏️ Изменить профиль”, callback_data=“edit_profile”)],
[InlineKeyboardButton(“🌐 Сменить язык 🇰🇬”, callback_data=“change_lang”)],
[InlineKeyboardButton(“🌍 Войти в личный кабинет”, url=WEBAPP_LINK)],
])
await update.message.reply_text(welcome_text, parse_mode=“Markdown”, reply_markup=inline_buttons)
await update.message.reply_text(“👇 Выберите нужный раздел:”, reply_markup=main_keyboard())

async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
uid = update.effective_user.id
if uid not in users_db:
await start(update, context)
return
u = users_db[uid]
text = (
f”📋 *Ваш профиль*\n\n”
f”🪪 Персональный КОД: *{u[‘code’]}*\n”
f”👤 ФИО: {u[‘name’]}\n”
f”📞 Номер: {u[‘phone’] or ‘-’}\n”
f”🏠 Адрес: {u[‘address’] or ‘-’}\n\n”
f”📍 ПВЗ: Рухий Мурас\n”
f”📞 ПВЗ телефон: +996 505 600 542\n”
f”🕐 Часы работы: 10:00 - 19:00”
)
await update.message.reply_text(text, parse_mode=“Markdown”,
reply_markup=InlineKeyboardMarkup([
[InlineKeyboardButton(“🌍 Войти в кабинет”, url=WEBAPP_LINK)],
[InlineKeyboardButton(“🇰🇬 Тилди алмаштыруу”, callback_data=“change_lang”)],
]))

async def addresses(update: Update, context: ContextTypes.DEFAULT_TYPE):
uid = update.effective_user.id
code = users_db.get(uid, {}).get(“code”, “ZC-XXXX”)
await update.message.reply_text(“📬 *Скопируйте ниже. Это адрес склада в Китае 🇨🇳:*”, parse_mode=“Markdown”)
await update.message.reply_text(
f”广东省佛山市南海区里广路洲村工业区飞机场13-2号\n”
f”收件人：VXMMM\n”
f”电话：135 4510 0875\n”
f”（TSL КАРГО）*{code}*\n\n”
f”⚠️ Напишите продавцу код *{code}* в примечании!”,
parse_mode=“Markdown”
)
await update.message.reply_text(
f”🇰🇬 *Адрес выдачи в Бишкеке:*\n\n”
f”📍 ПВЗ: Рухий Мурас\n”
f”📞 Телефон: +996 505 600 542\n”
f”🕐 Часы работы: 10:00 - 19:00”,
parse_mode=“Markdown”, reply_markup=main_keyboard())

async def my_packages(update: Update, context: ContextTypes.DEFAULT_TYPE):
await update.message.reply_text(“📦 *Мои посылки:*\n\nВыберите статус:”,
parse_mode=“Markdown”, reply_markup=packages_keyboard())

async def packages_in_transit(update: Update, context: ContextTypes.DEFAULT_TYPE):
await update.message.reply_text(
“🚛 *Посылки в пути:*\n\n_Для деталей нажмите_ ✅ Добавить трек”,
parse_mode=“Markdown”, reply_markup=main_keyboard())

async def packages_in_office(update: Update, context: ContextTypes.DEFAULT_TYPE):
await update.message.reply_text(
“✅ *Посылки в офисе (готовы к выдаче):*\n\n”
“📍 Адрес: Рухий Мурас\n📞 +996 505 600 542”,
parse_mode=“Markdown”, reply_markup=main_keyboard())

async def add_track_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
await update.message.reply_text(
“✅ *Отправьте трек код для отслеживания*\n\n”
“❗ Можно разделить трек код через запятую\n”
“*(YT1111 носки, 67899876 куртка)*”,
parse_mode=“Markdown”, reply_markup=cancel_keyboard())
return WAITING_TRACK

async def process_track(update: Update, context: ContextTypes.DEFAULT_TYPE):
text = update.message.text.strip()
if text == “⬅️ Отмена”:
await update.message.reply_text(“Вы отменили последнюю команду”, reply_markup=main_keyboard())
return ConversationHandler.END
tracks = [t.strip() for t in text.replace(”,”, “\n”).split(”\n”) if t.strip()]
result = “”
for track_raw in tracks:
parts = track_raw.split(” “, 1)
track_id = parts[0].upper()
label = parts[1] if len(parts) > 1 else “”
if track_id in packages_db:
pkg = packages_db[track_id]
steps_text = “\n”.join([f”   {icon} {title} — {date}” for icon, title, date in pkg[“steps”]])
result += f”\n📦 *{track_id}*{’ (’ + label + ‘)’ if label else ‘’}\nСтатус: {pkg[‘status’]}\n\n{steps_text}\n”
else:
result += f”\n❌ *{track_id}* — не найден\n”
await update.message.reply_text(result or “❌ Не найдено”, parse_mode=“Markdown”, reply_markup=main_keyboard())
return ConversationHandler.END

async def forbidden(update: Update, context: ContextTypes.DEFAULT_TYPE):
await update.message.reply_text(
“🚫 *Запрещённые к перевозке товары:*\n\n”
“🔴 Лекарства, наркотики, психотропные вещества\n”
“🔴 Взрывчатые, легковоспламеняющиеся вещества\n”
“🔴 Жидкие и сыпучие вещества\n”
“🔴 Электронные сигареты, вейпы\n”
“🔴 Острые, режущие предметы\n\n”
“❗ Штраф за нарушение: *10-50 тысяч сом*”,
parse_mode=“Markdown”,
reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(“💬 Спросить менеджера”, url=WHATSAPP_LINK)]]))
await update.message.reply_text(“👇 Меню:”, reply_markup=main_keyboard())

async def instruction(update: Update, context: ContextTypes.DEFAULT_TYPE):
uid = update.effective_user.id
code = users_db.get(uid, {}).get(“code”, “ZC-XXXX”)
await update.message.reply_text(“📕 *Выберите маркетплейс:*”, parse_mode=“Markdown”,
reply_markup=InlineKeyboardMarkup([
[InlineKeyboardButton(“Пиндуодуо”, url=“https://www.pinduoduo.com”),
InlineKeyboardButton(“Таобао”, url=“https://www.taobao.com”)],
[InlineKeyboardButton(“1688”, url=“https://www.1688.com”),
InlineKeyboardButton(“JD”, url=“https://www.jd.com”)],
]))
await update.message.reply_text(
f”📖 *Инструкция:*\n\n”
f”1️⃣ Выберите товар на маркетплейсе\n”
f”2️⃣ Укажите адрес нашего склада в Китае\n”
f”3️⃣ В примечании напишите ваш код: *{code}*\n”
f”4️⃣ Добавьте трек-код через кнопку ✅ Добавить трек\n”
f”5️⃣ Мы уведомим о прибытии груза”,
parse_mode=“Markdown”, reply_markup=main_keyboard())

async def support(update: Update, context: ContextTypes.DEFAULT_TYPE):
await update.message.reply_text(
“⚙️ *Поддержка Zero Cargo312*\n\n”
“💬 WhatsApp: +996 505 600 542\n”
“📸 Instagram: @zero_cargo.313\n”
“🕐 Работаем: 09:00 - 20:00”,
parse_mode=“Markdown”,
reply_markup=InlineKeyboardMarkup([
[InlineKeyboardButton(“💬 WhatsApp”, url=WHATSAPP_LINK)],
[InlineKeyboardButton(“📸 Instagram”, url=INSTAGRAM_LINK)],
]))
await update.message.reply_text(“👇 Меню:”, reply_markup=main_keyboard())

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
query = update.callback_query
await query.answer()
if query.data == “change_lang”:
await query.message.reply_text(“🌐 Выберите язык:”,
reply_markup=InlineKeyboardMarkup([
[InlineKeyboardButton(“🇷🇺 Русский”, callback_data=“lang_ru”)],
[InlineKeyboardButton(“🇰🇬 Кыргызча”, callback_data=“lang_kg”)],
]))
elif query.data == “lang_ru”:
await query.message.reply_text(“✅ Язык изменён на Русский”)
elif query.data == “lang_kg”:
await query.message.reply_text(“✅ Тил кыргызчага өзгөртүлдү”)
elif query.data == “edit_profile”:
await query.message.reply_text(“✏️ Свяжитесь с поддержкой для изменения профиля.”)

async def go_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
await update.message.reply_text(“👇 Главное меню:”, reply_markup=main_keyboard())

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
await update.message.reply_text(“❓ Используйте кнопки меню 👇”, reply_markup=main_keyboard())

def main():
print(f”🚀 Запуск {COMPANY_NAME}…”)
app = Application.builder().token(BOT_TOKEN).build()
track_conv = ConversationHandler(
entry_points=[MessageHandler(filters.Regex(“✅ Добавить трек”), add_track_start)],
states={WAITING_TRACK: [MessageHandler(filters.TEXT, process_track)]},
fallbacks=[MessageHandler(filters.Regex(“⬅️ Отмена”), go_back)],
)
app.add_handler(CommandHandler(“start”, start))
app.add_handler(track_conv)
app.add_handler(MessageHandler(filters.Regex(“👤 Профиль”), profile))
app.add_handler(MessageHandler(filters.Regex(“📋 Адреса”), addresses))
app.add_handler(MessageHandler(filters.Regex(“📦 Мои посылки”), my_packages))
app.add_handler(MessageHandler(filters.Regex(“🚛 В пути”), packages_in_transit))
app.add_handler(MessageHandler(filters.Regex(“✅ В офисе”), packages_in_office))
app.add_handler(MessageHandler(filters.Regex(“📕 Инструкция”), instruction))
app.add_handler(MessageHandler(filters.Regex(“🚫 Запрещённые”), forbidden))
app.add_handler(MessageHandler(filters.Regex(“⚙️ Поддержка”), support))
app.add_handler(MessageHandler(filters.Regex(“⬅️ Назад|⬅️ Отмена”), go_back))
app.add_handler(CallbackQueryHandler(callback_handler))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, unknown))
print(“✅ Бот запущен!”)
app.run_polling(drop_pending_updates=True)

if **name** == “**main**”:
main()
