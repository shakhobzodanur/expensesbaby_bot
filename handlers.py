import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import (
    init_db, ensure_user, get_user, get_lang, set_lang,
    get_currency, set_currency,
    get_daily_limit, set_daily_limit,
    get_initial_balance, set_initial_balance,
    is_setup_done, set_setup_done,
    add_entry, delete_entry,
    get_today_stats, get_week_stats, get_month_stats,
    get_all_stats, get_balance, get_last_week_expenses,
    add_share, remove_share, get_shared_owners,
    reset_all
)
from lang import t, LANGUAGES, CURRENCIES

init_db()

NEAR_THRESHOLD = 0.8
SPIKE_RATIO    = 1.30

# ─── Setup state tracking (in-memory per user) ───────────────────────────────
# States: 'lang' → 'currency' → 'balance' → done
_setup_state: dict[int, str] = {}


def fmt(amount: float) -> str:
    return f"{amount:,.0f}".replace(",", " ")


def pct(part: float, whole: float) -> float:
    if whole <= 0:
        return 0.0
    return round(part / whole * 100, 1)


# ─── Keyboards ────────────────────────────────────────────────────────────────

def lang_keyboard(prefix: str = "setlang") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(v, callback_data=f"{prefix}:{k}")]
        for k, v in LANGUAGES.items()
    ])


def currency_keyboard(prefix: str = "setcur") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(c, callback_data=f"{prefix}:{c}") for c in CURRENCIES]
    ])


def settings_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(t("set_language", lang), callback_data="cfg:language")],
        [InlineKeyboardButton(t("set_currency", lang), callback_data="cfg:currency")],
        [InlineKeyboardButton(t("set_balance",  lang), callback_data="cfg:balance")],
        [InlineKeyboardButton(t("set_limit",    lang), callback_data="cfg:limit")],
        [InlineKeyboardButton(t("reset_all_btn", lang), callback_data="cfg:reset")],
    ])


def confirm_reset_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(t("reset_yes", lang), callback_data="reset:yes"),
         InlineKeyboardButton(t("reset_no",  lang), callback_data="reset:no")],
    ])


# ─── Setup flow ───────────────────────────────────────────────────────────────

async def start_setup(update: Update, user_id: int):
    ensure_user(user_id)
    _setup_state[user_id] = "lang"
    await update.message.reply_text(
        "🌐 Choose your language / Выберите язык / Tilni tanlang:",
        reply_markup=lang_keyboard("setup_lang")
    )


async def handle_setup_lang_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    lang = query.data.split(":")[1]
    set_lang(user_id, lang)
    _setup_state[user_id] = "currency"
    await query.edit_message_text(
        t("choose_currency", lang),
        reply_markup=currency_keyboard("setup_cur")
    )


async def handle_setup_cur_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    cur = query.data.split(":")[1]
    set_currency(user_id, cur)
    lang = get_lang(user_id) or "en"
    _setup_state[user_id] = "balance"
    await query.edit_message_text(t("enter_balance", lang))


async def handle_setup_balance_input(update: Update, user_id: int, lang: str):
    raw = update.message.text.strip().replace(" ", "").replace(",", "").replace(".", "")
    try:
        amount = float(raw)
        if amount < 0:
            raise ValueError
    except ValueError:
        await update.message.reply_text(t("invalid_balance", lang))
        return

    cur = get_currency(user_id)
    set_initial_balance(user_id, amount)
    set_setup_done(user_id)
    _setup_state.pop(user_id, None)
    name = update.effective_user.first_name or ""
    await update.message.reply_text(
        t("balance_set", lang, bal=fmt(amount), cur=cur) + "\n\n" +
        t("setup_done", lang)
    )


# ─── Settings flow ────────────────────────────────────────────────────────────

# track who is waiting to type a balance / limit in settings
_awaiting: dict[int, str] = {}  # user_id → 'balance' | 'limit'


