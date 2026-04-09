"""
Selection Way Telegram Bot
Supports: Render (Web Service / Worker), Heroku, Railway, VPS
"""

import os
import sys
import asyncio
import logging

import aiohttp
from aiohttp import web
from pyrogram import Client, filters
from pyrogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

# ──────────────────────────────────────────────────────────
#  LOGGING
# ──────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("SelectionWayBot")

# ──────────────────────────────────────────────────────────
#  CONFIG  —  all values from environment variables
# ──────────────────────────────────────────────────────────
def _require(key: str) -> str:
    val = os.environ.get(key, "").strip()
    if not val:
        log.critical(f"❌ Environment variable '{key}' is not set. Exiting.")
        sys.exit(1)
    return val


API_ID    = int(_require("API_ID"))
API_HASH  = _require("API_HASH")
BOT_TOKEN = _require("BOT_TOKEN")

BASE_URL  = os.environ.get("BASE_URL", "https://raj-selectionwayapi.onrender.com").rstrip("/")

# Render injects PORT automatically; fallback to 8080
PORT = int(os.environ.get("PORT", 8080))

# ──────────────────────────────────────────────────────────
#  PYROGRAM CLIENT
# ──────────────────────────────────────────────────────────
app = Client(
    "selectionway_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    # store session in /tmp so it works on ephemeral filesystems
    workdir=os.environ.get("SESSION_DIR", "/tmp"),
)

# ──────────────────────────────────────────────────────────
#  HELPERS
# ──────────────────────────────────────────────────────────

async def api_get(path: str) -> dict:
    """GET request to Selection Way API, returns parsed JSON."""
    url = f"{BASE_URL}{path}"
    timeout = aiohttp.ClientTimeout(total=30)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(url) as resp:
            resp.raise_for_status()
            return await resp.json(content_type=None)


async def send_in_chunks(target, header: str, lines: list):
    """
    Send lines as Telegram messages, splitting when 4096-char limit is reached.
    First chunk uses `header`; subsequent chunks are plain continuation.
    """
    MAX = 4000  # slight margin below 4096
    chunk = header + "\n"

    for line in lines:
        candidate = chunk + line + "\n"
        if len(candidate) > MAX:
            await target.reply_text(chunk, disable_web_page_preview=True)
            chunk = line + "\n"
        else:
            chunk = candidate

    if chunk.strip():
        await target.reply_text(chunk, disable_web_page_preview=True)


# ──────────────────────────────────────────────────────────
#  /start
# ──────────────────────────────────────────────────────────

@app.on_message(filters.command("start") & filters.private)
async def cmd_start(_: Client, msg: Message):
    await msg.reply_text(
        "**📚 Selection Way Bot**\n\n"
        "इस bot से आप Selection Way के सभी batches के\n"
        "📄 **PDFs** और 🎬 **Videos** देख सकते हैं।\n\n"
        "➡️ /batches — सभी batches देखें",
        quote=True,
    )


# ──────────────────────────────────────────────────────────
#  /batches
# ──────────────────────────────────────────────────────────

@app.on_message(filters.command("batches") & filters.private)
async def cmd_batches(_: Client, msg: Message):
    loading = await msg.reply_text("⏳ Batches load हो रहे हैं...", quote=True)
    try:
        data = await api_get("/allbatch")
    except Exception as e:
        log.error(f"allbatch API error: {e}")
        await loading.edit_text(f"❌ API error: {e}\n\nThoda baad try karein.")
        return

    if not data.get("success"):
        await loading.edit_text("❌ Batches fetch नहीं हो सके। बाद में try करें।")
        return

    batches = data.get("data", [])
    if not batches:
        await loading.edit_text("⚠️ कोई batch नहीं मिला।")
        return

    buttons = [
        [InlineKeyboardButton(b["title"], callback_data=f"batch|{b['id']}")]
        for b in batches
        if b.get("id") and b.get("title")
    ]
    await loading.edit_text(
        "**📚 Available Batches**\n\nकोई एक batch चुनें:",
        reply_markup=InlineKeyboardMarkup(buttons),
    )


# ──────────────────────────────────────────────────────────
#  Batch menu (PDF / Video choice)
# ──────────────────────────────────────────────────────────

@app.on_callback_query(filters.regex(r"^batch\|(.+)$"))
async def cb_batch_menu(_: Client, cq: CallbackQuery):
    await cq.answer()
    batch_id = cq.data.split("|", 1)[1]
    buttons = [
        [InlineKeyboardButton("📄 PDFs देखें",   callback_data=f"pdf|{batch_id}")],
        [InlineKeyboardButton("🎬 Videos देखें", callback_data=f"vid|{batch_id}")],
        [InlineKeyboardButton("🔙 Batches",       callback_data="back|batches")],
    ]
    await cq.message.edit_text(
        "क्या चाहिए?",
        reply_markup=InlineKeyboardMarkup(buttons),
    )


# ──────────────────────────────────────────────────────────
#  PDFs
# ──────────────────────────────────────────────────────────

