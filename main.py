#!/usr/bin/env python3
"""Render worker entrypoint for the Ishonch Logistics courier bot.

Render runs `python main.py` for the worker service. We import the existing
bot module and start its long-polling loop. The Telegram token can be supplied
via the TELEGRAM_TOKEN (or BOT_TOKEN) environment variable on Render; if unset,
it falls back to the value baked into bot.py for local runs.
"""

import os

import bot

_token = os.environ.get("TELEGRAM_TOKEN") or os.environ.get("BOT_TOKEN")
if _token:
    # bot.main() reads the module-level TOKEN at call time, so overriding it
    # here takes effect before the Application is built.
    bot.TOKEN = _token


if __name__ == "__main__":
    bot.main()
