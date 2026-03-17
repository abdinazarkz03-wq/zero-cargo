import logging
import os
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("BOT_TOKEN", "8676654212:AAFtmReTMfPUrBMkVGSqc2XTUoBhmiwMmaU")
WEBAPP_URL = os.getenv("WEBAPP_URL", "https://zerocargo-webapp.onrender.com")
ADMIN_ID = int(os.getenv("ADMIN_ID", "1053328646"))

def get_user(telegram_id):
    try:
        r = requests.get(f"{WEBAPP_URL}/api/user?telegram_id={telegram_id}", timeout=10)
        d = r.json()
        return d if d.get("found") else None
    except Exception as e:
        logger.error(f"get_user error: {e}")
        return None

def get_lang(user):
    if user and user.get("language"):
        return user["language"]
    return "ru"

TEXTS = {
    "ru": {
        "welcome_new": (
            "🚛 Добро пожаловать в <b>ZERO CARGO</b>!\n\n"
            "Мы — карго компания, которая помогает быстро и надёжно доставлять грузы из Китая в Бишкек 🇨🇳➡️🇰🇬\n\n"
            "💎 Доставка Китай — Бишкек\n"
            "💰 Всего <b>2.8$ за кг</b>\n"
            "⏱ Сроки: <b>7–14 дней</b>\n"
            "📍 Адрес: ж/м Рухий Мурас\n\n"
            "Вы не зарегистрированы. Нажмите <b>«Регистрация»</b> чтобы продолжить."
        ),
        "welcome_back": "👋 Добро пожаловать обратно, <b>{name}</b>!\n\n🔑 Ваш персональный код: <b>{code}</b>",
        "reg_btn": "📝 Регистрация",
        "mycode_btn": "📦 Мой код",
        "parcels_btn": "🚨 Мои посылки",
        "address_btn": "📍 Адреса",
        "instruction_btn": "📖 Инструкция",
        "profile_btn": "👤 Профиль",
        "banned_btn": "🚫 Запрещённые грузы",
        "support_btn": "💬 Поддержка",
        "lang_btn": "🌐 Язык",
        "mycode_text": (
            "📋 Ваши данные:\n\n"
            "🔑 Персональный код: <b>{code}</b>\n"
            "👤 ФИО: <b>{name}</b>\n"
            "📱 Телефон: <b>{phone}</b>\n"
            "📍 ПВЗ: ж/м Рухий Мурас\n"
            "📞 Менеджер: <b>+996505600542</b>"
        ),
        "profile_text": (
            "👤 Ваш профиль:\n\n"
            "🔑 Персональный код: <b>{code}</b>\n"
            "👤 ФИО: <b>{name}</b>\n"
            "📱 Телефон: <b>{phone}</b>\n"
            "📍 ПВЗ: ж/м Рухий Мурас\n"
            "🌐 Язык: Русский\n"
            "📅 Дата регистрации: <b>{date}</b>"
        ),
        "address_text": (
            "📦 Адрес склада в Китае:\n\n"
            "收件人：VXMMM\n"
            "电话：13545100875\n"
            "广东省佛山市南海区里广路洲村工业区飞机场13-2号\n"
            "（TSL КАРГО）VXMMM <b>{code}</b>\n\n"
            "⚠️ <b>ВАЖНО:</b> Обязательно укажите ваш персональный код в адресе!"
        ),
        "instruction_text": (
            "📖 <b>Инструкция по отправке посылок:</b>\n\n"
            "💰 <b>Тарифы:</b>\n"
            "• 2.8$ за кг из Китая\n"
            "• Срок доставки: 7–14 дней\n\n"
            "📋 <b>Пошаговая инструкция:</b>\n\n"
            "1️⃣ Зарегистрируйтесь и получите персональный код\n"
            "2️⃣ При заказе товара укажите адрес склада в Китае\n"
            "3️⃣ <b>Обязательно</b> укажите ваш код в адресе\n"
            "4️⃣ Отслеживайте посылку через «Мои посылки»\n"
            "5️⃣ Получите посылку в ПВЗ: ж/м Рухий Мурас\n\n"
            "⚠️ <b>ВАЖНО:</b> Обязательно укажите персональный код в адресе!"
        ),
        "banned_text": (
            "🚫 <b>Запрещённые к перевозке грузы:</b>\n\n"
            "❌ Лекарственные препараты, наркотические и психотропные вещества\n"
            "❌ Легковоспламеняющиеся, взрывчатые и едкие вещества\n"
            "❌ Острые, колющие и режущие предметы\n"
            "❌ Оружие и имитация оружия\n"
            "❌ Предметы военного характера\n"
            "❌ Жидкие, сыпучие, порошковые и густые вещества\n"
            "❌ Электронные сигареты\n\n"
            "⚠️ <b>ВНИМАНИЕ!</b> За попытку отправки запрещённых товаров предусмотрен штраф от 10 000 до 50 000 сом!"
        ),
        "support_text": (
            "💬 <b>Поддержка ZERO CARGO</b>\n\n"
            "📱 WhatsApp: <b>+996505600542</b>\n"
            "📱 Telegram: <b>@zero_cargo.312</b>\n\n"
            "Нажмите на кнопку ниже, чтобы связаться с нами:"
        ),
        "not_registered": "❌ Вы не зарегистрированы. Нажмите «Регистрация».",
        "parcels_open": "📦 Просмотр ваших посылок и отслеживание по трек-номеру:",
        "open_parcels_btn": "🔍 Открыть мои посылки",
    },
    "kg": {
        "welcome_new": (
            "🚛 <b>ZERO CARGO</b>'го кош келиңиз!\n\n"
            "Биз — Кытайдан Бишкекке жүктөрдү тез жана ишенимдүү жеткизүүгө жардам берген карго компаниябыз 🇨🇳➡️🇰🇬\n\n"
            "💎 Кытай — Бишкек жеткизүү\n"
            "💰 Болгону <b>2.8$ кг үчүн</b>\n"
            "⏱ Мөөнөт: <b>7–14 күн</b>\n"
            "📍 Дарек: Рухий Мурас ж/м\n\n"
            "Сиз катталган эмессиз. Улантуу үчүн <b>«Катталуу»</b> баскычын басыңыз."
        ),
        "welcome_back": "👋 Кайра кош келиңиз, <b>{name}</b>!\n\n🔑 Сиздин жеке кодуңуз: <b>{code}</b>",
        "reg_btn": "📝 Катталуу",
        "mycode_btn": "📦 Менин кодум",
        "parcels_btn": "🚨 Менин посылкаларым",
        "address_btn": "📍 Даректер",
        "instruction_btn": "📖 Көрсөтмө",
        "profile_btn": "👤 Профиль",
        "banned_btn": "🚫 Тыюу салынган жүктөр",
        "support_btn": "💬 Колдоо",
        "lang_btn": "🌐 Тил",
        "mycode_text": (
            "📋 Сиздин маалыматтарыңыз:\n\n"
            "🔑 Жеке код: <b>{code}</b>\n"
            "👤 ФАА: <b>{name}</b>\n"
            "📱 Телефон: <b>{phone}</b>\n"
            "📍 ПВЗ: Рухий Мурас ж/м\n"
            "📞 Менеджер: <b>+996505600542</b>"
        ),
        "profile_text": (
            "👤 Сиздин профилиңиз:\n\n"
            "🔑 Жеке код: <b>{code}</b>\n"
            "👤 ФАА: <b>{name}</b>\n"
            "📱 Телефон: <b>{phone}</b>\n"
            "📍 ПВЗ: Рухий Мурас ж/м\n"
            "🌐 Тил: Кыргызча\n"
            "📅 Катталган күн: <b>{date}</b>"
        ),
        "address_text": (
            "📦 Кытайдагы кампа дареги:\n\n"
            "收件人：VXMMM\n"
            "电话：13545100875\n"
            "广东省佛山市南海区里广路洲村工业区飞机场13-2号\n"
            "（TSL КАРГО）VXMMM <b>{code}</b>\n\n"
            "⚠️ <b>МААНИЛҮҮ:</b> Даректе өзүңүздүн жеке кодуңузду көрсөтүүнү унутпаңыз!"
        ),
        "instruction_text": (
            "📖 <b>Посылка жөнөтүү боюнча көрсөтмө:</b>\n\n"
            "💰 <b>Тарифтер:</b>\n"
            "• Кытайдан кг үчүн 2.8$\n"
            "• Жеткизүү мөөнөтү: 7–14 күн\n\n"
            "📋 <b>Кадам-кадам нускамасы:</b>\n\n"
            "1️⃣ Катталып, жеке кодуңузду алыңыз\n"
            "2️⃣ Товар заказ кылып, Кытайдагы кампанын дарегин көрсөтүңүз\n"
            "3️⃣ Даректе кодуңузду <b>милдеттүү түрдө</b> көрсөтүңүз\n"
            "4️⃣ «Менин посылкаларым» аркылуу посылканы кадарлаңыз\n"
            "5️⃣ Посылканы ПВЗдан алыңыз: Рухий Мурас ж/м"
        ),
        "banned_text": (
            "🚫 <b>Ташууга тыюу салынган жүктөр:</b>\n\n"
            "❌ Дары-дармектер, баңги жана психотроптук заттар\n"
            "❌ Тез жанган, жарылуучу жана коррозиялык заттар\n"
            "❌ Курч, бычкак жана кесүүчү предметтер\n"
            "❌ Курал жана курал имитациясы\n"
            "❌ Аскердик мүнөздөгү буюмдар\n"
            "❌ Суюк, сүрүлүүчү, порошок жана калың заттар\n"
            "❌ Электрондук темекилер\n\n"
            "⚠️ <b>ЭСКЕРТҮҮ!</b> Тыюу салынган товарларды жөнөтүүгө аракет кылгандыгы үчүн 10 000ден 50 000 сомго чейин айып салынат!"
        ),
        "support_text": (
            "💬 <b>ZERO CARGO колдоосу</b>\n\n"
            "📱 WhatsApp: <b>+996505600542</b>\n"
            "📱 Telegram: <b>@zero_cargo.312</b>\n\n"
            "Биз менен байланышуу үчүн төмөндөгү баскычты басыңыз:"
        ),
        "not_registered": "❌ Сиз катталган эмессиз. «Катталуу» баскычын басыңыз.",
        "parcels_open": "📦 Посылкаларыңызды көрүү жана трек-номер боюнча кадарлоо:",
        "open_parcels_btn": "🔍 Менин посылкаларымды ачуу",
    }
}

