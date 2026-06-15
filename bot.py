import os
import logging
import pytz
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, filters
)
from handlers import (
    handle_amount, handle_undo_callback,
    handle_setup_lang_callback, handle_setup_cur_callback,
    handle_setlang_callback, handle_setcur_callback,
    handle_cfg_callback, handle_reset_callback,
    cmd_today, cmd_week, cmd_month, cmd_all, cmd_balance,
    cmd_setlimit, cmd_language, cmd_settings,
    cmd_share, cmd_unshare, cmd_start, cmd_help,
    cmd_myid, cmd_viewstats
)
from scheduler import setup_scheduler

logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=logging.INFO)
TASHKENT_TZ = pytz.timezone("Asia/Tashkent")


def main():
    token = os.environ.get("BOT_TOKEN")
    if not token:
        raise ValueError("BOT_TOKEN not set")

    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start",     cmd_start))
    app.add_handler(CommandHandler("help",      cmd_help))
    app.add_handler(CommandHandler("today",     cmd_today))
    app.add_handler(CommandHandler("week",      cmd_week))
    app.add_handler(CommandHandler("month",     cmd_month))
    app.add_handler(CommandHandler("all",       cmd_all))
    app.add_handler(CommandHandler("balance",   cmd_balance))
    app.add_handler(CommandHandler("setlimit",  cmd_setlimit))
    app.add_handler(CommandHandler("language",  cmd_language))
    app.add_handler(CommandHandler("settings",  cmd_settings))
    app.add_handler(CommandHandler("share",     cmd_share))
    app.add_handler(CommandHandler("unshare",   cmd_unshare))
    app.add_handler(CommandHandler("myid",      cmd_myid))
    app.add_handler(CommandHandler("viewstats", cmd_viewstats))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_amount))

    # Callbacks — order matters: most specific first
    app.add_handler(CallbackQueryHandler(handle_setup_lang_callback, pattern="^setup_lang:"))
    app.add_handler(CallbackQueryHandler(handle_setup_cur_callback,  pattern="^setup_cur:"))
    app.add_handler(CallbackQueryHandler(handle_setlang_callback,    pattern="^setlang:"))
    app.add_handler(CallbackQueryHandler(handle_setcur_callback,     pattern="^setcur:"))
    app.add_handler(CallbackQueryHandler(handle_cfg_callback,        pattern="^cfg:"))
    app.add_handler(CallbackQueryHandler(handle_reset_callback,      pattern="^reset:"))
    app.add_handler(CallbackQueryHandler(handle_undo_callback,       pattern="^undo:"))

    setup_scheduler(app, TASHKENT_TZ)

    logging.info("Bot started")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
