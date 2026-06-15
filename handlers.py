import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import (
    init_db, ensure_user, get_lang, set_lang,
    get_daily_limit, set_daily_limit,
    add_entry, delete_entry,
    get_today_stats, get_week_stats, get_month_stats,
    get_all_stats, get_balance, get_last_week_expenses,
    add_share, remove_share, get_shared_owners
)
from lang import t, LANGUAGES

init_db()

# Daily-limit warning threshold (percent) before the limit itself
NEAR_THRESHOLD = 0.8
# How much more than last week triggers a spike warning
SPIKE_RATIO = 1.30


def fmt(amount: float) -> str:
    return f"{amount:,.0f}".replace(",", " ")


def pct(part: float, whole: float) -> float:
    if whole <= 0:
        return 0.0
    return round(part / whole * 100, 1)


# ── language gate ─────────────────────────────────────────────────────────────

def lang_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(LANGUAGES["en"], callback_data="setlang:en")],
        [InlineKeyboardButton(LANGUAGES["ru"], callback_data="setlang:ru")],
        [InlineKeyboardButton(LANGUAGES["uz"], callback_data="setlang:uz")],
    ])


async def ask_language(update: Update):
    msg = update.message or update.callback_query.message
    await msg.reply_text(
        "🌐 Choose your language / Выберите язык / Tilni tanlang:",
        reply_markup=lang_keyboard()
    )


async def handle_setlang_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = query.data.split(":")[1]
    user_id = update.effective_user.id
    set_lang(user_id, lang)
    name = update.effective_user.first_name or ""
    await query.edit_message_text(t("language_set", lang))
    await query.message.reply_text(t("welcome", lang, name=name))


# ── stats block ───────────────────────────────────────────────────────────────

def stats_lines(stats: dict, lang: str) -> str:
    balance = stats["income"] - stats["expenses"]
    sign = "+" if balance >= 0 else "-"
    return (
        f"💸 {t('spent', lang)}: {fmt(stats['expenses'])} UZS\n"
        f"💵 {t('earned', lang)}: {fmt(stats['income'])} UZS\n"
        f"💰 {t('balance', lang)}: {sign}{fmt(abs(balance))} UZS"
    )


# ── main amount handler ───────────────────────────────────────────────────────

AMOUNT_RE = re.compile(r"^([+-])(\d[\d\s.,]*)$")


async def handle_amount(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = get_lang(user_id)
    if lang is None:
        await ask_language(update)
        return

    raw = update.message.text.strip().replace(" ", "").replace(",", ".")
    match = AMOUNT_RE.match(raw)
    if not match:
        return  # ignore non-amount text

    sign = match.group(1)
    try:
        value = float(match.group(2))
    except ValueError:
        await update.message.reply_text(t("invalid_number", lang))
        return
    if value <= 0:
        await update.message.reply_text(t("invalid_number", lang))
        return

    entry_type = "income" if sign == "+" else "expense"
    entry_id = add_entry(user_id, value, entry_type)

    today = get_today_stats(user_id)
    overall = get_all_stats(user_id)
    bal = overall["income"] - overall["expenses"]
    bal_sign = "+" if bal >= 0 else "-"

    head = t(entry_type, lang)
    amt_sign = "+" if entry_type == "income" else "-"

    parts = [
        f"{head}: {amt_sign}{fmt(value)} UZS\n",
        f"{t('today', lang)}",
        f"  💸 {t('spent', lang)}: {fmt(today['expenses'])} UZS",
        f"  💵 {t('earned', lang)}: {fmt(today['income'])} UZS\n",
        f"{t('all_time', lang)}",
        f"  💸 {t('spent', lang)}: {fmt(overall['expenses'])} UZS",
        f"  💵 {t('earned', lang)}: {fmt(overall['income'])} UZS",
        f"  💰 {t('balance', lang)}: {bal_sign}{fmt(abs(bal))} UZS",
    ]

    # ── percentages ──
    if entry_type == "expense":
        if bal > 0:
            parts.append("")
            parts.append(t("pct_of_balance", lang, pct=pct(value, bal)))
        if overall["income"] > 0:
            parts.append(t("pct_spent_of_earned", lang,
                           pct=pct(overall["expenses"], overall["income"])))
    else:  # income
        if overall["income"] > 0:
            parts.append("")
            parts.append(t("pct_of_earned_income", lang,
                           pct=pct(value, overall["income"])))

    # ── daily limit warning (only for expenses) ──
    if entry_type == "expense":
        limit = get_daily_limit(user_id)
        if limit > 0:
            spent_today = today["expenses"]
            if spent_today >= limit:
                parts.append("")
                parts.append(t("limit_over", lang,
                               spent=fmt(spent_today), limit=fmt(limit)))
            elif spent_today >= limit * NEAR_THRESHOLD:
                parts.append("")
                parts.append(t("limit_near", lang,
                               pct=pct(spent_today, limit), limit=fmt(limit)))

        # ── weekly spike warning ──
        this_week = get_week_stats(user_id)["expenses"]
        last_week = get_last_week_expenses(user_id)
        if last_week > 0 and this_week > last_week * SPIKE_RATIO:
            more = pct(this_week - last_week, last_week)
            parts.append("")
            parts.append(t("week_spike", lang, pct=more))

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(t("undo_btn", lang), callback_data=f"undo:{entry_id}")]
    ])
    await update.message.reply_text("\n".join(parts), reply_markup=keyboard)


