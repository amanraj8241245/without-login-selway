import os
import asyncio
import aiohttp
from pyrogram import Client, filters
from pyrogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

# ─────────────────────── CONFIG ───────────────────────
API_ID    = int(os.environ.get("API_ID", 0))
API_HASH  = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
BASE_URL  = "https://raj-selectionwayapi.onrender.com"
# ──────────────────────────────────────────────────────

app = Client(
    "selectionway_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
)


# ───────────────────── HELPER ─────────────────────────

async def api_get(path: str) -> dict:
    """Perform a GET request to the API and return JSON."""
    url = f"{BASE_URL}{path}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as resp:
            resp.raise_for_status()
            return await resp.json()


async def send_in_chunks(target, header: str, lines: list[str]):
    """
    Send `lines` as one or more Telegram messages.
    Each message starts with `header` if it is the first chunk.
    """
    MAX = 4096
    chunk = header + "\n"
    first = True

    for line in lines:
        candidate = chunk + line + "\n"
        if len(candidate) > MAX:
            await target.reply_text(chunk, disable_web_page_preview=True)
            chunk = line + "\n"
            first = False
        else:
            chunk = candidate

    if chunk.strip():
        await target.reply_text(chunk, disable_web_page_preview=True)


# ──────────────────── /start  ─────────────────────────

@app.on_message(filters.command("start") & filters.private)
async def cmd_start(_: Client, msg: Message):
    await msg.reply_text(
        "**📚 Selection Way Bot**\n\n"
        "इस bot से आप Selection Way के सभी batches के\n"
        "📄 **PDFs** और 🎬 **Videos** देख सकते हैं।\n\n"
        "➡️ /batches — सभी batches देखें",
        quote=True,
    )


# ─────────────────── /batches  ────────────────────────

@app.on_message(filters.command("batches") & filters.private)
async def cmd_batches(_: Client, msg: Message):
    loading = await msg.reply_text("⏳ Batches load हो रहे हैं...", quote=True)
    try:
        data = await api_get("/allbatch")
    except Exception as e:
        await loading.edit_text(f"❌ API error: {e}")
        return

    if not data.get("success"):
        await loading.edit_text("❌ Batches fetch नहीं हो सके। बाद में try करें।")
        return

    batches = data.get("data", [])
    if not batches:
        await loading.edit_text("कोई batch नहीं मिला।")
        return

    buttons = [
        [InlineKeyboardButton(b["title"], callback_data=f"batch|{b['id']}")]
        for b in batches
    ]
    await loading.edit_text(
        "**📚 Available Batches**\n\nकोई एक batch चुनें:",
        reply_markup=InlineKeyboardMarkup(buttons),
    )


# ─────────────── Batch selected → PDF / Video ─────────

@app.on_callback_query(filters.regex(r"^batch\|(.+)$"))
async def cb_batch_menu(_: Client, cq: CallbackQuery):
    batch_id = cq.data.split("|", 1)[1]
    buttons = [
        [InlineKeyboardButton("📄 PDFs देखें",    callback_data=f"pdf|{batch_id}")],
        [InlineKeyboardButton("🎬 Videos देखें",  callback_data=f"vid|{batch_id}")],
        [InlineKeyboardButton("🔙 Back",           callback_data="back|batches")],
    ]
    await cq.message.edit_text(
        "क्या चाहिए?",
        reply_markup=InlineKeyboardMarkup(buttons),
    )
    await cq.answer()


# ─────────────────── PDFs ─────────────────────────────

@app.on_callback_query(filters.regex(r"^pdf\|(.+)$"))
async def cb_pdfs(_: Client, cq: CallbackQuery):
    batch_id = cq.data.split("|", 1)[1]
    await cq.answer("PDFs fetch हो रहे हैं…")
    await cq.message.edit_text("⏳ PDFs load हो रहे हैं…")

    try:
        data = await api_get(f"/pdf/{batch_id}")
    except Exception as e:
        await cq.message.edit_text(f"❌ Error: {e}")
        return

    if not data.get("success"):
        await cq.message.edit_text("❌ PDFs fetch नहीं हो सके।")
        return

    topics = data.get("topics", [])
    if not topics:
        await cq.message.edit_text("इस batch में कोई PDF नहीं है।")
        return

    await cq.message.edit_text("📄 **PDFs — नीचे topic-wise list है:**")

    for topic in topics:
        topic_name = topic.get("topicName", "Unknown Topic")
        pdfs = topic.get("pdfs", [])
        if not pdfs:
            continue

        header = f"**📂 {topic_name}**"
        lines = [f"• [{p.get('title','Untitled')}]({p.get('uploadPdf','')})" for p in pdfs]
        await send_in_chunks(cq.message, header, lines)


# ─────────────────── Videos ───────────────────────────

@app.on_callback_query(filters.regex(r"^vid\|(.+)$"))
async def cb_videos(_: Client, cq: CallbackQuery):
    batch_id = cq.data.split("|", 1)[1]
    await cq.answer("Videos fetch हो रहे हैं…")
    await cq.message.edit_text("⏳ Videos load हो रहे हैं…")

    try:
        data = await api_get(f"/chapter/{batch_id}")
    except Exception as e:
        await cq.message.edit_text(f"❌ Error: {e}")
        return

    if not data.get("success"):
        await cq.message.edit_text("❌ Videos fetch नहीं हो सके।")
        return

    chapters = data.get("classes", [])
    if not chapters:
        await cq.message.edit_text("इस batch में कोई video नहीं है।")
        return

    await cq.message.edit_text("🎬 **Videos — नीचे topic-wise list है:**")

    for topic in chapters:
        topic_name = topic.get("topicName", "Unknown Topic")
        videos = topic.get("classes", [])
        if not videos:
            continue

        header = f"**📹 {topic_name}**"
        lines = [f"• [{v.get('title','Untitled')}]({v.get('class_link','')})" for v in videos]
        await send_in_chunks(cq.message, header, lines)


# ─────────────── Back → Batches list ──────────────────

@app.on_callback_query(filters.regex(r"^back\|batches$"))
async def cb_back_batches(_: Client, cq: CallbackQuery):
    await cq.answer("वापस जा रहे हैं…")
    await cq.message.edit_text("⏳ Batches load हो रहे हैं…")

    try:
        data = await api_get("/allbatch")
    except Exception as e:
        await cq.message.edit_text(f"❌ Error: {e}")
        return

    if not data.get("success"):
        await cq.message.edit_text("❌ Batches fetch नहीं हो सके।")
        return

    batches = data.get("data", [])
    buttons = [
        [InlineKeyboardButton(b["title"], callback_data=f"batch|{b['id']}")]
        for b in batches
    ]
    await cq.message.edit_text(
        "**📚 Available Batches**\n\nकोई एक batch चुनें:",
        reply_markup=InlineKeyboardMarkup(buttons),
    )


# ──────────────────────── RUN ─────────────────────────

if __name__ == "__main__":
    print("Bot starting...")
    app.run()
