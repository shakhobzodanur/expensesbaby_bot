from datetime import time
from telegram.ext import Application
from database import get_conn, get_today_stats, get_week_stats
import logging

logger = logging.getLogger(__name__)


def fmt(amount: float) -> str:
    return f"{amount:,.0f}".replace(",", " ")


def stats_lines(stats: dict) -> str:
    balance = stats["income"] - stats["expenses"]
    sign = "+" if balance >= 0 else "-"
    return (
        f"💸 Spent:    {fmt(stats['expenses'])} UZS\n"
        f"💵 Earned:   {fmt(stats['income'])} UZS\n"
        f"💰 Balance:  {sign}{fmt(abs(balance))} UZS"
    )


def get_all_user_ids() -> list[int]:
    with get_conn() as conn:
        rows = conn.execute("SELECT DISTINCT user_id FROM entries").fetchall()
        return [r["user_id"] for r in rows]


async def send_daily_summary(context):
    user_ids = get_all_user_ids()
    for user_id in user_ids:
        try:
            stats = get_today_stats(user_id)
            if stats["expenses"] == 0 and stats["income"] == 0:
                continue  # skip if nothing logged today
            text = f"📅 Daily Summary\n\n{stats_lines(stats)}"
            await context.bot.send_message(chat_id=user_id, text=text)
        except Exception as e:
            logger.warning(f"Could not send daily summary to {user_id}: {e}")


async def send_weekly_summary(context):
    user_ids = get_all_user_ids()
    for user_id in user_ids:
        try:
            stats = get_week_stats(user_id)
            if stats["expenses"] == 0 and stats["income"] == 0:
                continue
            text = f"📆 Weekly Summary\n\n{stats_lines(stats)}"
            await context.bot.send_message(chat_id=user_id, text=text)
        except Exception as e:
            logger.warning(f"Could not send weekly summary to {user_id}: {e}")


def setup_scheduler(app: Application, tz):
    job_queue = app.job_queue

    # Daily summary every night at 23:59 Tashkent time
    job_queue.run_daily(
        send_daily_summary,
        time=time(23, 59, 0, tzinfo=tz),
        name="daily_summary"
    )

    # Weekly summary every Sunday at 21:00 Tashkent time
    job_queue.run_daily(
        send_weekly_summary,
        time=time(21, 0, 0, tzinfo=tz),
        days=(6,),  # 6 = Sunday
        name="weekly_summary"
    )
