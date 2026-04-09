import os
import threading
from pyrogram import Client
from flask import Flask

# Flask server for Render health checks
app = Flask(__name__)

@app.route('/')
def health_check():
    return "Bot is running!", 200

# Your Bot configuration from environment variables
api_id = os.environ.get('API_ID')
api_hash = os.environ.get('API_HASH')
bot_token = os.environ.get('BOT_TOKEN')

app_bot = Client(
    "selectionway_bot",
    api_id=api_id,
    api_hash=api_hash,
    bot_token=bot_token
)

def run_bot():
    print("Starting Pyrogram Bot...")
    app_bot.run()

if __name__ == "__main__":
    # This part runs if you execute 'python bot.py' locally
    threading.Thread(target=run_bot, daemon=True).start()
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
else:
    # This part runs when Gunicorn imports 'app' from this file
    threading.Thread(target=run_bot, daemon=True).start()