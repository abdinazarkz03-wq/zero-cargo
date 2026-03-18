import os
import asyncio
import threading
from dotenv import load_dotenv

load_dotenv()

from webapp import app
from bot import dp, bot


def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, use_reloader=False)


async def main():
    threading.Thread(target=run_flask, daemon=True).start()
    print("🚀 Система ZERO CARGO запущена и готова к работе!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("🛑 Работа остановлена")