@app.on_callback_query(filters.regex(r"^pdf\|(.+)$"))
async def cb_pdfs(_: Client, cq: CallbackQuery):
    await cq.answer("PDFs fetch हो रहे हैं…")
    batch_id = cq.data.split("|", 1)[1]
    await cq.message.edit_text("⏳ PDFs load हो रहे हैं…")

    try:
        data = await api_get(f"/pdf/{batch_id}")
    except Exception as e:
        log.error(f"pdf API error ({batch_id}): {e}")
        await cq.message.edit_text(f"❌ Error: {e}")
        return

    if not data.get("success"):
        await cq.message.edit_text("❌ PDFs fetch नहीं हो सके।")
        return

    topics = data.get("topics", [])
    if not topics:
        await cq.message.edit_text("⚠️ इस batch में कोई PDF नहीं है।")
        return

    await cq.message.edit_text("📄 **PDFs — topic-wise list नीचे है:**")

    for topic in topics:
        topic_name = topic.get("topicName", "Unknown Topic")
        pdfs = topic.get("pdfs", [])
        if not pdfs:
            continue
        header = f"**📂 {topic_name}**"
        lines = [
            f"• [{p.get('title', 'Untitled')}]({p.get('uploadPdf', '')})"
            for p in pdfs
            if p.get("uploadPdf")
        ]
        if lines:
            await send_in_chunks(cq.message, header, lines)


# ──────────────────────────────────────────────────────────
#  Videos
# ──────────────────────────────────────────────────────────

@app.on_callback_query(filters.regex(r"^vid\|(.+)$"))
async def cb_videos(_: Client, cq: CallbackQuery):
    await cq.answer("Videos fetch हो रहे हैं…")
    batch_id = cq.data.split("|", 1)[1]
    await cq.message.edit_text("⏳ Videos load हो रहे हैं…")

    try:
        data = await api_get(f"/chapter/{batch_id}")
    except Exception as e:
        log.error(f"chapter API error ({batch_id}): {e}")
        await cq.message.edit_text(f"❌ Error: {e}")
        return

    if not data.get("success"):
        await cq.message.edit_text("❌ Videos fetch नहीं हो सके।")
        return

    chapters = data.get("classes", [])
    if not chapters:
        await cq.message.edit_text("⚠️ इस batch में कोई video नहीं है।")
        return

    await cq.message.edit_text("🎬 **Videos — topic-wise list नीचे है:**")

    for topic in chapters:
        topic_name = topic.get("topicName", "Unknown Topic")
        videos = topic.get("classes", [])
        if not videos:
            continue
        header = f"**📹 {topic_name}**"
        lines = [
            f"• [{v.get('title', 'Untitled')}]({v.get('class_link', '')})"
            for v in videos
            if v.get("class_link")
        ]
        if lines:
            await send_in_chunks(cq.message, header, lines)


# ──────────────────────────────────────────────────────────
#  Back → Batches
# ──────────────────────────────────────────────────────────

@app.on_callback_query(filters.regex(r"^back\|batches$"))
async def cb_back_batches(_: Client, cq: CallbackQuery):
    await cq.answer("वापस जा रहे हैं…")
    await cq.message.edit_text("⏳ Batches load हो रहे हैं…")

    try:
        data = await api_get("/allbatch")
    except Exception as e:
        log.error(f"allbatch (back) error: {e}")
        await cq.message.edit_text(f"❌ Error: {e}")
        return

    if not data.get("success"):
        await cq.message.edit_text("❌ Batches fetch नहीं हो सके।")
        return

    batches = data.get("data", [])
    buttons = [
        [InlineKeyboardButton(b["title"], callback_data=f"batch|{b['id']}")]
        for b in batches
        if b.get("id") and b.get("title")
    ]
    await cq.message.edit_text(
        "**📚 Available Batches**\n\nकोई एक batch चुनें:",
        reply_markup=InlineKeyboardMarkup(buttons),
    )


# ──────────────────────────────────────────────────────────
#  HEALTH-CHECK WEB SERVER  (required for Render Web Service)
#  Render pings GET /  — must return 200 or service is killed
# ──────────────────────────────────────────────────────────

async def handle_health(_request: web.Request) -> web.Response:
    return web.Response(text="OK — Selection Way Bot is running ✅")


async def run_web_server():
    web_app = web.Application()
    web_app.router.add_get("/", handle_health)
    web_app.router.add_get("/health", handle_health)
    runner = web.AppRunner(web_app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    log.info(f"✅ Health-check server running on port {PORT}")


# ──────────────────────────────────────────────────────────
#  MAIN  —  run bot + web server concurrently
# ──────────────────────────────────────────────────────────

async def main():
    log.info("🚀 Starting Selection Way Bot…")
    await run_web_server()
    await app.start()
    me = await app.get_me()
    log.info(f"✅ Bot started as @{me.username}")
    await asyncio.Event().wait()          # keep running forever


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.info("Bot stopped.")
