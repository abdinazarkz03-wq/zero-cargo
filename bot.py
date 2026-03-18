import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from database import Database

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8676654212:AAFtmReTMfPUrBMkVGSqc2XTUoBhmiwMmaU")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "1053328646"))
WEBAPP_URL = os.environ.get("WEBAPP_URL", "https://zerocargo-bot.onrender.com")
WHATSAPP = "996505600542"

db = Database()

RU = {
    "welcome_new": "👋 Добро пожаловать в <b>ZERO CARGO</b> 🚛📦\n\n💎 Цена: <b>2.8$ за кг</b>\n⏱ Сроки: <b>7–14 дней</b>\n📍 Адрес: ж/м Рухий Мурас\n\nНажмите «Регистрация» чтобы продолжить.",
    "welcome_back": "👋 Добро пожаловать обратно, <b>{name}</b>!\n🔑 Ваш код: <b>{code}</b>",
    "not_reg": "❌ Вы не зарегистрированы. Нажмите «Регистрация».",
    "my_code": "🔑 Код: <b>{code}</b>\n👤 ФИО: <b>{name}</b>\n📱 Тел: <b>{phone}</b>\n📍 ПВЗ: ж/м Рухий Мурас\n📞 Менеджер: +996505600542",
    "profile": "👤 Профиль:\n🔑 Код: <b>{code}</b>\n👤 ФИО: <b>{name}</b>\n📱 Тел: <b>{phone}</b>\n📍 ПВЗ: ж/м Рухий Мурас\n🗓 Регистрация: <b>{date}</b>",
    "china": "📍 <b>Адрес склада в Китае:</b>\n\n收件人: VXMMM\n电话: 13545100875\n地址: 广东省佛山市南海区里广路洲村工业区飞机场13-2号\n（TSL КАРГО）VXMMM <b>{code}</b>\n\n⚠️ Укажите ваш код вместо VXMMM",
    "bishkek": "📍 <b>ПВЗ в Бишкеке:</b>\nж/м Рухий Мурас, Бишкек",
    "forbidden": "🚫 <b>Запрещённые грузы:</b>\n❌ Лекарства и наркотики\n❌ Взрывчатые вещества\n❌ Острые предметы\n❌ Военные предметы\n❌ Жидкости и порошки\n❌ Электронные сигареты\n\n⚠️ Штраф 10 000 – 50 000 сом!",
    "support": "💬 <b>Поддержка ZERO CARGO</b>\n📞 +996505600542",
    "instruction": "📖 <b>Инструкция:</b>\n\n1️⃣ Зарегистрируйтесь и получите код\n2️⃣ При заказе укажите адрес склада в Китае со своим кодом\n3️⃣ Ожидайте посылку\n4️⃣ Отслеживайте в «Мои посылки»\n5️⃣ Получите в ж/м Рухий Мурас",
    "parcels": "📦 Нажмите кнопку для просмотра посылок:",
    "lang": "🌐 Выберите язык:",
}