async def cmd_settings(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_setup_done(user_id):
        await start_setup(update, user_id)
        return
    lang = get_lang(user_id) or "en"
    cur  = get_currency(user_id)
    bal  = get_balance(user_id)
    lim  = get_daily_limit(user_id)
    sign = "+" if bal >= 0 else "-"
    info = (
        f"💰 {t('balance', lang)}: {sign}{fmt(abs(bal))} {cur}\n"
        f"🎯 {t('set_limit', lang)}: {fmt(lim)} {cur}\n"
        f"💱 {cur}  🌐 {LANGUAGES[lang]}"
    )
    await update.message.reply_text(
        f"{t('settings_title', lang)}\n\n{info}",
        reply_markup=settings_keyboard(lang)
    )


async def handle_cfg_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    lang = get_lang(user_id) or "en"
    action = query.data.split(":")[1]

    if action == "language":
        await query.edit_message_text(
            t("choose_language", lang), reply_markup=lang_keyboard("setlang")
        )
    elif action == "currency":
        await query.edit_message_text(
            t("choose_currency", lang), reply_markup=currency_keyboard("setcur")
        )
    elif action == "balance":
        _awaiting[user_id] = "balance"
        await query.edit_message_text(t("enter_balance", lang))
    elif action == "limit":
        cur = get_currency(user_id)
        lim = get_daily_limit(user_id)
        _awaiting[user_id] = "limit"
        await query.edit_message_text(t("setlimit_usage", lang, limit=fmt(lim), cur=cur))
    elif action == "reset":
        await query.edit_message_text(
            t("reset_confirm", lang), reply_markup=confirm_reset_keyboard(lang)
        )


async def handle_setlang_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    lang = query.data.split(":")[1]
    set_lang(user_id, lang)
    await query.edit_message_text(t("language_set", lang))


async def handle_setcur_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    cur = query.data.split(":")[1]
    set_currency(user_id, cur)
    lang = get_lang(user_id) or "en"
    await query.edit_message_text(t("currency_set", lang, cur=cur))


async def handle_reset_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    lang = get_lang(user_id) or "en"
    action = query.data.split(":")[1]
    if action == "yes":
        reset_all(user_id)
        await query.edit_message_text(t("reset_done", lang))
    else:
        await query.edit_message_text(t("reset_cancelled", lang))


# ─── Main amount / text handler ───────────────────────────────────────────────

AMOUNT_RE = re.compile(r"^([+-])(\d[\d\s.,]*)$")


async def handle_amount(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    ensure_user(user_id)

    # ── setup not done ──
    if not is_setup_done(user_id):
        state = _setup_state.get(user_id)
        if state == "balance":
            lang = get_lang(user_id) or "en"
            await handle_setup_balance_input(update, user_id, lang)
        elif state == "limit":
            lang = get_lang(user_id) or "en"
            await handle_awaiting_input(update, user_id, lang)
        elif state is None:
            await start_setup(update, user_id)
        return

    lang = get_lang(user_id) or "en"
    cur  = get_currency(user_id)

    # ── waiting for balance or limit update ──
    if user_id in _awaiting:
        await handle_awaiting_input(update, user_id, lang)
        return

    # ── parse amount ──
    raw = update.message.text.strip().replace(" ", "").replace(",", ".")
    match = AMOUNT_RE.match(raw)
    if not match:
        return  # silently ignore non-commands

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
    entry_id   = add_entry(user_id, value, entry_type)

    today   = get_today_stats(user_id)
    overall = get_all_stats(user_id)
    bal     = get_balance(user_id)
    bal_sign = "+" if bal >= 0 else "-"
    amt_sign = "+" if entry_type == "income" else "-"

    parts = [
        f"{t(entry_type, lang)}: {amt_sign}{fmt(value)} {cur}\n",
        f"{t('today', lang)}",
        f"  💸 {t('spent', lang)}: {fmt(today['expenses'])} {cur}",
        f"  💵 {t('earned', lang)}: {fmt(today['income'])} {cur}\n",
        f"{t('all_time', lang)}",
        f"  💸 {t('spent', lang)}: {fmt(overall['expenses'])} {cur}",
        f"  💵 {t('earned', lang)}: {fmt(overall['income'])} {cur}",
        f"  💰 {t('balance', lang)}: {bal_sign}{fmt(abs(bal))} {cur}",
    ]

    # percentages
    if entry_type == "expense":
        if bal > 0:
            parts += ["", t("pct_of_balance", lang, pct=pct(value, bal))]
        if overall["income"] > 0:
            parts.append(t("pct_spent_of_earned", lang, pct=pct(overall["expenses"], overall["income"])))

        # daily limit warning
        limit = get_daily_limit(user_id)
        if limit > 0:
            spent_today = today["expenses"]
            if spent_today >= limit:
                parts += ["", t("limit_over", lang, spent=fmt(spent_today), limit=fmt(limit), cur=cur)]
            elif spent_today >= limit * NEAR_THRESHOLD:
                parts += ["", t("limit_near", lang, pct=pct(spent_today, limit), limit=fmt(limit), cur=cur)]

        # weekly spike
        this_week = get_week_stats(user_id)["expenses"]
        last_week = get_last_week_expenses(user_id)
        if last_week > 0 and this_week > last_week * SPIKE_RATIO:
            parts += ["", t("week_spike", lang, pct=pct(this_week - last_week, last_week))]
    else:
        if overall["income"] > 0:
            parts += ["", t("pct_of_earned_income", lang, pct=pct(value, overall["income"]))]

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(t("undo_btn", lang), callback_data=f"undo:{entry_id}")]
    ])
    await update.message.reply_text("\n".join(parts), reply_markup=keyboard)


