from telegram import (
Update, ReplyKeyboardMarkup, KeyboardButton,
InlineKeyboardMarkup, InlineKeyboardButton
)
from telegram.ext import (
Application, CommandHandler, MessageHandler,
filters, ContextTypes, CallbackQueryHandler, ConversationHandler
)

# ══════════════════════════════════════════════

# ВСТАВЬТЕ СВОЙ ТОКЕН ЗДЕСЬ

# ══════════════════════════════════════════════

BOT_TOKEN = “ВСТАВЬТЕ_ТОКЕН_СЮДА”

# ══════════════════════════════════════════════

# ВАШИ ДАННЫЕ — ЗАМЕНИТЕ НА СВОИ

# ══════════════════════════════════════════════

COMPANY_NAME = “Zero Cargo312”
PERSONAL_CODE_PREFIX = “ZC”

# Адрес склада в Китае

CHINA_ADDRESS = “”“广东省佛山市南海区里广路洲村工业区飞机场13-2号
收件人：VXMMM
电话：135 4510 0875
（TSL КАРГО）”””

# Адрес ПВЗ в Бишкеке

BISHKEK_ADDRESS = “”“📍 ПВЗ: Рухий Мурас
📞 Телефон: +996 505 600 542
🕐 Часы работы: 10:00 - 19:00”””

# Ссылки для поддержки

WHATSAPP_LINK = “https://wa.me/996505600542”
INSTAGRAM_LINK = “https://instagram.com/zero_cargo.313”
WEBAPP_LINK = “https://t.me/zerocar312_bot”  # Замените на ссылку вашего WebApp

# Тариф

PRICE_PER_KG = 2.8
DELIVERY_DAYS = “7–14”

# Состояния диалога

WAITING_TRACK = 1
WAITING_NAME = 2
WAITING_PHONE = 3
WAITING_ADDRESS_BISHKEK = 4
WAITING_GOODS = 5
WAITING_WEIGHT = 6

# База посылок (в реальном боте — это база данных)

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
(“⬜”, “Склад Бишкек”, “—”),
(“⬜”, “Доставлен получателю”, “—”),
]
},
“ZC-2024-07543”: {
“status”: “✅ Доставлен”,
“weight”: “45 кг”,
“type”: “Одежда”,
“steps”: [
(“✅”, “Принят на склад Иу”, “10 янв 2025”),
(“✅”, “Отправлен со склада”, “13 янв 2025”),
(“✅”, “Прошёл таможню Торугарт”, “19 янв 2025”),
(“✅”, “Прибыл на склад Бишкек”, “03 фев 2025”),
(“✅”, “Доставлен получателю”, “05 фев 2025”),
]
}
}

# Временное хранилище пользователей (в реальном боте — база данных)

users_db = {}
orders_db = {}

# ══════════════════════════════════════════════

# ГЕНЕРАЦИЯ ПЕРСОНАЛЬНОГО КОДА

# ══════════════════════════════════════════════

def gen_client_code(user_id: int) -> str:
chars = ‘ABCDEFGHJKLMNPQRSTUVWXYZ23456789’
h = abs(user_id * 2654435761) ^ (user_id >> 16)
code = ‘’
for _ in range(4):
code += chars[h % len(chars)]
h = (h // len(chars)) + (h * 31)
return f”{PERSONAL_CODE_PREFIX}-{code[:4]}”

# ══════════════════════════════════════════════

# КЛАВИАТУРЫ

# ══════════════════════════════════════════════

def main_keyboard():
keyboard = [
[KeyboardButton(“👤 Профиль”),    KeyboardButton(“📋 Адреса”),     KeyboardButton(“📦 Мои посылки”)],
[KeyboardButton(“📕 Инструкция”), KeyboardButton(“🚫 Запрещённые”), KeyboardButton(“⚙️ Поддержка”)],
[KeyboardButton(“✅ Добавить трек”)],
]
return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, persistent=True)

def cancel_keyboard():
return ReplyKeyboardMarkup(
[[KeyboardButton(“⬅️ Отмена”)]],
resize_keyboard=True
)

def packages_keyboard():
keyboard = [
[KeyboardButton(“🚛 В пути”)],
[KeyboardButton(“✅ В офисе”)],
[KeyboardButton(“⬅️ Назад”)],
]
return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# ══════════════════════════════════════════════

# /start — АВТОМАТИЧЕСКИЙ СТАРТ

# ══════════════════════════════════════════════

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
user = update.effective_user
uid = user.id

