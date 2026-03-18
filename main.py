import threading
import os
import logging
from webapp import app
from bot import main as bot_main

logging.basicConfig(level=logging.INFO)

def run_webapp():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)

if __name__ == "__main__":
    webapp_thread = threading.Thread(target=run_webapp, daemon=True)
    webapp_thread.start()
    bot_main()
