import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import (
    init_db, add_entry, delete_entry,
    get_today_stats, get_week_stats, get_month_stats,
    get_all_stats, get_balance,
    add_share, remove_share, get_shared_owners
)

init_db()

# ── Formatters ───────────────────────────────────────────────────────────────

def fmt(amount: float) -> str:
    """Format number with thousands separator."""
    return f"{amount:,.0f}".replace(",", " ")


def stats_lines(stats: dict) -> str:
    balance = stats["income"] - stats["expenses"]
    sign = "+" if balance >= 0 else "-"
    return (
        f"💸 Spent:    {fmt(stats['expenses'])} UZS\n"
        f"💵 Earned:   {fmt(stats['income'])} UZS\n"
        f"💰 Balance:  {sign}{fmt(abs(balance))} UZS"
    )


# ── Main amount handler ───────────────────────────────────────────────────────

AMOUNT_RE = re.compile(r"^([+-])(\d[\d\s.,]*)$")


async def handle_amount(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip().replace(" ", "").replace(",", ".")
    match = AMOUNT_RE.match(text)

    if not match:
        # Silently ignore non-amount messages
        return

    sign = match.group(1)
    try:
        value = float(match.group(2))
    except ValueError:
        await update.message.reply_text("❌ Invalid number. Example: +200000 or -45000")
        return

    if value <= 0:
        await update.message.reply_text("❌ Amount must be greater than 0.")
        return

    user_id = update.effective_user.id
    entry_type = "income" if sign == "+" else "expense"
    entry_id = add_entry(user_id, value, entry_type)

    today = get_today_stats(user_id)
    overall = get_all_stats(user_id)
    bal = overall["income"] - overall["expenses"]
    bal_sign = "+" if bal >= 0 else "-"

    icon = "✅" if entry_type == "income" else "🔴"
    label = "Income" if entry_type == "income" else "Expense"
    amount_sign = "+" if entry_type == "income" else "-"

    text = (
        f"{icon} {label}: {amount_sign}{fmt(value)} UZS\n\n"
        f"📅 Today\n"
        f"  💸 Spent:  {fmt(today['expenses'])} UZS\n"
        f"  💵 Earned: {fmt(today['income'])} UZS\n\n"
        f"📊 All Time\n"
        f"  💸 Spent:  {fmt(overall['expenses'])} UZS\n"
        f"  💵 Earned: {fmt(overall['income'])} UZS\n"
        f"  💰 Balance: {bal_sign}{fmt(abs(bal))} UZS"
    )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("↩️ Undo last entry", callback_data=f"undo:{entry_id}")]
    ])

    await update.message.reply_text(text, reply_markup=keyboard)


async def handle_undo_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    entry_id = int(query.data.split(":")[1])

    deleted = delete_entry(entry_id, user_id)
    if deleted:
        overall = get_all_stats(user_id)
        bal = overall["income"] - overall["expenses"]
        bal_sign = "+" if bal >= 0 else "-"

        text = (
            "↩️ Entry removed.\n\n"
            f"📊 Updated All Time\n"
            f"  💸 Spent:  {fmt(overall['expenses'])} UZS\n"
            f"  💵 Earned: {fmt(overall['income'])} UZS\n"
            f"  💰 Balance: {bal_sign}{fmt(abs(bal))} UZS"
        )
        await query.edit_message_text(text)
    else:
        await query.edit_message_text("❌ Could not undo — entry not found or already removed.")


# ── Summary commands ─────────────────────────────────────────────────────────

