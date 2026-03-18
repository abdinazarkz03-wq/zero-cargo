import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from database import Database

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8676654212:AAFtmReTMfPUrBMkVGSqc2XTUoBhmiwMmaU")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "1053328646"))
WEBAPP_URL = os.environ.get("WEBAPP_URL", "https://zerocargo312.onrender.com")
WHATSAPP_NUMBER = "996505600542"
SUPPORT_TELEGRAM = "https://t.me/zerocargo312_bot"

db = Database()

TEXTS = {
    "ru": {
        "welcome_new": "👋 Добро пожаловать в <b>ZERO CARGO</b> 🚛📦\n\nМы — карго компания, доставляем грузы из Китая в Бишкек 🇨🇳➡️🇰🇬\n\n💎 Цена: <b>2.8$ за кг</b>\n⏱ Сроки: <b>7–14 дней</b>\n📍 Адрес: ж/м Рухий Мурас\n\nПожалуйста, нажмите «Регистрация», чтобы продолжить.",
        "welcome_back": "👋 Добро пожаловать обратно, <b>{name}</b>!\n\n🔑 Ваш персональный код: <b>{code}</b>",
        "not_registered": "❌ Вы не зарегистрированы.\nПожалуйста, нажмите «📝 Регистрация», чтобы продолжить.",
        "reg_success": "✅ Регистрация успешно завершена!\n\n📋 Ваши данные:\n\n🔑 Персональный код: <b>{code}</b>\n👤 ФИО: <b>{name}</b>\n📱 Телефон: <b>{phone}</b>\n📍 ПВЗ: ж/м Рухий Мурас (Бишкек)\n\n📞 Менеджер: +996505600542",
        "my_code": "📋 Ваши данные:\n\n🔑 Персональный код: <b>{code}</b>\n👤 ФИО: <b>{name}</b>\n📱 Телефон: <b>{phone}</b>\n📍 ПВЗ: ж/м Рухий Мурас (Бишкек)\n\n📞 Менеджер: +996505600542",
        "profile": "👤 Ваш профиль:\n\n🔑 Персональный код: <b>{code}</b>\n👤 ФИО: <b>{name}</b>\n📱 Телефон: <b>{phone}</b>\n📍 ПВЗ: ж/м Рухий Мурас (Бишкек)\n🌐 Язык: Русский\n🗓 Дата регистрации: <b>{date}</b>",
        "address_china": "📍 <b>Адрес склада в Китае:</b>\n\n收件人: VXMMM\n电话: 13545100875\n地址: 广东省佛山市南海区里广路洲村工业区飞机场13-2号\n（TSL КАРГО）VXMMM <b>{code}</b>\n\n⚠️ <b>Важно!</b>\n• Скопируйте адрес полностью с вашим персональным кодом\n• Укажите ваш код вместо VXMMM при заказе",
        "address_bishkek": "📍 <b>Адрес ПВЗ в Бишкеке:</b>\n\nж/м Рухий Мурас\nБишкек, Кыргызстан",
        "forbidden": "🚫 <b>Запрещённые к перевозке грузы:</b>\n\n❌ Лекарственные препараты, наркотические и психотропные вещества\n❌ Легковоспламеняющиеся, взрывчатые и едкие вещества\n❌ Острые, колющие и режущие предметы\n❌ Предметы военного характера\n❌ Жидкие, сыпучие, порошковые и густые вещества\n❌ Электронные сигареты\n\n⚠️ ВНИМАНИЕ! За попытку отправки запрещённых товаров предусмотрен штраф от 10 000 до 50 000 сом!",
        "support": "💬 <b>Поддержка ZERO CARGO</b>\n\n📞 Telegram: +996505600542\n💚 WhatsApp: +996505600542\n\nНажмите на кнопку ниже, чтобы связаться с нами:",
        "instruction": "📖 <b>Инструкция по использованию:</b>\n\n1️⃣ Зарегистрируйтесь в боте и получите персональный код\n\n2️⃣ При заказе товара в Китае укажите адрес нашего склада:\n收件人: VXMMM\n电话: 13545100875\n地址: 广东省佛山市南海区里广路洲村工业区飞机场13-2号\n（TSL КАРГО）VXMMM <b>{code}</b>\n\n3️⃣ Ожидайте прибытия посылки на наш склад в Китае\n\n4️⃣ Отслеживайте статус в разделе «Мои посылки»\n\n5️⃣ Получите посылку в ПВЗ: ж/м Рухий Мурас\n\n⚠️ ВАЖНО:\n• Обязательно укажите ваш персональный код в адресе",
        "parcels_view": "📦 Просмотр ваших посылок и отслеживание по трек-номеру:",
        "lang_select": "🌐 Выберите язык / Тилди тандаңыз:",
        "btn_register": "📝📝 Регистрация",
        "btn_my_code": "📦 Мой код",
        "btn_parcels": "📮 Мои посылки",
        "btn_address": "📍 Адреса",
        "btn_instruction": "📖 Инструкция",
        "btn_profile": "👤 Профиль",
        "btn_forbidden": "🚫 Запрещённые грузы",
        "btn_support": "💬 Поддержка",
        "btn_language": "🌐 Язык",
        "btn_whatsapp": "💚 Написать в WhatsApp",
        "btn_telegram": "📱 Написать в Telegram",
    },
    "ky": {
        "welcome_new": "👋 <b>ZERO CARGO</b> га кош келиңиз 🚛📦\n\nБиз — Кытайдан Бишкекке жүк жеткирүүчү карго компания 🇨🇳➡️🇰🇬\n\n💎 Баасы: <b>1 кг үчүн 2.8$</b>\n⏱ Мөөнөт: <b>7–14 күн</b>\n📍 Дарек: Рухий Мурас ж/м\n\nУланта берүү үчүн «Катталуу» баскычын басыңыз.",
        "welcome_back": "👋 Кайра кош келиңиз, <b>{name}</b>!\n\n🔑 Жеке кодуңуз: <b>{code}</b>",
        "not_registered": "❌ Сиз катталган эмессиз.\nУланта берүү үчүн «📝 Катталуу» баскычын басыңыз.",
        "reg_success": "✅ Каттоо ийгиликтүү аяктады!\n\n📋 Сиздин маалыматтар:\n\n🔑 Жеке код: <b>{code}</b>\n👤 АТ: <b>{name}</b>\n📱 Телефон: <b>{phone}</b>\n📍 ПВЗ: Рухий Мурас ж/м (Бишкек)\n\n📞 Менеджер: +996505600542",
        "my_code": "📋 Сиздин маалыматтар:\n\n🔑 Жеке код: <b>{code}</b>\n👤 АТ: <b>{name}</b>\n📱 Телефон: <b>{phone}</b>\n📍 ПВЗ: Рухий Мурас ж/м (Бишкек)\n\n📞 Менеджер: +996505600542",
        "profile": "👤 Сиздин профиль:\n\n🔑 Жеке код: <b>{code}</b>\n👤 АТ: <b>{name}</b>\n📱 Телефон: <b>{phone}</b>\n📍 ПВЗ: Рухий Мурас ж/м (Бишкек)\n🌐 Тил: Кыргызча\n🗓 Катталган күн: <b>{date}</b>",
        "address_china": "📍 <b>Кытайдагы кампанын дареги:</b>\n\n收件人: VXMMM\n电话: 13545100875\n地址: 广东省佛山市南海区里广路洲村工业区飞机场13-2号\n（TSL КАРГО）VXMMM <b>{code}</b>\n\n⚠️ <b>Маанилүү!</b>\n• Даректи жеке кодуңуз менен толук көчүрүңүз",
        "address_bishkek": "📍 <b>Бишкектеги ПВЗ дареги:</b>\n\nРухий Мурас ж/м\nБишкек, Кыргызстан",
        "forbidden": "🚫 <b>Ташууга тыюу салынган жүктөр:</b>\n\n❌ Дарылар, баңги жана психотроптук заттар\n❌ От алгыч, жарылуучу жана коррозиялык заттар\n❌ Курч, сайгыч жана кескич буюмдар\n❌ Аскердик мүнөздөгү буюмдар\n❌ Суюк, сепкич, порошок жана калың заттар\n❌ Электрондук темекилер\n\n⚠️ ЭСКЕРТҮҮ! Тыюу салынган товарларды жөнөтүүгө аракет кылгандыгы үчүн 10 000ден 50 000 сомго чейин айып каралган!",
        "support": "💬 <b>ZERO CARGO колдоосу</b>\n\n📞 Telegram: +996505600542\n💚 WhatsApp: +996505600542\n\nБиз менен байланышуу үчүн төмөндөгү баскычты басыңыз:",
        "instruction": "📖 <b>Колдонуу боюнча нускама:</b>\n\n1️⃣ Ботко катталып, жеке код алыңыз\n\n2️⃣ Кытайдан товар заказ кылганда биздин кампанын дарегин көрсөтүңүз:\n收件人: VXMMM\n电话: 13545100875\n地址: 广东省佛山市南海区里广路洲村工业区飞机场13-2号\n（TSL КАРГО）VXMMM <b>{code}</b>\n\n3️⃣ Посылканын Кытайдагы кампага жеткирилишин күтүңүз\n\n4️⃣ «Менин посылкаларым» бөлүмүндө статусту байкаңыз\n\n5️⃣ Посылканы ПВЗден алыңыз: Рухий Мурас ж/м",
        "parcels_view": "📦 Посылкаларыңызды көрүү жана трек-номер боюнча издөө:",
        "lang_select": "🌐 Выберите язык / Тилди тандаңыз:",
        "btn_register": "📝📝 Катталуу",
        "btn_my_code": "📦 Менин кодум",
        "btn_parcels": "📮 Менин посылкаларым",
        "btn_address": "📍 Даректер",
        "btn_instruction": "📖 Нускама",
        "btn_profile": "👤 Профиль",
        "btn_forbidden": "🚫 Тыюу салынган жүктөр",
        "btn_support": "💬 Колдоо",
        "btn_language": "🌐 Тил",
        "btn_whatsapp": "💚 WhatsApp жазуу",
        "btn_telegram": "📱 Telegram жазуу",
    }
}
def get_lang(user_id):
    user = db.get_user(user_id)
    if user and user.get("language"):
        return user["language"]
    return "ru"

