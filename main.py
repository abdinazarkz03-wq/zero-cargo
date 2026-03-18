import asyncio
import threading
import os
from webapp import app
from bot import get_dispatcher_instance, get_bot_instance, set_main_menu

def run_flask():
    # Render сам назначит порт, берем его из системы
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

async def main():
    dp = get_dispatcher_instance()
    bot = get_bot_instance()

    # 1. Запускаем Flask (сайт и админку) в отдельном потоке
    print("Запуск веб-сервера...")
    threading.Thread(target=run_flask, daemon=True).start()

    # 2. Устанавливаем команды меню в Telegram (Кнопка Menu)
    print("Настройка команд меню...")
    await set_main_menu(bot)

    # 3. Запускаем бота
    print("Бот ZERO CARGO запущен и готов к работе!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Работа бота остановлена")
