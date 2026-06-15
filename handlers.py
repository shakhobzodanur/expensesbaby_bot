import re
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup,
    ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
)
from telegram.ext import ContextTypes
from database import (
    init_db, ensure_user, get_user, get_lang, set_lang,
    get_currency, set_currency,
    get_daily_limit, set_daily_limit,
    get_monthly_budget, set_monthly_budget,
    get_initial_balance, set_initial_balance,
    is_setup_done, set_setup_done,
    add_entry, delete_entry,
    get_today_stats, get_week_stats, get_month_stats,
    get_all_stats, get_balance, get_last_week_expenses,
    add_share, remove_share, get_shared_owners,
    reset_all, reset_today
)
from lang import t, LANGUAGES, CURRENCIES

init_db()

NEAR_THRESHOLD = 0.8
SPIKE_RATIO    = 1.30

_setup_state: dict = {}   # user_id → 'lang'|'currency'|'balance'
_awaiting:    dict = {}   # user_id → 'balance'|'limit'|'budget'


# ─── Helpers ──────────────────────────────────────────────────────────────────

def fmt(amount: float) -> str:
    return f"{amount:,.0f}".replace(",", " ")

def pct(part: float, whole: float) -> float:
    return round(part / whole * 100, 1) if whole > 0 else 0.0


# ─── Reply keyboard (bottom menu) ────────────────────────────────────────────

def main_keyboard(lang: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton(t("btn_today", lang)),   KeyboardButton(t("btn_week", lang))],
            [KeyboardButton(t("btn_month", lang)),   KeyboardButton(t("btn_balance", lang))],
            [KeyboardButton(t("btn_settings", lang)),KeyboardButton(t("btn_help", lang))],
        ],
        resize_keyboard=True,
        is_persistent=True,
    )


# ─── Inline keyboards ─────────────────────────────────────────────────────────

def lang_keyboard(prefix="setlang") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(v, callback_data=f"{prefix}:{k}")]
        for k, v in LANGUAGES.items()
    ])

def currency_keyboard(prefix="setcur") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(c, callback_data=f"{prefix}:{c}") for c in CURRENCIES]
    ])

def settings_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(t("set_language", lang), callback_data="cfg:language"),
         InlineKeyboardButton(t("set_currency", lang), callback_data="cfg:currency")],
        [InlineKeyboardButton(t("set_balance",  lang), callback_data="cfg:balance"),
         InlineKeyboardButton(t("set_limit",    lang), callback_data="cfg:limit")],
        [InlineKeyboardButton(t("set_budget",   lang), callback_data="cfg:budget")],
        [InlineKeyboardButton(t("reset_today_btn", lang), callback_data="cfg:reset_today"),
         InlineKeyboardButton(t("reset_all_btn",   lang), callback_data="cfg:reset_all")],
    ])

def confirm_keyboard(action: str, lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        InlineKeyboardButton(t("reset_yes", lang), callback_data=f"confirm:{action}:yes"),
        InlineKeyboardButton(t("reset_no",  lang), callback_data=f"confirm:{action}:no"),
    ]])


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
    await query.edit_message_text(t("choose_currency", lang),
                                  reply_markup=currency_keyboard("setup_cur"))

async def handle_setup_cur_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    cur = query.data.split(":")[1]
    set_currency(user_id, cur)
    lang = get_lang(user_id) or "en"
    _setup_state[user_id] = "balance"
    await query.edit_message_text(t("enter_balance", lang))

async def _finish_setup(update: Update, user_id: int, lang: str, amount: float):
    cur = get_currency(user_id)
    set_initial_balance(user_id, amount)
    set_setup_done(user_id)
    _setup_state.pop(user_id, None)
    name = update.effective_user.first_name or ""
    await update.message.reply_text(
        t("balance_set", lang, bal=fmt(amount), cur=cur) + "\n\n" + t("setup_done", lang),
        reply_markup=main_keyboard(lang)
    )


# ─── Settings ─────────────────────────────────────────────────────────────────