KY = {
    "welcome_new": "👋 <b>ZERO CARGO</b> га кош келиңиз 🚛📦\n\n💎 Баасы: <b>2.8$</b>\n⏱ Мөөнөт: <b>7–14 күн</b>\n📍 Дарек: Рухий Мурас\n\n«Катталуу» баскычын басыңыз.",
    "welcome_back": "👋 Кайра кош келиңиз, <b>{name}</b>!\n🔑 Кодуңуз: <b>{code}</b>",
    "not_reg": "❌ Катталган эмессиз. «Катталуу» баскычын басыңыз.",
    "my_code": "🔑 Код: <b>{code}</b>\n👤 АТ: <b>{name}</b>\n📱 Тел: <b>{phone}</b>\n📍 ПВЗ: Рухий Мурас\n📞 Менеджер: +996505600542",
    "profile": "👤 Профиль:\n🔑 Код: <b>{code}</b>\n👤 АТ: <b>{name}</b>\n📱 Тел: <b>{phone}</b>\n📍 ПВЗ: Рухий Мурас\n🗓 Катталган: <b>{date}</b>",
    "china": "📍 <b>Кытайдагы кампа:</b>\n\n收件人: VXMMM\n电话: 13545100875\n地址: 广东省佛山市南海区里广路洲村工业区飞机场13-2号\n（TSL КАРГО）VXMMM <b>{code}</b>",
    "bishkek": "📍 <b>ПВЗ Бишкек:</b>\nРухий Мурас ж/м",
    "forbidden": "🚫 <b>Тыюу салынган жүктөр:</b>\n❌ Дарылар\n❌ Жарылуучу заттар\n❌ Курч буюмдар\n❌ Аскердик буюмдар\n❌ Суюктуктар\n❌ Электрондук темекилер\n\n⚠️ Айып 10 000 – 50 000 сом!",
    "support": "💬 <b>ZERO CARGO колдоосу</b>\n📞 +996505600542",
    "instruction": "📖 <b>Нускама:</b>\n\n1️⃣ Катталып код алыңыз\n2️⃣ Кытайдан заказда кампанын дарегин көрсөтүңүз\n3️⃣ Посылканы күтүңүз\n4️⃣ «Менин посылкаларым» бөлүмүнөн байкаңыз\n5️⃣ Рухий Мурасдан алыңыз",
    "parcels": "📦 Посылкаларды көрүү үчүн басыңыз:",
    "lang": "🌐 Тилди тандаңыз:",
}

def lang(uid):
    u = db.get_user(uid)
    return "ky" if u and u.get("language") == "ky" else "ru"

def tx(uid):
    return KY if lang(uid) == "ky" else RU

def main_kb(uid):
    t = tx(uid)
    if lang(uid) == "ru":
        kb = [
            [KeyboardButton("📦 Мой код"), KeyboardButton("📮 Мои посылки")],
            [KeyboardButton("📍 Адреса"), KeyboardButton("📖 Инструкция")],
            [KeyboardButton("👤 Профиль"), KeyboardButton("🚫 Запрещённые грузы")],
            [KeyboardButton("💬 Поддержка"), KeyboardButton("🌐 Язык")],
        ]
    else:
        kb = [
            [KeyboardButton("📦 Менин кодум"), KeyboardButton("📮 Менин посылкаларым")],
            [KeyboardButton("📍 Даректер"), KeyboardButton("📖 Нускама")],
            [KeyboardButton("👤 Профиль"), KeyboardButton("🚫 Тыюу салынган жүктөр")],
            [KeyboardButton("💬 Колдоо"), KeyboardButton("🌐 Тил")],
        ]
    return ReplyKeyboardMarkup(kb, resize_keyboard=True)

def reg_kb(uid):
    l = lang(uid)
    label = "📝 Регистрация" if l == "ru" else "📝 Катталуу"
    kb = [[KeyboardButton(label, web_app=WebAppInfo(url=f"{WEBAPP_URL}/register"))]]
    return ReplyKeyboardMarkup(kb, resize_keyboard=True)

async def start(update, context):
    uid = update.effective_user.id
    u = db.get_user(uid)
    if u:
        t = tx(uid)
        await update.message.reply_text(
            t["welcome_back"].format(name=u["full_name"], code=u["client_code"]),
            parse_mode="HTML", reply_markup=main_kb(uid))
    else:
        await update.message.reply_text(
            RU["welcome_new"], parse_mode="HTML", reply_markup=reg_kb(uid))

