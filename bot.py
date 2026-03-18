import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from database import Database

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8676654212:AAFtmReTMfPUrBMkVGSqc2XTUoBhmiwMmaU")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "1053328646"))
WEBAPP_URL = os.environ.get("WEBAPP_URL", "https://zerocargo-bot.onrender.com")
WHATSAPP = "996505600542"

db = Database()
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

def main_kb(uid):
    user = db.get_user(uid)
    lang = user.get("language", "ru") if user else "ru"
    if lang == "ru":
        kb = ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(text="📦 Мой код"), KeyboardButton(text="📮 Мои посылки")],
            [KeyboardButton(text="📍 Адреса"), KeyboardButton(text="📖 Инструкция")],
            [KeyboardButton(text="👤 Профиль"), KeyboardButton(text="🚫 Запрещённые грузы")],
            [KeyboardButton(text="💬 Поддержка"), KeyboardButton(text="🌐 Язык")],
        ], resize_keyboard=True)
    else:
        kb = ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(text="📦 Менин кодум"), KeyboardButton(text="📮 Менин посылкаларым")],
            [KeyboardButton(text="📍 Даректер"), KeyboardButton(text="📖 Нускама")],
            [KeyboardButton(text="👤 Профиль"), KeyboardButton(text="🚫 Тыюу салынган жүктөр")],
            [KeyboardButton(text="💬 Колдоо"), KeyboardButton(text="🌐 Тил")],
        ], resize_keyboard=True)
    return kb

def reg_kb():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="📝 Регистрация", web_app=WebAppInfo(url=f"{WEBAPP_URL}/register"))]
    ], resize_keyboard=True)

@dp.message(CommandStart())
async def start(message: types.Message):
    uid = message.from_user.id
    u = db.get_user(uid)
    if u:
        lang = u.get("language", "ru")
        if lang == "ru":
            text = f"👋 Добро пожаловать обратно, <b>{u['full_name']}</b>!\n🔑 Ваш код: <b>{u['client_code']}</b>"
        else:
            text = f"👋 Кайра кош келиңиз, <b>{u['full_name']}</b>!\n🔑 Кодуңуз: <b>{u['client_code']}</b>"
        await message.answer(text, parse_mode="HTML", reply_markup=main_kb(uid))
    else:
        await message.answer(
            "👋 Добро пожаловать в <b>ZERO CARGO</b> 🚛📦\n\n💎 Цена: <b>2.8$ за кг</b>\n⏱ Сроки: <b>7–14 дней</b>\n📍 Адрес: ж/м Рухий Мурас\n\nНажмите «Регистрация» чтобы продолжить.",
            parse_mode="HTML", reply_markup=reg_kb())

@dp.message(Command("admin"))
async def admin(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔧 Админ-панель", web_app=WebAppInfo(url=f"{WEBAPP_URL}/admin"))]
    ])
    await message.answer("🔧 <b>Админ ZERO CARGO</b>", parse_mode="HTML", reply_markup=kb)

@dp.message(F.text.in_(["📦 Мой код", "📦 Менин кодум"]))
async def my_code(message: types.Message):
    uid = message.from_user.id
    u = db.get_user(uid)
    if not u:
        await message.answer("❌ Вы не зарегистрированы.", reply_markup=reg_kb())
        return
    await message.answer(
        f"🔑 Код: <b>{u['client_code']}</b>\n👤 ФИО: <b>{u['full_name']}</b>\n📱 Тел: <b>{u['phone']}</b>\n📍 ПВЗ: ж/м Рухий Мурас\n📞 Менеджер: +996505600542",
        parse_mode="HTML", reply_markup=main_kb(uid))

@dp.message(F.text.in_(["📮 Мои посылки", "📮 Менин посылкаларым"]))
async def my_parcels(message: types.Message):
    uid = message.from_user.id
    u = db.get_user(uid)
    if not u:
        await message.answer("❌ Вы не зарегистрированы.", reply_markup=reg_kb())
        return
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔍 Открыть посылки", web_app=WebAppInfo(url=f"{WEBAPP_URL}/parcels?user_id={uid}"))]
    ])
    await message.answer("📦 Нажмите для просмотра посылок:", reply_markup=kb)