async def handle_awaiting_input(update: Update, user_id: int, lang: str):
    what = _awaiting.get(user_id)
    raw = update.message.text.strip().replace(" ", "").replace(",", "").replace(".", "")
    try:
        amount = float(raw)
        if amount < 0:
            raise ValueError
    except ValueError:
        await update.message.reply_text(t("invalid_balance", lang))
        return

    cur = get_currency(user_id)
    if what == "balance":
        set_initial_balance(user_id, amount)
        _awaiting.pop(user_id, None)
        await update.message.reply_text(t("balance_set", lang, bal=fmt(amount), cur=cur))
    elif what == "limit":
        set_daily_limit(user_id, amount)
        _awaiting.pop(user_id, None)
        await update.message.reply_text(t("setlimit_done", lang, limit=fmt(amount), cur=cur))


async def handle_undo_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id  = update.effective_user.id
    lang     = get_lang(user_id) or "en"
    cur      = get_currency(user_id)
    entry_id = int(query.data.split(":")[1])

    if delete_entry(entry_id, user_id):
        overall  = get_all_stats(user_id)
        bal      = get_balance(user_id)
        bal_sign = "+" if bal >= 0 else "-"
        text = (
            f"{t('undo_done', lang)}\n\n"
            f"📊 {t('updated', lang)}\n"
            f"  💸 {t('spent', lang)}: {fmt(overall['expenses'])} {cur}\n"
            f"  💵 {t('earned', lang)}: {fmt(overall['income'])} {cur}\n"
            f"  💰 {t('balance', lang)}: {bal_sign}{fmt(abs(bal))} {cur}"
        )
        await query.edit_message_text(text)
    else:
        await query.edit_message_text(t("undo_fail", lang))


# ─── Summary commands ─────────────────────────────────────────────────────────

def _sl(stats: dict, lang: str, cur: str) -> str:
    bal = stats["income"] - stats["expenses"]
    sign = "+" if bal >= 0 else "-"
    return (
        f"💸 {t('spent', lang)}: {fmt(stats['expenses'])} {cur}\n"
        f"💵 {t('earned', lang)}: {fmt(stats['income'])} {cur}\n"
        f"💰 {t('balance', lang)}: {sign}{fmt(abs(bal))} {cur}"
    )


async def _guard(update: Update) -> tuple:
    user_id = update.effective_user.id
    if not is_setup_done(user_id):
        await start_setup(update, user_id)
        return None, None, None
    return user_id, get_lang(user_id) or "en", get_currency(user_id)


