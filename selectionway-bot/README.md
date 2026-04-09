# 📚 Selection Way Telegram Bot

Selection Way API से PDFs और Videos को Telegram पर serve करने वाला bot.

---

## ✨ Features

- `/start` → Welcome message
- `/batches` → सभी batches inline buttons में
- Batch → PDF links या Video links (topic-wise)
- Long lists auto-split (4096 char limit safe)
- 🔙 Back button
- Built-in health-check server → Render free tier compatible

---

## 📁 Files

```
selectionway-bot/
├── bot.py             ← Main bot code
├── requirements.txt   ← Python dependencies
├── Procfile           ← Heroku worker
├── render.yaml        ← Render one-click config
├── railway.toml       ← Railway config
├── runtime.txt        ← Python version (Heroku)
├── .env.example       ← Environment variables template
└── .gitignore
```

---

## ⚙️ Environment Variables

| Variable      | Description                                | Required |
|---------------|--------------------------------------------|----------|
| `API_ID`      | Telegram API ID from https://my.telegram.org | ✅ Yes  |
| `API_HASH`    | Telegram API Hash from https://my.telegram.org | ✅ Yes |
| `BOT_TOKEN`   | Bot token from @BotFather                  | ✅ Yes   |
| `BASE_URL`    | API base URL (default already set)         | ❌ No    |
| `SESSION_DIR` | Session file directory (default: `/tmp`)   | ❌ No    |
| `PORT`        | Health-check port (Render sets this auto)  | ❌ No    |

---

## 🚀 Deploy on Render (Free Web Service) — RECOMMENDED

> **Render free plan** पर bot बिना error के run होगा।

### Step 1 — GitHub repo बनाएं

```bash
git init
git add .
git commit -m "Initial commit"
# GitHub पर new repo बनाएं, फिर:
git remote add origin https://github.com/YOUR_USERNAME/selectionway-bot.git
git push -u origin main
```

### Step 2 — Render पर deploy करें

1. https://render.com पर जाएं → Sign up / Login
2. **New +** → **Web Service**
3. GitHub repo connect करें
4. Settings:
   - **Name:** `selectionway-bot`
   - **Runtime:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python bot.py`
   - **Plan:** `Free`
5. **Environment Variables** tab में add करें:
   ```
   API_ID      = आपका API ID
   API_HASH    = आपका API Hash
   BOT_TOKEN   = आपका Bot Token
   SESSION_DIR = /tmp
   ```
6. **Create Web Service** click करें ✅

> ⚠️ **Note:** Render free tier ~15 min idle के बाद sleep करता है।
> Bot को active रखने के लिए UptimeRobot (free) से `/health` endpoint ping करें।

### UptimeRobot से bot को 24/7 active रखें (Free)

1. https://uptimerobot.com → Sign up
2. **New Monitor** → **HTTP(s)**
3. URL: `https://YOUR-APP.onrender.com/health`
4. Interval: **5 minutes**
5. Save → Bot हमेशा active रहेगा ✅

---

## 🟣 Deploy on Heroku

### Step 1 — Heroku CLI install करें

```bash
# macOS
brew tap heroku/brew && brew install heroku

# Windows: https://devcenter.heroku.com/articles/heroku-cli से installer download करें
```

### Step 2 — Deploy करें

```bash
heroku login
heroku create selectionway-bot

# Environment variables set करें
heroku config:set API_ID="आपका API ID"
heroku config:set API_HASH="आपका API Hash"
heroku config:set BOT_TOKEN="आपका Bot Token"
heroku config:set SESSION_DIR="/tmp"

# Deploy
git push heroku main

# Worker dyno scale करें (bot के लिए web नहीं, worker चाहिए)
heroku ps:scale worker=1
heroku ps:scale web=0
```

---

## 🚂 Deploy on Railway

1. https://railway.app → Login with GitHub
2. **New Project** → **Deploy from GitHub Repo**
3. Repo select करें
4. **Variables** tab में add करें:
   ```
   API_ID, API_HASH, BOT_TOKEN, SESSION_DIR=/tmp
   ```
5. Deploy होगा automatically ✅

---

## 💻 Local Run करें

```bash
# Repo clone करें
git clone https://github.com/YOUR_USERNAME/selectionway-bot.git
cd selectionway-bot

# Dependencies install करें
pip install -r requirements.txt

# .env file बनाएं
cp .env.example .env
# .env file खोलें और API_ID, API_HASH, BOT_TOKEN भरें

# Bot run करें
python bot.py
```

---

## 🔧 Credentials कहाँ से लें?

### API_ID और API_HASH
1. https://my.telegram.org/auth पर जाएं
2. अपना phone number enter करें
3. **API development tools** click करें
4. App बनाएं → `App api_id` और `App api_hash` मिलेगा

### BOT_TOKEN
1. Telegram में @BotFather खोलें
2. `/newbot` send करें
3. Bot का नाम और username दें
4. Token मिल जाएगा

---

## ❓ Common Errors & Fixes

| Error | Fix |
|-------|-----|
| `API_ID is not set` | Render/Heroku में environment variable check करें |
| `401 Unauthorized` | BOT_TOKEN गलत है, @BotFather से दोबारा लें |
| `Session conflict` | `SESSION_DIR=/tmp` set करें |
| `Port already in use` | `PORT` env variable change करें |
| Bot responds to old messages | Normal है, पहली बार start पर होता है |