@dp.message(F.text.in_(["📍 Адреса", "📍 Даректер"]))
async def addresses(message: types.Message):
    uid = message.from_user.id
    u = db.get_user(uid)
    if not u:
        await message.answer("❌ Вы не зарегистрированы.", reply_markup=reg_kb())
        return
    await message.answer(
        f"📍 <b>Адрес склада в Китае:</b>\n\n收件人: VXMMM\n电话: 13545100875\n地址: 广东省佛山市南海区里广路洲村工业区飞机场13-2号\n（TSL КАРГО）VXMMM <b>{u['client_code']}</b>\n\n⚠️ Укажите ваш код вместо VXMMM",
        parse_mode="HTML")
    await message.answer("📍 <b>ПВЗ в Бишкеке:</b>\nж/м Рухий Мурас, Бишкек", parse_mode="HTML", reply_markup=main_kb(uid))

@dp.message(F.text.in_(["📖 Инструкция", "📖 Нускама"]))
async def instruction(message: types.Message):
    uid = message.from_user.id
    u = db.get_user(uid)
    code = u['client_code'] if u else "ВАШ КОД"
    await message.answer(
        f"📖 <b>Инструкция:</b>\n\n1️⃣ Зарегистрируйтесь и получите код\n2️⃣ При заказе укажите адрес склада в Китае со своим кодом\n3️⃣ Ожидайте посылку\n4️⃣ Отслеживайте в «Мои посылки»\n5️⃣ Получите в ж/м Рухий Мурас",
        parse_mode="HTML", reply_markup=main_kb(uid))

@dp.message(F.text.in_(["👤 Профиль"]))
async def profile(message: types.Message):
    uid = message.from_user.id
    u = db.get_user(uid)
    if not u:
        await message.answer("❌ Вы не зарегистрированы.", reply_markup=reg_kb())
        return
    await message.answer(
        f"👤 Профиль:\n🔑 Код: <b>{u['client_code']}</b>\n👤 ФИО: <b>{u['full_name']}</b>\n📱 Тел: <b>{u['phone']}</b>\n📍 ПВЗ: ж/м Рухий Мурас\n🗓 Регистрация: <b>{u['created_at'][:10]}</b>",
        parse_mode="HTML", reply_markup=main_kb(uid))

@dp.message(F.text.in_(["🚫 Запрещённые грузы", "🚫 Тыюу салынган жүктөр"]))
async def forbidden(message: types.Message):
    uid = message.from_user.id
    await message.answer(
        "🚫 <b>Запрещённые грузы:</b>\n❌ Лекарства и наркотики\n❌ Взрывчатые вещества\n❌ Острые предметы\n❌ Военные предметы\n❌ Жидкости и порошки\n❌ Электронные сигареты\n\n⚠️ Штраф 10 000 – 50 000 сом!",
        parse_mode="HTML", reply_markup=main_kb(uid))

@dp.message(F.text.in_(["💬 Поддержка", "💬 Колдоо"]))
async def support(message: types.Message):
    uid = message.from_user.id
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💚 WhatsApp", url=f"https://wa.me/{WHATSAPP}")],
        [InlineKeyboardButton(text="📱 Telegram", url="https://t.me/zerocargo312_bot")]
    ])
    await message.answer("💬 <b>Поддержка ZERO CARGO</b>\n📞 +996505600542", parse_mode="HTML", reply_markup=kb)

@dp.message(F.text.in_(["🌐 Язык", "🌐 Тил"]))
async def language(message: types.Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru"),
         InlineKeyboardButton(text="🇰🇬 Кыргызча", callback_data="lang_ky")]
    ])
    await message.answer("🌐 Выберите язык:", reply_markup=kb)

@dp.callback_query(F.data.startswith("lang_"))
async def set_lang(callback: types.CallbackQuery):
    uid = callback.from_user.id
    lang = callback.data.split("_")[1]
    db.update_language(uid, lang)
    msg = "✅ Язык: Русский" if lang == "ru" else "✅ Тил: Кыргызча"
    await callback.message.edit_text(msg)
    await callback.message.answer("👇", reply_markup=main_kb(uid))
    await callback.answer()

@dp.message(F.text.in_(["📝 Регистрация", "📝 Катталуу"]))
async def register(message: types.Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Открыть регистрацию", web_app=WebAppInfo(url=f"{WEBAPP_URL}/register"))]
    ])
    await message.answer("Нажмите кнопку:", reply_markup=kb)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
