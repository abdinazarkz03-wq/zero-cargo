import asyncio
import threading
import os
from webapp import app
from bot import dp, bot

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

async def main():
    # Запуск Flask в отдельном потоке
    threading.Thread(target=run_flask, daemon=True).start()
    # Запуск Telegram бота
    print("🚀 Система ZERO CARGO запущена и готова к работе!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("🛑 Работа остановлена")