async def cmd_today(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid, lang, cur = await _guard(update)
    if uid is None: return
    await update.message.reply_text(f"{t('sum_today', lang)}\n\n{_sl(get_today_stats(uid), lang, cur)}")


async def cmd_week(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid, lang, cur = await _guard(update)
    if uid is None: return
    await update.message.reply_text(f"{t('sum_week', lang)}\n\n{_sl(get_week_stats(uid), lang, cur)}")


async def cmd_month(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid, lang, cur = await _guard(update)
    if uid is None: return
    await update.message.reply_text(f"{t('sum_month', lang)}\n\n{_sl(get_month_stats(uid), lang, cur)}")


async def cmd_all(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid, lang, cur = await _guard(update)
    if uid is None: return
    await update.message.reply_text(f"{t('sum_all', lang)}\n\n{_sl(get_all_stats(uid), lang, cur)}")


async def cmd_balance(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid, lang, cur = await _guard(update)
    if uid is None: return
    bal  = get_balance(uid)
    sign = "+" if bal >= 0 else "-"
    emoji = "🟢" if bal >= 0 else "🔴"
    await update.message.reply_text(f"{emoji} {t('cur_balance', lang)}\n\n💰 {sign}{fmt(abs(bal))} {cur}")


async def cmd_setlimit(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid, lang, cur = await _guard(update)
    if uid is None: return
    if not ctx.args:
        _awaiting[uid] = "limit"
        lim = get_daily_limit(uid)
        await update.message.reply_text(t("setlimit_usage", lang, limit=fmt(lim), cur=cur))
        return
    raw = ctx.args[0].replace(" ", "").replace(",", "").replace(".", "")
    try:
        limit = float(raw)
        if limit <= 0: raise ValueError
    except ValueError:
        await update.message.reply_text(t("setlimit_invalid", lang))
        return
    set_daily_limit(uid, limit)
    await update.message.reply_text(t("setlimit_done", lang, limit=fmt(limit), cur=cur))


async def cmd_language(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid, lang, _ = await _guard(update)
    if uid is None: return
    await update.message.reply_text(t("choose_language", lang), reply_markup=lang_keyboard())


# ─── Share & utility commands ─────────────────────────────────────────────────

async def cmd_share(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid, lang, _ = await _guard(update)
    if uid is None: return
    if not ctx.args:
        await update.message.reply_text(t("share_usage", lang)); return
    try: viewer_id = int(ctx.args[0])
    except ValueError:
        await update.message.reply_text(t("share_invalid", lang)); return
    if viewer_id == uid:
        await update.message.reply_text(t("share_self", lang)); return
    add_share(uid, viewer_id)
    await update.message.reply_text(t("share_done", lang, id=viewer_id))


async def cmd_unshare(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid, lang, _ = await _guard(update)
    if uid is None: return
    if not ctx.args:
        await update.message.reply_text(t("unshare_usage", lang)); return
    try: viewer_id = int(ctx.args[0])
    except ValueError:
        await update.message.reply_text(t("share_invalid", lang)); return
    remove_share(uid, viewer_id)
    await update.message.reply_text(t("unshare_done", lang, id=viewer_id))


async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    ensure_user(user_id)
    if not is_setup_done(user_id):
        await start_setup(update, user_id)
        return
    lang = get_lang(user_id) or "en"
    name = update.effective_user.first_name or ""
    await update.message.reply_text(t("welcome", lang, name=name))


async def cmd_help(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid, lang, _ = await _guard(update)
    if uid is None: return
    await update.message.reply_text(t("help", lang))


async def cmd_myid(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = get_lang(user_id) or "en"
    await update.message.reply_text(t("myid", lang, id=user_id))


async def cmd_viewstats(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    viewer_id = update.effective_user.id
    lang = get_lang(viewer_id) or "en"
    cur  = get_currency(viewer_id)
    owners = get_shared_owners(viewer_id)
    if not owners:
        await update.message.reply_text(t("viewstats_none", lang, id=viewer_id)); return
    lines = []
    for oid in owners:
        s = get_all_stats(oid)
        bal = get_balance(oid)
        sign = "+" if bal >= 0 else "-"
        lines.append(
            f"👤 {t('user', lang)} {oid}\n"
            f"  💸 {t('spent', lang)}: {fmt(s['expenses'])} {cur}\n"
            f"  💵 {t('earned', lang)}: {fmt(s['income'])} {cur}\n"
            f"  💰 {t('balance', lang)}: {sign}{fmt(abs(bal))} {cur}"
        )
    await update.message.reply_text(f"{t('viewstats_title', lang)}\n\n" + "\n\n".join(lines))