```
# Генерируем или получаем код
if uid not in users_db:
    users_db[uid] = {
        "code": gen_client_code(uid),
        "name": f"{user.first_name} {user.last_name or ''}".strip(),
        "phone": "",
        "address": "",
    }

u = users_db[uid]
code = u["code"]

# Приветственное сообщение с профилем
welcome_text = (
    f"👋 Добро пожаловать в *{COMPANY_NAME}*!\n\n"
    f"🪪 Персональный КОД: *{code}*\n"
    f"👤 ФИО: {u['name']}\n"
    f"📞 Номер: {u['phone'] or 'не указан'}\n"
    f"🏠 Адрес: {u['address'] or 'не указан'}\n\n"
    f"🇨🇳➡️🇰🇬 Доставка Китай → Бишкек\n"
    f"💰 *{PRICE_PER_KG}$ / кг* • ⏱ *{DELIVERY_DAYS} дней*"
)

inline_buttons = InlineKeyboardMarkup([
    [InlineKeyboardButton("✏️ Изменить профиль", callback_data="edit_profile")],
    [InlineKeyboardButton("🌐 Сменить язык 🇰🇬", callback_data="change_lang")],
    [InlineKeyboardButton("🌍 Войти в личный кабинет", url=WEBAPP_LINK)],
])

await update.message.reply_text(
    welcome_text,
    parse_mode="Markdown",
    reply_markup=inline_buttons
)

await update.message.reply_text(
    "👇 Выберите нужный раздел из меню:",
    reply_markup=main_keyboard()
)
```

# ══════════════════════════════════════════════

# ПРОФИЛЬ

# ══════════════════════════════════════════════

async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
uid = update.effective_user.id
if uid not in users_db:
await start(update, context)
return

```
u = users_db[uid]
text = (
    f"📋 *Ваш профиль*\n\n"
    f"🪪 Персональный КОД: *{u['code']}*\n"
    f"👤 ФИО: {u['name']}\n"
    f"📞 Номер: {u['phone'] or '—'}\n"
    f"🏠 Адрес: {u['address'] or '—'}\n\n"
    f"📍 ПВЗ: Суеркулова 4\n"
    f"📞 ПВЗ телефон: 996501777277\n"
    f"🕐 Часы работы: 11:00 - 19:00"
)

buttons = InlineKeyboardMarkup([
    [InlineKeyboardButton("✏️ Редактировать профиль", callback_data="edit_profile")],
    [InlineKeyboardButton("🌍 Войти в кабинет", url=WEBAPP_LINK)],
    [InlineKeyboardButton("🇰🇬 Тилди алмаштыруу", callback_data="change_lang")],
])

await update.message.reply_text(text, parse_mode="Markdown", reply_markup=buttons)
```

# ══════════════════════════════════════════════

# АДРЕСА СКЛАДОВ

# ══════════════════════════════════════════════

async def addresses(update: Update, context: ContextTypes.DEFAULT_TYPE):
uid = update.effective_user.id
code = users_db.get(uid, {}).get(“code”, “ZC-XXXX”)

```
await update.message.reply_text(
    f"📬 *Скопируйте ниже. Это адрес склада в Китае 🇨🇳:*",
    parse_mode="Markdown"
)

china_text = (
    f"广东省佛山市南海区里广路洲村工业区飞机场13-2号\n"
    f"收件人：VXMMM\n"
    f"电话：135 4510 0875\n"
    f"（TSL КАРГО）*{code}*\n\n"
    f"_Гуандун, Фошань, Наньхай_\n\n"
    f"⚠️ Обязательно напишите продавцу код *{code}* в примечании!"
)

await update.message.reply_text(china_text, parse_mode="Markdown")

bishkek_text = (
    f"🇰🇬 *Адрес выдачи в Бишкеке:*\n\n"
    f"📍 ПВЗ: Рухий Мурас\n"
    f"📞 Телефон: +996 505 600 542\n"
    f"🕐 Часы работы: 10:00 - 19:00\n"
    f"📍 Локация на Карте: [открыть](https://maps.google.com)"
)

await update.message.reply_text(
    bishkek_text,
    parse_mode="Markdown",
    reply_markup=main_keyboard()
)
```

# ══════════════════════════════════════════════

# МОИ ПОСЫЛКИ

# ══════════════════════════════════════════════

async def my_packages(update: Update, context: ContextTypes.DEFAULT_TYPE):
await update.message.reply_text(
“📦 *Мои посылки:*\n\nВыберите статус:”,
parse_mode=“Markdown”,
reply_markup=packages_keyboard()
)

async def packages_in_transit(update: Update, context: ContextTypes.DEFAULT_TYPE):
uid = update.effective_user.id
# В реальном боте — запрос к БД по user_id
text = (
“🚛 *Посылки в пути:*\n\n”
“📦 ZC-2024-08821 — Электроника, 12 кг\n”
“   └ 📍 Торугарт (таможня)\n\n”
“*Для детального отслеживания нажмите* ✅ Добавить трек”
)
await update.message.reply_text(text, parse_mode=“Markdown”, reply_markup=main_keyboard())

