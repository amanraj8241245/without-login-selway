import os
from pyrogram import Client
from flask import Flask
import threading

# Flask server for Render health checks
app = Flask(__name__)

@app.route('/')
def health_check():
    return "Bot is running!", 200

def run_flask():
    # Render provides the PORT environment variable
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# Your Bot configuration
api_id = os.environ.get('API_ID')
api_hash = os.environ.get('API_HASH')
bot_token = os.environ.get('BOT_TOKEN')

app_bot = Client(
    "selectionway_bot",
    api_id=api_id,
    api_hash=api_hash,
    bot_token=bot_token
)

if __name__ == "__main__":
    # Start Flask in a separate thread
    threading.Thread(target=run_flask, daemon=True).start()
    print("Starting Bot...")
    app_bot.run()