def t(user_id, key):
    lang = get_lang(user_id)
    return TEXTS[lang].get(key, TEXTS["ru"].get(key, key))

def get_main_keyboard(user_id):
    lang = get_lang(user_id)
    tx = TEXTS[lang]
    keyboard = [
        [KeyboardButton(tx["btn_my_code"]), KeyboardButton(tx["btn_parcels"])],
        [KeyboardButton(tx["btn_address"]), KeyboardButton(tx["btn_instruction"])],
        [KeyboardButton(tx["btn_profile"]), KeyboardButton(tx["btn_forbidden"])],
        [KeyboardButton(tx["btn_support"]), KeyboardButton(tx["btn_language"])],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_register_keyboard(user_id):
    lang = get_lang(user_id)
    webapp_url = f"{WEBAPP_URL}/register"
    keyboard = [[KeyboardButton("📝📝 Регистрация" if lang == "ru" else "📝📝 Катталуу",
                                web_app=WebAppInfo(url=webapp_url))]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_parcels_keyboard(user_id):
    webapp_url = f"{WEBAPP_URL}/parcels?user_id={user_id}"
    lang = get_lang(user_id)
    text = "🔍 Открыть мои посылки" if lang == "ru" else "🔍 Менин посылкаларымды ачуу"
    keyboard = [[InlineKeyboardButton(text, web_app=WebAppInfo(url=webapp_url))]]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = db.get_user(user_id)
    if user:
        lang = user.get("language", "ru")
        tx = TEXTS[lang]
        msg = tx["welcome_back"].format(name=user["full_name"], code=user["client_code"])
        await update.message.reply_text(msg, parse_mode="HTML", reply_markup=get_main_keyboard(user_id))
    else:
        msg = TEXTS["ru"]["welcome_new"]
        await update.message.reply_text(msg, parse_mode="HTML", reply_markup=get_register_keyboard(user_id))

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    lang = get_lang(user_id)
    tx = TEXTS[lang]
    tx_ru = TEXTS["ru"]
    tx_ky = TEXTS["ky"]

    all_btn_my_code = [tx_ru["btn_my_code"], tx_ky["btn_my_code"]]
    all_btn_parcels = [tx_ru["btn_parcels"], tx_ky["btn_parcels"]]
    all_btn_address = [tx_ru["btn_address"], tx_ky["btn_address"]]
    all_btn_instruction = [tx_ru["btn_instruction"], tx_ky["btn_instruction"]]
    all_btn_profile = [tx_ru["btn_profile"], tx_ky["btn_profile"]]
    all_btn_forbidden = [tx_ru["btn_forbidden"], tx_ky["btn_forbidden"]]
    all_btn_support = [tx_ru["btn_support"], tx_ky["btn_support"]]
    all_btn_language = [tx_ru["btn_language"], tx_ky["btn_language"]]
    all_btn_register = [tx_ru["btn_register"], tx_ky["btn_register"]]

    user = db.get_user(user_id)

    if text in all_btn_register:
        webapp_url = f"{WEBAPP_URL}/register"
        keyboard = [[InlineKeyboardButton(
            "📝 Открыть форму регистрации" if lang == "ru" else "📝 Каттоо формасын ачуу",
            web_app=WebAppInfo(url=webapp_url))]]
        await update.message.reply_text(
            "📝 Нажмите кнопку ниже для регистрации:" if lang == "ru" else "📝 Каттоо үчүн төмөндөгү баскычты басыңыз:",
            reply_markup=InlineKeyboardMarkup(keyboard))
        return

    if not user and text not in all_btn_language:
        await update.message.reply_text(tx["not_registered"], parse_mode="HTML",
                                        reply_markup=get_register_keyboard(user_id))
        return

    if text in all_btn_my_code:
        msg = tx["my_code"].format(code=user["client_code"], name=user["full_name"], phone=user["phone"])
        await update.message.reply_text(msg, parse_mode="HTML", reply_markup=get_main_keyboard(user_id))

    elif text in all_btn_parcels:
        await update.message.reply_text(tx["parcels_view"], parse_mode="HTML",
                                        reply_markup=get_parcels_keyboard(user_id))

    elif text in all_btn_address:
        china_msg = tx["address_china"].format(code=user["client_code"])
        await update.message.reply_text(china_msg, parse_mode="HTML")
        await update.message.reply_text(tx["address_bishkek"], parse_mode="HTML",
                                        reply_markup=get_main_keyboard(user_id))

    elif text in all_btn_instruction:
        code = user["client_code"] if user else "ВАШ КОД"
        await update.message.reply_text(tx["instruction"].format(code=code), parse_mode="HTML",
                                        reply_markup=get_main_keyboard(user_id))

    elif text in all_btn_profile:
        msg = tx["profile"].format(code=user["client_code"], name=user["full_name"],
                                   phone=user["phone"], date=user["created_at"][:10])
        await update.message.reply_text(msg, parse_mode="HTML", reply_markup=get_main_keyboard(user_id))

    elif text in all_btn_forbidden:
        await update.message.reply_text(tx["forbidden"], parse_mode="HTML",
                                        reply_markup=get_main_keyboard(user_id))

    elif text in all_btn_support:
        keyboard = [
            [InlineKeyboardButton(tx["btn_whatsapp"], url=f"https://wa.me/{WHATSAPP_NUMBER}")],
            [InlineKeyboardButton(tx["btn_telegram"], url=SUPPORT_TELEGRAM)],
        ]
        await update.message.reply_text(tx["support"], parse_mode="HTML",
                                        reply_markup=InlineKeyboardMarkup(keyboard))

    elif text in all_btn_language:
        keyboard = [[
            InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru"),
            InlineKeyboardButton("🇰🇬 Кыргызча", callback_data="lang_ky")
        ]]
        await update.message.reply_text(TEXTS["ru"]["lang_select"],
                                        reply_markup=InlineKeyboardMarkup(keyboard))

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    data = query.data
    await query.answer()
    if data.startswith("lang_"):
        new_lang = data.split("_")[1]
        db.update_language(user_id, new_lang)
        msg = "✅ Язык изменён на Русский" if new_lang == "ru" else "✅ Тил Кыргызчага өзгөртүлдү"
        await query.edit_message_text(msg)
        user = db.get_user(user_id)
        if user:
            await context.bot.send_message(user_id, "👇", reply_markup=get_main_keyboard(user_id))

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    webapp_url = f"{WEBAPP_URL}/admin"
    keyboard = [[InlineKeyboardButton("🔧 Открыть Админ-панель", web_app=WebAppInfo(url=webapp_url))]]
    await update.message.reply_text("🔧 <b>Админ-панель ZERO CARGO</b>", parse_mode="HTML",
                                    reply_markup=InlineKeyboardMarkup(keyboard))

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin_command))
    app.add_handler(CallbackQueryHandler(callback_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    port = int(os.environ.get("PORT", 8443))
    webhook_url = os.environ.get("WEBHOOK_URL", "")
    if webhook_url:
        app.run_webhook(listen="0.0.0.0", port=port, url_path=BOT_TOKEN,
                        webhook_url=f"{webhook_url}/{BOT_TOKEN}")
    else:
        app.run_polling()

if __name__ == "__main__":
    main()
