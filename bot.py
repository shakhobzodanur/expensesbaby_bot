import os
import logging
from datetime import time
import pytz
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, filters, ContextTypes
)
from handlers import (
    handle_amount, handle_undo_callback,
    cmd_today, cmd_week, cmd_month, cmd_all, cmd_balance,
    cmd_share, cmd_unshare, cmd_start, cmd_help,
    cmd_myid, cmd_viewstats
)
from scheduler import setup_scheduler

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TASHKENT_TZ = pytz.timezone("Asia/Tashkent")


def main():
    token = os.environ.get("BOT_TOKEN")
    if not token:
        raise ValueError("BOT_TOKEN environment variable not set")

    app = Application.builder().token(token).build()

    # Commands
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("today", cmd_today))
    app.add_handler(CommandHandler("week", cmd_week))
    app.add_handler(CommandHandler("month", cmd_month))
    app.add_handler(CommandHandler("all", cmd_all))
    app.add_handler(CommandHandler("balance", cmd_balance))
    app.add_handler(CommandHandler("share", cmd_share))
    app.add_handler(CommandHandler("unshare", cmd_unshare))
    app.add_handler(CommandHandler("myid", cmd_myid))
    app.add_handler(CommandHandler("viewstats", cmd_viewstats))

    # Amount messages like +200000 or -45000
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, handle_amount
    ))

    # Undo button callback
    app.add_handler(CallbackQueryHandler(handle_undo_callback, pattern="^undo:"))

    # Scheduled summaries
    setup_scheduler(app, TASHKENT_TZ)

    logger.info("Bot started...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
