#!/usr/bin/env python3
import os
import threading
import bot

# Override token from environment if set
_token = os.environ.get("TELEGRAM_TOKEN") or os.environ.get("BOT_TOKEN")
if _token:
    bot.TOKEN = _token

def run_bot():
    bot.main()

if __name__ == "__main__":
    # Start bot in background thread
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    print("Bot started in background thread")

    # Start proxy in main thread (Render needs open port)
    from proxy import app
    import os
    port = int(os.environ.get("PORT", 10000))
    print(f"Starting proxy on port {port}")
    from gunicorn.app.base import BaseApplication

    class StandaloneApp(BaseApplication):
        def __init__(self, app, options=None):
            self.options = options or {}
            self.application = app
            super().__init__()
        def load_config(self):
            for key, value in self.options.items():
                self.cfg.set(key.lower(), value)
        def load(self):
            return self.application

    options = {
        "bind": f"0.0.0.0:{port}",
        "workers": 2,
        "timeout": 30,
    }
    StandaloneApp(app, options).run()
