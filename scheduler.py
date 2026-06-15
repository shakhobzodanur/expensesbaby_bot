from datetime import time
from telegram.ext import Application
from database import get_all_user_ids, get_today_stats, get_week_stats, get_lang
from lang import t
import logging

logger = logging.getLogger(__name__)


def fmt(amount: float) -> str:
    return f"{amount:,.0f}".replace(",", " ")


def stats_lines(stats: dict, lang: str) -> str:
    balance = stats["income"] - stats["expenses"]
    sign = "+" if balance >= 0 else "-"
    return (
        f"💸 {t('spent', lang)}: {fmt(stats['expenses'])} UZS\n"
        f"💵 {t('earned', lang)}: {fmt(stats['income'])} UZS\n"
        f"💰 {t('balance', lang)}: {sign}{fmt(abs(balance))} UZS"
    )


async def send_daily_summary(context):
    for user_id in get_all_user_ids():
        try:
            stats = get_today_stats(user_id)
            if stats["expenses"] == 0 and stats["income"] == 0:
                continue
            lang = get_lang(user_id) or "en"
            text = f"{t('daily_summary', lang)}\n\n{stats_lines(stats, lang)}"
            await context.bot.send_message(chat_id=user_id, text=text)
        except Exception as e:
            logger.warning(f"Daily summary failed for {user_id}: {e}")


async def send_weekly_summary(context):
    for user_id in get_all_user_ids():
        try:
            stats = get_week_stats(user_id)
            if stats["expenses"] == 0 and stats["income"] == 0:
                continue
            lang = get_lang(user_id) or "en"
            text = f"{t('weekly_summary', lang)}\n\n{stats_lines(stats, lang)}"
            await context.bot.send_message(chat_id=user_id, text=text)
        except Exception as e:
            logger.warning(f"Weekly summary failed for {user_id}: {e}")


def setup_scheduler(app: Application, tz):
    jq = app.job_queue
    jq.run_daily(send_daily_summary, time=time(23, 59, 0, tzinfo=tz), name="daily_summary")
    jq.run_daily(send_weekly_summary, time=time(21, 0, 0, tzinfo=tz), days=(6,), name="weekly_summary")