async def packages_in_office(update: Update, context: ContextTypes.DEFAULT_TYPE):
text = (
“✅ *Посылки в офисе (готовы к выдаче):*\n\n”
“📦 ZC-2024-07543 — Одежда, 45 кг\n”
“   └ ✅ Прибыл 03 фев 2025\n\n”
“📍 Адрес выдачи: Рухий Мурас\n”
“📞 +996 505 600 542”
)
await update.message.reply_text(text, parse_mode=“Markdown”, reply_markup=main_keyboard())

# ══════════════════════════════════════════════

# ДОБАВИТЬ ТРЕК — ДИАЛОГ

# ══════════════════════════════════════════════

async def add_track_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
await update.message.reply_text(
“✅ *Отправьте трек код для отслеживания*\n\n”
“❗ Можно разделить трек код через запятую\n”
“*(YT1111 носки, 67899876 куртка)*”,
parse_mode=“Markdown”,
reply_markup=cancel_keyboard()
)
return WAITING_TRACK

async def process_track(update: Update, context: ContextTypes.DEFAULT_TYPE):
text = update.message.text.strip()

```
if text == "⬅️ Отмена":
    await update.message.reply_text("Вы отменили последнюю команду", reply_markup=main_keyboard())
    return ConversationHandler.END

# Парсим треки через запятую
tracks = [t.strip() for t in text.replace(",", "\n").split("\n") if t.strip()]

result = ""
for track_raw in tracks:
    parts = track_raw.split(" ", 1)
    track_id = parts[0].upper()
    label = parts[1] if len(parts) > 1 else ""

    if track_id in packages_db:
        pkg = packages_db[track_id]
        steps_text = "\n".join(
            [f"   {icon} {title} — {date}" for icon, title, date in pkg["steps"]]
        )
        result += (
            f"\n📦 *{track_id}*{' (' + label + ')' if label else ''}\n"
            f"Статус: {pkg['status']}\n"
            f"Вес: {pkg['weight']} | {pkg['type']}\n\n"
            f"{steps_text}\n"
            f"{'─' * 30}\n"
        )
    else:
        result += f"\n❌ *{track_id}* — не найден. Проверьте трек-код.\n"

await update.message.reply_text(
    result or "❌ Трек-коды не найдены",
    parse_mode="Markdown",
    reply_markup=main_keyboard()
)
return ConversationHandler.END
```

# ══════════════════════════════════════════════

# ЗАПРЕЩЁННЫЕ ТОВАРЫ

# ══════════════════════════════════════════════

async def forbidden(update: Update, context: ContextTypes.DEFAULT_TYPE):
text = (
“🚫 *Список запрещённых к перевозке грузов:*\n\n”
“🔴 Лекарственные препараты, наркотические, психотропные вещества;\n”
“🔴 Легковоспламеняющиеся, взрывчатые, едкие вещества (фейерверки, различные виды оружия);\n”
“🔴 Жидкие, сыпучие вещества;\n”
“🔴 Электронные сигареты, жидкости для вейпов;\n”
“🔴 Острые, колющие, режущие предметы;\n\n”
“⚠️ Если у вас возникают сомнения относительно заказа какого-либо товара, “
“лучше напишите нам, и мы предоставим информацию о возможности его доставки.\n\n”
“❗ Эти товары запрещены для перевозки в соответствии с актами таможенных правил. “
“В случае заказа указанных товаров, налагается штраф в размере *10–50 тысяч*.”
)

```
buttons = InlineKeyboardMarkup([
    [InlineKeyboardButton("💬 Спросить менеджера", url=WHATSAPP_LINK)]
])

await update.message.reply_text(
    text, parse_mode="Markdown",
    reply_markup=buttons
)
await update.message.reply_text("👇 Меню:", reply_markup=main_keyboard())
```

# ══════════════════════════════════════════════

# ИНСТРУКЦИЯ

# ══════════════════════════════════════════════

async def instruction(update: Update, context: ContextTypes.DEFAULT_TYPE):
uid = update.effective_user.id
code = users_db.get(uid, {}).get(“code”, “ZC-XXXX”)

```
buttons = InlineKeyboardMarkup([
    [InlineKeyboardButton("Пиндуодуо", url="https://www.pinduoduo.com"),
     InlineKeyboardButton("Таобао", url="https://www.taobao.com")],
    [InlineKeyboardButton("1688", url="https://www.1688.com"),
     InlineKeyboardButton("JD", url="https://www.jd.com")],
])

await update.message.reply_text("📕 *Выберите маркетплейс:*", parse_mode="Markdown")

await update.message.reply_text(
    f"📖 *Инструкция по заказу:*\n\n"
    f"1️⃣ Выберите товар на маркетплейсе\n"
    f"2️⃣ При оформлении заказа укажите адрес склада в Китае\n"
    f"3️⃣ В примечании обязательно напишите ваш код: *{code}*\n"
    f"4️⃣ После оформления добавьте трек-код в бот (кнопка ✅ Добавить трек)\n"
    f"5️⃣ Мы уведомим вас о прибытии груза\n\n"
    f"❓ Остались вопросы? Напишите нам в WhatsApp!",
    parse_mode="Markdown",
    reply_markup=buttons
)
await update.message.reply_text("👇 Меню:", reply_markup=main_keyboard())
```

