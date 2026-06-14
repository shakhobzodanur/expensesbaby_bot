# 🚀 Expense Bot — Railway Deployment Guide

## Step 1 — Create your Telegram Bot

1. Open Telegram → search **@BotFather**
2. Send `/newbot`
3. Choose a name: e.g. `Nuriddin Expense Bot`
4. Choose a username: e.g. `nuriddin_expense_bot` (must end in `bot`)
5. BotFather sends you a **token** like:
   `7123456789:AAFxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
6. **Copy and save this token**

---

## Step 2 — Upload code to GitHub

1. Go to [github.com](https://github.com) → **New repository**
2. Name it: `expense-bot` → Create
3. Upload these files:
   - `bot.py`
   - `handlers.py`
   - `database.py`
   - `scheduler.py`
   - `requirements.txt`
   - `Procfile`
   - `railway.toml`
   - `.gitignore`

---

## Step 3 — Deploy on Railway

1. Go to [railway.app](https://railway.app) → Sign up with GitHub
2. Click **New Project** → **Deploy from GitHub repo**
3. Select your `expense-bot` repo
4. Railway auto-detects Python ✅

### Add environment variable:
- Click your service → **Variables** tab
- Add: `BOT_TOKEN` = `your token from Step 1`

### Add persistent storage (for the database):
- Click **+ New** → **Volume**
- Mount path: `/data`
- Then add another variable: `DB_PATH` = `/data/expenses.db`

5. Click **Deploy** — done! 🎉

---

## Step 4 — Test your bot

Open Telegram → find your bot → send:
```
+500000
-45000
/balance
/today
```

---

## How to use

| Send this | What happens |
|-----------|-------------|
| `+200000` | Logs 200,000 UZS income |
| `-45000`  | Logs 45,000 UZS expense |
| ↩️ Undo button | Removes last entry |
| `/today`  | Today's summary |
| `/week`   | This week |
| `/month`  | This month |
| `/all`    | All time totals |
| `/balance`| Current balance |

## Share with wife

**You:**
1. Ask her to send `/myid` to the bot
2. She gets her ID (e.g. `987654321`)
3. You send: `/share 987654321`

**She:**
- Sends `/viewstats` to see your summary (read-only)

**To remove access:**
- You send: `/unshare 987654321`

---

## Auto summaries

- Every night at **23:59** → daily summary sent automatically
- Every **Sunday at 21:00** → weekly summary sent automatically

*(All times in Tashkent timezone — Asia/Tashkent)*