async def cmd_settings(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_setup_done(user_id):
        await start_setup(update, user_id); return
    lang = get_lang(user_id) or "en"
    cur  = get_currency(user_id)
    bal  = get_balance(user_id)
    lim  = get_daily_limit(user_id)
    bud  = get_monthly_budget(user_id)
    sign = "+" if bal >= 0 else "-"
    info = (
        f"💰 {t('balance', lang)}: {sign}{fmt(abs(bal))} {cur}\n"
        f"🎯 {t('set_limit', lang)}: {fmt(lim)} {cur}\n"
        f"📊 {t('set_budget', lang)}: {fmt(bud) if bud > 0 else '—'} {cur if bud > 0 else ''}\n"
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
    lang    = get_lang(user_id) or "en"
    cur     = get_currency(user_id)
    action  = query.data.split(":")[1]

    if action == "language":
        await query.edit_message_text(t("choose_language", lang),
                                      reply_markup=lang_keyboard("setlang"))
    elif action == "currency":
        await query.edit_message_text(t("choose_currency", lang),
                                      reply_markup=currency_keyboard("setcur"))
    elif action == "balance":
        _awaiting[user_id] = "balance"
        await query.edit_message_text(t("enter_balance", lang))
    elif action == "limit":
        _awaiting[user_id] = "limit"
        lim = get_daily_limit(user_id)
        await query.edit_message_text(t("setlimit_usage", lang, limit=fmt(lim), cur=cur))
    elif action == "budget":
        _awaiting[user_id] = "budget"
        await query.edit_message_text(t("enter_budget", lang))
    elif action == "reset_today":
        await query.edit_message_text(
            t("reset_today_confirm", lang),
            reply_markup=confirm_keyboard("today", lang))
    elif action == "reset_all":
        await query.edit_message_text(
            t("reset_confirm", lang),
            reply_markup=confirm_keyboard("all", lang))

async def handle_setlang_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    lang = query.data.split(":")[1]
    set_lang(user_id, lang)
    await query.edit_message_text(t("language_set", lang))
    # refresh keyboard in correct language
    await query.message.reply_text("✅", reply_markup=main_keyboard(lang))

async def handle_setcur_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    cur  = query.data.split(":")[1]
    lang = get_lang(user_id) or "en"
    set_currency(user_id, cur)
    await query.edit_message_text(t("currency_set", lang, cur=cur))

async def handle_confirm_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    lang    = get_lang(user_id) or "en"
    _, action, choice = query.data.split(":")
    if choice == "no":
        await query.edit_message_text(t("reset_cancelled", lang)); return
    if action == "all":
        reset_all(user_id)
        await query.edit_message_text(t("reset_done", lang))
    elif action == "today":
        reset_today(user_id)
        await query.edit_message_text(t("reset_today_done", lang))


# ─── Text/amount handler ──────────────────────────────────────────────────────

AMOUNT_RE = re.compile(r"^([+-])(\d[\d\s.,]*)$")

async def handle_amount(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    ensure_user(user_id)
    text = update.message.text.strip()

    # ── setup not done ──
    if not is_setup_done(user_id):
        state = _setup_state.get(user_id)
        if state == "balance":
            lang = get_lang(user_id) or "en"
            raw = text.replace(" ","").replace(",","").replace(".","")
            try:
                amount = float(raw)
                if amount < 0: raise ValueError
            except ValueError:
                await update.message.reply_text(t("invalid_balance", lang)); return
            await _finish_setup(update, user_id, lang, amount)
        else:
            await start_setup(update, user_id)
        return

    lang = get_lang(user_id) or "en"
    cur  = get_currency(user_id)

    # ── menu button taps ──
    btn_map = {
        t("btn_today",    lang): _show_today,
        t("btn_week",     lang): _show_week,
        t("btn_month",    lang): _show_month,
        t("btn_balance",  lang): _show_balance,
        t("btn_settings", lang): cmd_settings,
        t("btn_help",     lang): cmd_help,
    }
    if text in btn_map:
        await btn_map[text](update, ctx)
        return

    # ── awaiting typed input (balance / limit / budget) ──
    if user_id in _awaiting:
        what = _awaiting[user_id]
        raw = text.replace(" ","").replace(",","").replace(".","")
        try:
            amount = float(raw)
            if amount < 0: raise ValueError
        except ValueError:
            await update.message.reply_text(t("invalid_balance", lang)); return
        if what == "balance":
            set_initial_balance(user_id, amount)
            _awaiting.pop(user_id)
            await update.message.reply_text(t("balance_set", lang, bal=fmt(amount), cur=cur))
        elif what == "limit":
            set_daily_limit(user_id, amount)
            _awaiting.pop(user_id)
            await update.message.reply_text(t("setlimit_done", lang, limit=fmt(amount), cur=cur))
        elif what == "budget":
            set_monthly_budget(user_id, amount)
            _awaiting.pop(user_id)
            await update.message.reply_text(t("budget_set", lang, budget=fmt(amount), cur=cur))
        return

    # ── parse +/- amount ──
    raw = text.replace(" ","").replace(",",".")
    match = AMOUNT_RE.match(raw)
    if not match:
        return  # ignore unrecognised text

    sign = match.group(1)
    try:
        value = float(match.group(2))
    except ValueError:
        await update.message.reply_text(t("invalid_number", lang)); return
    if value <= 0:
        await update.message.reply_text(t("invalid_number", lang)); return

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

    if entry_type == "expense":
        if bal > 0:
            parts += ["", t("pct_of_balance", lang, pct=pct(value, bal))]
        if overall["income"] > 0:
            parts.append(t("pct_spent_of_earned", lang, pct=pct(overall["expenses"], overall["income"])))

        # daily limit
        limit = get_daily_limit(user_id)
        if limit > 0:
            spent_t = today["expenses"]
            if spent_t >= limit:
                parts += ["", t("limit_over", lang, spent=fmt(spent_t), limit=fmt(limit), cur=cur)]
            elif spent_t >= limit * NEAR_THRESHOLD:
                parts += ["", t("limit_near", lang, pct=pct(spent_t, limit), spent=fmt(spent_t), limit=fmt(limit), cur=cur)]

        # monthly budget
        budget = get_monthly_budget(user_id)
        if budget > 0:
            month_spent = get_month_stats(user_id)["expenses"]
            if month_spent >= budget:
                parts += ["", t("budget_over", lang, spent=fmt(month_spent), budget=fmt(budget), cur=cur)]
            elif month_spent >= budget * NEAR_THRESHOLD:
                parts += ["", t("budget_warn", lang, pct=pct(month_spent, budget), spent=fmt(month_spent), budget=fmt(budget), cur=cur)]

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
        sign     = "+" if bal >= 0 else "-"
        text = (f"{t('undo_done', lang)}\n\n"
                f"📊 {t('updated', lang)}\n"
                f"  💸 {t('spent', lang)}: {fmt(overall['expenses'])} {cur}\n"
                f"  💵 {t('earned', lang)}: {fmt(overall['income'])} {cur}\n"
                f"  💰 {t('balance', lang)}: {sign}{fmt(abs(bal))} {cur}")
        await query.edit_message_text(text)
    else:
        await query.edit_message_text(t("undo_fail", lang))


# ─── Summary helpers ──────────────────────────────────────────────────────────

def _sl(stats: dict, lang: str, cur: str) -> str:
    bal = stats["income"] - stats["expenses"]
    sign = "+" if bal >= 0 else "-"
    return (f"💸 {t('spent', lang)}: {fmt(stats['expenses'])} {cur}\n"
            f"💵 {t('earned', lang)}: {fmt(stats['income'])} {cur}\n"
            f"💰 {t('balance', lang)}: {sign}{fmt(abs(bal))} {cur}")

async def _guard(update: Update):
    uid = update.effective_user.id
    if not is_setup_done(uid):
        await start_setup(update, uid)
        return None, None, None
    return uid, get_lang(uid) or "en", get_currency(uid)

async def _show_today(update: Update, ctx):
    uid, lang, cur = await _guard(update)
    if uid is None: return
    await update.message.reply_text(
        f"{t('sum_today', lang)}\n\n{_sl(get_today_stats(uid), lang, cur)}")

async def _show_week(update: Update, ctx):
    uid, lang, cur = await _guard(update)
    if uid is None: return
    await update.message.reply_text(
        f"{t('sum_week', lang)}\n\n{_sl(get_week_stats(uid), lang, cur)}")

async def _show_month(update: Update, ctx):
    uid, lang, cur = await _guard(update)
    if uid is None: return
    await update.message.reply_text(
        f"{t('sum_month', lang)}\n\n{_sl(get_month_stats(uid), lang, cur)}")

async def _show_balance(update: Update, ctx):
    uid, lang, cur = await _guard(update)
    if uid is None: return
    bal  = get_balance(uid)
    sign = "+" if bal >= 0 else "-"
    emoji = "🟢" if bal >= 0 else "🔴"
    await update.message.reply_text(
        f"{emoji} {t('cur_balance', lang)}\n\n💰 {sign}{fmt(abs(bal))} {cur}")

# public aliases for CommandHandlers
async def cmd_today(update, ctx):  await _show_today(update, ctx)
async def cmd_week(update, ctx):   await _show_week(update, ctx)
async def cmd_month(update, ctx):  await _show_month(update, ctx)
async def cmd_balance(update, ctx):await _show_balance(update, ctx)

async def cmd_all(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid, lang, cur = await _guard(update)
    if uid is None: return
    stats = get_all_stats(uid)
    bal   = get_balance(uid)
    sign  = "+" if bal >= 0 else "-"
    await update.message.reply_text(
        f"{t('sum_all', lang)}\n\n"
        f"💸 {t('spent', lang)}: {fmt(stats['expenses'])} {cur}\n"
        f"💵 {t('earned', lang)}: {fmt(stats['income'])} {cur}\n"
        f"💰 {t('cur_balance', lang)}: {sign}{fmt(abs(bal))} {cur}")

async def cmd_setlimit(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid, lang, cur = await _guard(update)
    if uid is None: return
    if ctx.args:
        raw = ctx.args[0].replace(",","").replace(".","")
        try:
            lim = float(raw)
            if lim <= 0: raise ValueError
            set_daily_limit(uid, lim)
            await update.message.reply_text(t("setlimit_done", lang, limit=fmt(lim), cur=cur))
        except ValueError:
            await update.message.reply_text(t("setlimit_invalid", lang))
    else:
        _awaiting[uid] = "limit"
        await update.message.reply_text(
            t("setlimit_usage", lang, limit=fmt(get_daily_limit(uid)), cur=cur))

async def cmd_language(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid, lang, _ = await _guard(update)
    if uid is None: return
    await update.message.reply_text(t("choose_language", lang), reply_markup=lang_keyboard())

async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    ensure_user(user_id)
    if not is_setup_done(user_id):
        await start_setup(update, user_id); return
    lang = get_lang(user_id) or "en"
    name = update.effective_user.first_name or ""
    await update.message.reply_text(
        t("welcome", lang, name=name), reply_markup=main_keyboard(lang))

async def cmd_help(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid, lang, _ = await _guard(update)
    if uid is None: return
    await update.message.reply_text(t("help", lang))

async def cmd_myid(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid  = update.effective_user.id
    lang = get_lang(uid) or "en"
    await update.message.reply_text(t("myid", lang, id=uid))

async def cmd_share(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid, lang, _ = await _guard(update)
    if uid is None: return
    if not ctx.args:
        await update.message.reply_text(t("share_usage", lang)); return
    try: vid = int(ctx.args[0])
    except ValueError:
        await update.message.reply_text(t("share_invalid", lang)); return
    if vid == uid:
        await update.message.reply_text(t("share_self", lang)); return
    add_share(uid, vid)
    await update.message.reply_text(t("share_done", lang, id=vid))

async def cmd_unshare(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid, lang, _ = await _guard(update)
    if uid is None: return
    if not ctx.args:
        await update.message.reply_text(t("unshare_usage", lang)); return
    try: vid = int(ctx.args[0])
    except ValueError:
        await update.message.reply_text(t("share_invalid", lang)); return
    remove_share(uid, vid)
    await update.message.reply_text(t("unshare_done", lang, id=vid))

async def cmd_viewstats(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid  = update.effective_user.id
    lang = get_lang(uid) or "en"
    cur  = get_currency(uid)
    owners = get_shared_owners(uid)
    if not owners:
        await update.message.reply_text(t("viewstats_none", lang, id=uid)); return
    lines = []
    for oid in owners:
        s   = get_all_stats(oid)
        bal = get_balance(oid)
        sign = "+" if bal >= 0 else "-"
        lines.append(
            f"👤 {t('user', lang)} {oid}\n"
            f"  💸 {t('spent', lang)}: {fmt(s['expenses'])} {cur}\n"
            f"  💵 {t('earned', lang)}: {fmt(s['income'])} {cur}\n"
            f"  💰 {t('balance', lang)}: {sign}{fmt(abs(bal))} {cur}")
    await update.message.reply_text(
        f"{t('viewstats_title', lang)}\n\n" + "\n\n".join(lines))