async def handle_undo_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    lang = get_lang(user_id) or "en"
    entry_id = int(query.data.split(":")[1])

    if delete_entry(entry_id, user_id):
        overall = get_all_stats(user_id)
        bal = overall["income"] - overall["expenses"]
        bal_sign = "+" if bal >= 0 else "-"
        text = (
            f"{t('undo_done', lang)}\n\n"
            f"📊 {t('updated', lang)}\n"
            f"  💸 {t('spent', lang)}: {fmt(overall['expenses'])} UZS\n"
            f"  💵 {t('earned', lang)}: {fmt(overall['income'])} UZS\n"
            f"  💰 {t('balance', lang)}: {bal_sign}{fmt(abs(bal))} UZS"
        )
        await query.edit_message_text(text)
    else:
        await query.edit_message_text(t("undo_fail", lang))


# ── summary commands ──────────────────────────────────────────────────────────

async def _require_lang(update: Update):
    """Return lang or None (and prompt) if user hasn't chosen yet."""
    user_id = update.effective_user.id
    lang = get_lang(user_id)
    if lang is None:
        await ask_language(update)
    return lang


async def cmd_today(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    lang = await _require_lang(update)
    if lang is None:
        return
    stats = get_today_stats(update.effective_user.id)
    await update.message.reply_text(f"{t('sum_today', lang)}\n\n{stats_lines(stats, lang)}")


async def cmd_week(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    lang = await _require_lang(update)
    if lang is None:
        return
    stats = get_week_stats(update.effective_user.id)
    await update.message.reply_text(f"{t('sum_week', lang)}\n\n{stats_lines(stats, lang)}")


async def cmd_month(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    lang = await _require_lang(update)
    if lang is None:
        return
    stats = get_month_stats(update.effective_user.id)
    await update.message.reply_text(f"{t('sum_month', lang)}\n\n{stats_lines(stats, lang)}")


async def cmd_all(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    lang = await _require_lang(update)
    if lang is None:
        return
    stats = get_all_stats(update.effective_user.id)
    await update.message.reply_text(f"{t('sum_all', lang)}\n\n{stats_lines(stats, lang)}")


async def cmd_balance(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    lang = await _require_lang(update)
    if lang is None:
        return
    bal = get_balance(update.effective_user.id)
    sign = "+" if bal >= 0 else "-"
    emoji = "🟢" if bal >= 0 else "🔴"
    await update.message.reply_text(
        f"{emoji} {t('cur_balance', lang)}\n\n💰 {sign}{fmt(abs(bal))} UZS"
    )


# ── set daily limit ───────────────────────────────────────────────────────────

async def cmd_setlimit(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    lang = await _require_lang(update)
    if lang is None:
        return
    user_id = update.effective_user.id

    if not ctx.args:
        cur = get_daily_limit(user_id)
        await update.message.reply_text(t("setlimit_usage", lang, limit=fmt(cur)))
        return

    raw = ctx.args[0].replace(" ", "").replace(",", "").replace(".", "")
    try:
        limit = float(raw)
        if limit <= 0:
            raise ValueError
    except ValueError:
        await update.message.reply_text(t("setlimit_invalid", lang))
        return

    set_daily_limit(user_id, limit)
    await update.message.reply_text(t("setlimit_done", lang, limit=fmt(limit)))


# ── language command ──────────────────────────────────────────────────────────

async def cmd_language(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await ask_language(update)


# ── share commands ────────────────────────────────────────────────────────────

async def cmd_share(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    lang = await _require_lang(update)
    if lang is None:
        return
    user_id = update.effective_user.id

    if not ctx.args:
        await update.message.reply_text(t("share_usage", lang))
        return
    try:
        viewer_id = int(ctx.args[0])
    except ValueError:
        await update.message.reply_text(t("share_invalid", lang))
        return
    if viewer_id == user_id:
        await update.message.reply_text(t("share_self", lang))
        return

    add_share(user_id, viewer_id)
    await update.message.reply_text(t("share_done", lang, id=viewer_id))


async def cmd_unshare(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    lang = await _require_lang(update)
    if lang is None:
        return
    user_id = update.effective_user.id
    if not ctx.args:
        await update.message.reply_text(t("unshare_usage", lang))
        return
    try:
        viewer_id = int(ctx.args[0])
    except ValueError:
        await update.message.reply_text(t("share_invalid", lang))
        return
    remove_share(user_id, viewer_id)
    await update.message.reply_text(t("unshare_done", lang, id=viewer_id))


# ── utility commands ──────────────────────────────────────────────────────────

async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    ensure_user(user_id)
    lang = get_lang(user_id)
    if lang is None:
        await ask_language(update)
        return
    name = update.effective_user.first_name or ""
    await update.message.reply_text(t("welcome", lang, name=name))


async def cmd_help(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    lang = await _require_lang(update)
    if lang is None:
        return
    await update.message.reply_text(t("help", lang))


async def cmd_myid(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = get_lang(user_id) or "en"
    await update.message.reply_text(t("myid", lang, id=user_id))


async def cmd_viewstats(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    viewer_id = update.effective_user.id
    lang = get_lang(viewer_id) or "en"
    owners = get_shared_owners(viewer_id)
    if not owners:
        await update.message.reply_text(t("viewstats_none", lang, id=viewer_id))
        return

    lines = []
    for owner_id in owners:
        stats = get_all_stats(owner_id)
        bal = stats["income"] - stats["expenses"]
        bal_sign = "+" if bal >= 0 else "-"
        lines.append(
            f"👤 {t('user', lang)} {owner_id}\n"
            f"  💸 {t('spent', lang)}: {fmt(stats['expenses'])} UZS\n"
            f"  💵 {t('earned', lang)}: {fmt(stats['income'])} UZS\n"
            f"  💰 {t('balance', lang)}: {bal_sign}{fmt(abs(bal))} UZS"
        )
    await update.message.reply_text(
        f"{t('viewstats_title', lang)}\n\n" + "\n\n".join(lines)
    )