async def cmd_today(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    stats = get_today_stats(user_id)
    await update.message.reply_text(f"📅 Today's Summary\n\n{stats_lines(stats)}")


async def cmd_week(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    stats = get_week_stats(user_id)
    await update.message.reply_text(f"📆 This Week's Summary\n\n{stats_lines(stats)}")


async def cmd_month(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    stats = get_month_stats(user_id)
    await update.message.reply_text(f"🗓 This Month's Summary\n\n{stats_lines(stats)}")


async def cmd_all(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    stats = get_all_stats(user_id)
    await update.message.reply_text(f"📊 All Time Summary\n\n{stats_lines(stats)}")


async def cmd_balance(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    bal = get_balance(user_id)
    sign = "+" if bal >= 0 else "-"
    emoji = "🟢" if bal >= 0 else "🔴"
    await update.message.reply_text(
        f"{emoji} Current Balance\n\n"
        f"💰 {sign}{fmt(abs(bal))} UZS"
    )


# ── Share commands ────────────────────────────────────────────────────────────

async def cmd_share(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """
    Usage: /share 123456789
    The viewer sends /share to get their ID, owner uses /share <viewer_id>
    """
    user_id = update.effective_user.id

    if not ctx.args:
        await update.message.reply_text(
            "ℹ️ To share your stats:\n\n"
            "1. Ask your wife to send /myid to this bot\n"
            "2. She'll get her Telegram ID\n"
            "3. You send: /share <her_id>\n\n"
            "Example: /share 123456789"
        )
        return

    try:
        viewer_id = int(ctx.args[0])
    except ValueError:
        await update.message.reply_text("❌ Please provide a valid numeric Telegram ID.\nExample: /share 123456789")
        return

    if viewer_id == user_id:
        await update.message.reply_text("❌ You can't share with yourself.")
        return

    add_share(user_id, viewer_id)
    await update.message.reply_text(
        f"✅ Shared! User {viewer_id} can now view your stats.\n\n"
        f"They can type /viewstats to see your summary."
    )


async def cmd_unshare(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if not ctx.args:
        await update.message.reply_text(
            "Usage: /unshare <viewer_id>\nExample: /unshare 123456789"
        )
        return

    try:
        viewer_id = int(ctx.args[0])
    except ValueError:
        await update.message.reply_text("❌ Invalid ID.")
        return

    remove_share(user_id, viewer_id)
    await update.message.reply_text(f"✅ Access removed for user {viewer_id}.")


# ── Utility commands ──────────────────────────────────────────────────────────

async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    name = update.effective_user.first_name or "there"
    await update.message.reply_text(
        f"👋 Hello {name}!\n\n"
        "I track your expenses and income.\n\n"
        "Just send me:\n"
        "  +200000  → income\n"
        "  -45000   → expense\n\n"
        "Commands:\n"
        "/today   — today's summary\n"
        "/week    — this week\n"
        "/month   — this month\n"
        "/all     — all time\n"
        "/balance — current balance\n"
        "/myid    — your Telegram ID (for sharing)\n"
        "/share   — share stats with someone\n"
        "/help    — show this help"
    )


async def cmd_help(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 How to use:\n\n"
        "Log money:\n"
        "  +200000  → earned 200,000 UZS\n"
        "  -45000   → spent 45,000 UZS\n\n"
        "After each entry you'll see an ↩️ Undo button.\n\n"
        "Commands:\n"
        "/today   — today's summary\n"
        "/week    — this week\n"
        "/month   — this month\n"
        "/all     — all time totals\n"
        "/balance — how much you have now\n"
        "/myid    — see your Telegram ID\n"
        "/share <id>   — share with someone\n"
        "/unshare <id> — remove their access\n"
        "/viewstats    — see stats shared with you"
    )


async def cmd_myid(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    await update.message.reply_text(
        f"🆔 Your Telegram ID: `{user_id}`\n\n"
        "Share this with someone so they can give you access to their stats.",
        parse_mode="Markdown"
    )


async def cmd_viewstats(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Let a viewer see stats of owners who shared with them."""
    viewer_id = update.effective_user.id
    owners = get_shared_owners(viewer_id)

    if not owners:
        await update.message.reply_text(
            "❌ No one has shared their stats with you yet.\n\n"
            "Ask them to use /share <your_id>.\n"
            f"Your ID: {viewer_id}"
        )
        return

    lines = []
    for owner_id in owners:
        stats = get_all_stats(owner_id)
        bal = stats["income"] - stats["expenses"]
        bal_sign = "+" if bal >= 0 else "-"
        lines.append(
            f"👤 User {owner_id}\n"
            f"  💸 Spent:  {fmt(stats['expenses'])} UZS\n"
            f"  💵 Earned: {fmt(stats['income'])} UZS\n"
            f"  💰 Balance: {bal_sign}{fmt(abs(bal))} UZS"
        )

    await update.message.reply_text(
        "📊 Shared Stats\n\n" + "\n\n".join(lines)
    )
