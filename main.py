import asyncio
import threading
import os
from webapp import app
from bot import dp, bot  # Убедись, что в bot.py есть переменные dp и bot

def run_flask():
    # Render сам назначит порт
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

async def main():
    # 1. Запускаем Flask (сайт и админку) в отдельном потоке
    print("🚀 Запуск веб-сервера...")
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    # 2. Запускаем бота
    print("🤖 Бот ZERO CARGO запущен и готов к работе!")
    try:
        await dp.start_polling(bot)
    except Exception as e:
        print(f"❌ Ошибка при запуске бота: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("🛑 Работа остановлена")
