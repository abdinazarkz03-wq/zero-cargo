import threading
import asyncio
import os
from webapp import app
from bot import bot_start

def run_webapp():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)

if __name__ == "__main__":
    threading.Thread(target=run_webapp, daemon=True).start()
    asyncio.run(bot_start())