def tx(user, key, **kwargs):
    lang = get_lang(user)
    text = TEXTS[lang].get(key, TEXTS["ru"].get(key, key))
    return text.format(**kwargs) if kwargs else text

def get_main_keyboard(user, registered=True):
    lang = get_lang(user)
    t = TEXTS[lang]
    if not registered:
        return ReplyKeyboardMarkup([[KeyboardButton(t["reg_btn"])]], resize_keyboard=True)
    return ReplyKeyboardMarkup([
        [KeyboardButton(t["mycode_btn"]), KeyboardButton(t["parcels_btn"])],
        [KeyboardButton(t["address_btn"]), KeyboardButton(t["instruction_btn"])],
        [KeyboardButton(t["profile_btn"]), KeyboardButton(t["banned_btn"])],
        [KeyboardButton(t["support_btn"]), KeyboardButton(t["lang_btn"])],
    ], resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = get_user(user_id)
    if user:
        await update.message.reply_text(
            tx(user, "welcome_back", name=user["full_name"], code=user["client_code"]),
            parse_mode="HTML", reply_markup=get_main_keyboard(user)
        )
    else:
        await update.message.reply_text(
            tx(None, "welcome_new"), parse_mode="HTML",
            reply_markup=get_main_keyboard(None, registered=False)
        )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    user = get_user(user_id)
    ru = TEXTS["ru"]
    kg = TEXTS["kg"]

    if text in [ru["reg_btn"], kg["reg_btn"]]:
        webapp_url = f"{WEBAPP_URL}/register?user_id={user_id}"
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("📝 Регистрация", web_app=WebAppInfo(url=webapp_url))]])
        await update.message.reply_text("Нажмите кнопку ниже для регистрации:", reply_markup=keyboard)
        return

    if text in [ru["mycode_btn"], kg["mycode_btn"]]:
        if not user:
            await update.message.reply_text(tx(user, "not_registered"))
            return
        await update.message.reply_text(
            tx(user, "mycode_text", code=user["client_code"], name=user["full_name"], phone=user["phone"]),
            parse_mode="HTML"
        )
    elif text in [ru["parcels_btn"], kg["parcels_btn"]]:
        if not user:
            await update.message.reply_text(tx(user, "not_registered"))
            return
        webapp_url = f"{WEBAPP_URL}/parcels?user_id={user_id}&code={user['client_code']}"
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(tx(user, "open_parcels_btn"), web_app=WebAppInfo(url=webapp_url))]])
        await update.message.reply_text(tx(user, "parcels_open"), reply_markup=keyboard, parse_mode="HTML")
    elif text in [ru["address_btn"], kg["address_btn"]]:
        if not user:
            await update.message.reply_text(tx(user, "not_registered"))
            return
        await update.message.reply_text(tx(user, "address_text", code=user["client_code"]), parse_mode="HTML")
    elif text in [ru["instruction_btn"], kg["instruction_btn"]]:
        await update.message.reply_text(tx(user, "instruction_text"), parse_mode="HTML")
    elif text in [ru["profile_btn"], kg["profile_btn"]]:
        if not user:
            await update.message.reply_text(tx(user, "not_registered"))
            return
        await update.message.reply_text(
            tx(user, "profile_text", code=user["client_code"], name=user["full_name"],
               phone=user["phone"], date=user.get("created_at", "—")[:10]),
            parse_mode="HTML"
        )
    elif text in [ru["banned_btn"], kg["banned_btn"]]:
        await update.message.reply_text(tx(user, "banned_text"), parse_mode="HTML")
    elif text in [ru["support_btn"], kg["support_btn"]]:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("💚 Написать в WhatsApp", url="https://wa.me/996505600542")],
            [InlineKeyboardButton("📱 Написать в Telegram", url="https://t.me/zero_cargo312")],
        ])
        await update.message.reply_text(tx(user, "support_text"), reply_markup=keyboard, parse_mode="HTML")
    elif text in [ru["lang_btn"], kg["lang_btn"]]:
        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru"),
            InlineKeyboardButton("🇰🇬 Кыргызча", callback_data="lang_kg"),
        ]])
        await update.message.reply_text("🌐 Выберите язык / Тилди тандаңыз:", reply_markup=keyboard)
    else:
        await start(update, context)

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    lang = "ru" if query.data == "lang_ru" else "kg"
    try:
        requests.post(f"{WEBAPP_URL}/api/update-language",
                      json={"telegram_id": user_id, "language": lang}, timeout=5)
    except Exception as e:
        logger.error(f"update lang error: {e}")
    msg = "✅ Язык изменён на Русский" if lang == "ru" else "✅ Тил кыргызчага өзгөртүлдү"
    await query.edit_message_text(msg)
    user = get_user(user_id)
    if user:
        await context.bot.send_message(
            user_id,
            tx(user, "welcome_back", name=user["full_name"], code=user["client_code"]),
            parse_mode="HTML", reply_markup=get_main_keyboard(user)
        )

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(callback_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    logger.info("Zero Cargo Bot started!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
