import asyncio
from webapp import app
from bot import get_dispatcher_instance, get_bot_instance
import threading
import os

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

async def main():
    dp = get_dispatcher_instance()
    bot = get_bot_instance()
    # Запускаем Flask в отдельном потоке
    threading.Thread(target=run_flask, daemon=True).start()
    # Запускаем бота
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