async def msg(update, context):
    uid = update.effective_user.id
    text = update.message.text
    u = db.get_user(uid)
    t = tx(uid)
    l = lang(uid)

    reg_btns = ["📝 Регистрация", "📝 Катталуу"]
    lang_btns = ["🌐 Язык", "🌐 Тил"]
    code_btns = ["📦 Мой код", "📦 Менин кодум"]
    parcel_btns = ["📮 Мои посылки", "📮 Менин посылкаларым"]
    addr_btns = ["📍 Адреса", "📍 Даректер"]
    instr_btns = ["📖 Инструкция", "📖 Нускама"]
    prof_btns = ["👤 Профиль"]
    forbid_btns = ["🚫 Запрещённые грузы", "🚫 Тыюу салынган жүктөр"]
    support_btns = ["💬 Поддержка", "💬 Колдоо"]

    if text in reg_btns:
        kb = [[InlineKeyboardButton("📝 Открыть регистрацию" if l=="ru" else "📝 Каттоону ачуу",
               web_app=WebAppInfo(url=f"{WEBAPP_URL}/register"))]]
        await update.message.reply_text(
            "Нажмите:" if l=="ru" else "Басыңыз:",
            reply_markup=InlineKeyboardMarkup(kb))
        return

    if text in lang_btns:
        kb = [[InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru"),
               InlineKeyboardButton("🇰🇬 Кыргызча", callback_data="lang_ky")]]
        await update.message.reply_text(RU["lang"], reply_markup=InlineKeyboardMarkup(kb))
        return

    if not u and text not in lang_btns:
        await update.message.reply_text(RU["not_reg"], parse_mode="HTML", reply_markup=reg_kb(uid))
        return

    if text in code_btns:
        await update.message.reply_text(
            t["my_code"].format(code=u["client_code"], name=u["full_name"], phone=u["phone"]),
            parse_mode="HTML", reply_markup=main_kb(uid))

    elif text in parcel_btns:
        kb = [[InlineKeyboardButton("🔍 Открыть" if l=="ru" else "🔍 Ачуу",
               web_app=WebAppInfo(url=f"{WEBAPP_URL}/parcels?user_id={uid}"))]]
        await update.message.reply_text(t["parcels"], reply_markup=InlineKeyboardMarkup(kb))

    elif text in addr_btns:
        await update.message.reply_text(
            t["china"].format(code=u["client_code"]), parse_mode="HTML")
        await update.message.reply_text(t["bishkek"], parse_mode="HTML", reply_markup=main_kb(uid))

    elif text in instr_btns:
        await update.message.reply_text(
            t["instruction"], parse_mode="HTML", reply_markup=main_kb(uid))

    elif text in prof_btns:
        await update.message.reply_text(
            t["profile"].format(code=u["client_code"], name=u["full_name"],
                                phone=u["phone"], date=u["created_at"][:10]),
            parse_mode="HTML", reply_markup=main_kb(uid))

    elif text in forbid_btns:
        await update.message.reply_text(t["forbidden"], parse_mode="HTML", reply_markup=main_kb(uid))

    elif text in support_btns:
        kb = [[InlineKeyboardButton("💚 WhatsApp", url=f"https://wa.me/{WHATSAPP}")],
              [InlineKeyboardButton("📱 Telegram", url=f"https://t.me/zerocargo312_bot")]]
        await update.message.reply_text(t["support"], parse_mode="HTML",
                                        reply_markup=InlineKeyboardMarkup(kb))

async def cb(update, context):
    q = update.callback_query
    uid = q.from_user.id
    await q.answer()
    if q.data == "lang_ru":
        db.update_language(uid, "ru")
        await q.edit_message_text("✅ Язык: Русский")
    elif q.data == "lang_ky":
        db.update_language(uid, "ky")
        await q.edit_message_text("✅ Тил: Кыргызча")
    u = db.get_user(uid)
    if u:
        await context.bot.send_message(uid, "👇", reply_markup=main_kb(uid))

async def admin(update, context):
    if update.effective_user.id != ADMIN_ID:
        return
    kb = [[InlineKeyboardButton("🔧 Админ-панель",
           web_app=WebAppInfo(url=f"{WEBAPP_URL}/admin"))]]
    await update.message.reply_text("🔧 <b>Админ ZERO CARGO</b>",
                                    parse_mode="HTML", reply_markup=InlineKeyboardMarkup(kb))

def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("admin", admin))
    application.add_handler(CallbackQueryHandler(cb))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, msg))
    application.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