# ══════════════════════════════════════════════

# ПОДДЕРЖКА

# ══════════════════════════════════════════════

async def support(update: Update, context: ContextTypes.DEFAULT_TYPE):
buttons = InlineKeyboardMarkup([
[InlineKeyboardButton(“💬 WhatsApp +996 505 600 542”, url=WHATSAPP_LINK)],
[InlineKeyboardButton(“📸 Instagram @zero_cargo.313”, url=INSTAGRAM_LINK)],
])

```
await update.message.reply_text(
    "⚙️ *Поддержка Zero Cargo312*\n\n"
    "Свяжитесь с нами любым удобным способом:\n\n"
    "💬 WhatsApp: +996 505 600 542\n"
    "📸 Instagram: @zero_cargo.313\n"
    "🕐 Работаем: 09:00 - 20:00",
    parse_mode="Markdown",
    reply_markup=buttons
)
await update.message.reply_text("👇 Меню:", reply_markup=main_keyboard())
```

# ══════════════════════════════════════════════

# CALLBACK КНОПКИ (инлайн)

# ══════════════════════════════════════════════

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
query = update.callback_query
await query.answer()

```
if query.data == "edit_profile":
    await query.message.reply_text(
        "✏️ Для изменения профиля напишите /start\n"
        "Или свяжитесь с поддержкой.",
        reply_markup=main_keyboard()
    )
elif query.data == "change_lang":
    await query.message.reply_text(
        "🌐 Выберите язык / Тилди тандаңыз:",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru")],
            [InlineKeyboardButton("🇰🇬 Кыргызча", callback_data="lang_kg")],
        ])
    )
elif query.data == "lang_ru":
    await query.message.reply_text("✅ Язык изменён на Русский")
elif query.data == "lang_kg":
    await query.message.reply_text("✅ Тил кыргызчага өзгөртүлдү")
```

# ══════════════════════════════════════════════

# НАЗАД / ОТМЕНА

# ══════════════════════════════════════════════

async def go_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
await update.message.reply_text(“👇 Главное меню:”, reply_markup=main_keyboard())

# ══════════════════════════════════════════════

# НЕИЗВЕСТНЫЕ СООБЩЕНИЯ

# ══════════════════════════════════════════════

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
await update.message.reply_text(
“❓ Не понял команду. Используйте кнопки меню 👇”,
reply_markup=main_keyboard()
)

# ══════════════════════════════════════════════

# ЗАПУСК БОТА

# ══════════════════════════════════════════════

def main():
print(f”🚀 Запуск бота {COMPANY_NAME}…”)

```
app = Application.builder().token(BOT_TOKEN).build()

# Диалог добавления трека
track_conv = ConversationHandler(
    entry_points=[MessageHandler(filters.Regex("✅ Добавить трек"), add_track_start)],
    states={
        WAITING_TRACK: [MessageHandler(filters.TEXT, process_track)],
    },
    fallbacks=[MessageHandler(filters.Regex("⬅️ Отмена"), go_back)],
)

# Команды
app.add_handler(CommandHandler("start", start))

# Диалоги
app.add_handler(track_conv)

# Кнопки меню
app.add_handler(MessageHandler(filters.Regex("👤 Профиль"), profile))
app.add_handler(MessageHandler(filters.Regex("📋 Адреса"), addresses))
app.add_handler(MessageHandler(filters.Regex("📦 Мои посылки"), my_packages))
app.add_handler(MessageHandler(filters.Regex("🚛 В пути"), packages_in_transit))
app.add_handler(MessageHandler(filters.Regex("✅ В офисе"), packages_in_office))
app.add_handler(MessageHandler(filters.Regex("📕 Инструкция"), instruction))
app.add_handler(MessageHandler(filters.Regex("🚫 Запрещённые"), forbidden))
app.add_handler(MessageHandler(filters.Regex("⚙️ Поддержка"), support))
app.add_handler(MessageHandler(filters.Regex("⬅️ Назад|⬅️ Отмена"), go_back))

# Инлайн кнопки
app.add_handler(CallbackQueryHandler(callback_handler))

# Неизвестные сообщения
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, unknown))

print("✅ Бот запущен! Нажмите Ctrl+C для остановки.")
app.run_polling(drop_pending_updates=True)
```

if **name** == “**main**”:
main()
