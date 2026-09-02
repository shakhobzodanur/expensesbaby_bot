import re
import secrets
import logging
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup,
    ReplyKeyboardMarkup, KeyboardButton, InputFile
)
from telegram.ext import ContextTypes
from database import (
    init_db, ensure_user, get_user, get_lang, set_lang,
    is_allowed, allow_user, deny_user, get_allowed_users,
    create_invite_token, use_invite_token, get_owner_id,
    get_currency, set_currency,
    get_daily_limit, set_daily_limit,
    get_monthly_budget, set_monthly_budget,
    get_initial_balance, set_initial_balance,
    is_setup_done, set_setup_done,
    get_reminders_on, set_reminders_on,
    get_categories_on, set_categories_on,
    add_entry, delete_entry,
    get_today_stats, get_week_stats, get_month_stats,
    get_all_stats, get_balance, get_last_week_expenses,
    get_week_by_category, get_month_by_category,
    get_week_daily_totals, get_all_entries,
    add_share, remove_share, get_shared_owners,
    reset_all, reset_today,
    EXPENSE_CATEGORIES,
)
from lang import t, LANGUAGES, CURRENCIES, cat_name
from charts import generate_week_chart
from excel_export import generate_excel

init_db()
logger = logging.getLogger(__name__)

NEAR_THRESHOLD = 0.8
SPIKE_RATIO    = 1.30

_setup_state: dict = {}   # user_id → step name
_awaiting:    dict = {}   # user_id → 'balance'|'limit'|'budget'
_pending_expense: dict = {}  # user_id → {"value": float, "entry_id": int} awaiting category pick


# ── Helpers ────────────────────────────────────────────────────────────────────

def fmt(amount: float) -> str:
    return f"{amount:,.0f}".replace(",", " ")

def pct(part: float, whole: float) -> float:
    return round(part / whole * 100, 1) if whole > 0 else 0.0

def progress_bar(percent: float) -> str:
    p = min(percent, 100)
    if p == 0:
        return "⬜⬜⬜⬜⬜"
    elif p <= 20:
        return "🟩⬜⬜⬜⬜"
    elif p <= 40:
        return "🟩🟩⬜⬜⬜"
    elif p <= 60:
        return "🟨🟨🟨⬜⬜"
    elif p <= 80:
        return "🟧🟧🟧🟧⬜"
    elif p < 100:
        return "🟥🟥🟥🟥🟥"
    else:
        return "🔴🔴🔴🔴🔴"

def get_promo_lang(update: Update) -> str:
    tg_lang = update.effective_user.language_code or "en"
    return "ru" if tg_lang.startswith("ru") else "uz" if tg_lang.startswith("uz") else "en"


# ── Reply keyboard (bottom menu) ──────────────────────────────────────────────

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


# ── Inline keyboards ───────────────────────────────────────────────────────────

def lang_keyboard(prefix="setlang") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(v, callback_data=f"{prefix}:{k}")]
        for k, v in LANGUAGES.items()
    ])

def currency_keyboard(prefix="setcur") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(c, callback_data=f"{prefix}:{c}") for c in CURRENCIES]
    ])

def categories_choice_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(t("categories_yes", lang), callback_data="setup_cat:yes")],
        [InlineKeyboardButton(t("categories_no",  lang), callback_data="setup_cat:no")],
    ])

def category_picker_keyboard(lang: str) -> InlineKeyboardMarkup:
    rows = []
    row = []
    for icon, key in EXPENSE_CATEGORIES:
        row.append(InlineKeyboardButton(f"{icon} {cat_name(key, lang)}", callback_data=f"pickcat:{key}"))
        if len(row) == 2:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    return InlineKeyboardMarkup(rows)

def settings_keyboard(lang: str, categories_on: bool, reminders_on: bool) -> InlineKeyboardMarkup:
    cat_status = "✅" if categories_on else "◻️"
    rem_status = "✅" if reminders_on else "◻️"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(t("set_language", lang), callback_data="cfg:language"),
         InlineKeyboardButton(t("set_currency", lang), callback_data="cfg:currency")],
        [InlineKeyboardButton(t("set_balance",  lang), callback_data="cfg:balance"),
         InlineKeyboardButton(t("set_limit",    lang), callback_data="cfg:limit")],
        [InlineKeyboardButton(t("set_budget",   lang), callback_data="cfg:budget")],
        [InlineKeyboardButton(f"{cat_status} {t('set_categories', lang)}", callback_data="cfg:toggle_cat"),
         InlineKeyboardButton(f"{rem_status} {t('set_reminders', lang)}", callback_data="cfg:toggle_rem")],
        [InlineKeyboardButton(t("export_btn", lang), callback_data="cfg:export")],
        [InlineKeyboardButton(t("reset_today_btn", lang), callback_data="cfg:reset_today"),
         InlineKeyboardButton(t("reset_all_btn",   lang), callback_data="cfg:reset_all")],
    ])

def confirm_keyboard(action: str, lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        InlineKeyboardButton(t("reset_yes", lang), callback_data=f"confirm:{action}:yes"),
        InlineKeyboardButton(t("reset_no",  lang), callback_data=f"confirm:{action}:no"),
    ]])

def invite_share_keyboard(link: str, lang: str) -> InlineKeyboardMarkup:
    share_url = f"https://t.me/share/url?url={link}"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(t("share_button", lang), url=share_url)]
    ])


# ── Setup flow ─────────────────────────────────────────────────────────────────

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
    """Called after balance entered — now ask daily limit."""
    cur = get_currency(user_id)
    set_initial_balance(user_id, amount)
    _setup_state[user_id] = "daily_limit"
    skip_kb = InlineKeyboardMarkup([
        [InlineKeyboardButton(t("skip_btn", lang), callback_data="setup_skip:daily_limit")]
    ])
    await update.message.reply_text(
        t("balance_set", lang, bal=fmt(amount), cur=cur) + "\n\n" +
        t("ask_daily_limit", lang),
        reply_markup=skip_kb
    )

async def _ask_monthly_budget(update_or_query, user_id: int, lang: str, is_callback: bool = False):
    _setup_state[user_id] = "monthly_budget"
    skip_kb = InlineKeyboardMarkup([
        [InlineKeyboardButton(t("skip_btn", lang), callback_data="setup_skip:monthly_budget")]
    ])
    text = t("ask_monthly_budget", lang)
    if is_callback:
        await update_or_query.edit_message_text(text, reply_markup=skip_kb)
    else:
        await update_or_query.message.reply_text(text, reply_markup=skip_kb)

async def _ask_categories(update_or_query, user_id: int, lang: str, is_callback: bool = False):
    _setup_state[user_id] = "categories"
    text = t("ask_categories", lang)
    kb = categories_choice_keyboard(lang)
    if is_callback:
        await update_or_query.edit_message_text(text, reply_markup=kb)
    else:
        await update_or_query.message.reply_text(text, reply_markup=kb)

async def _complete_setup(update_or_query, user_id: int, lang: str, is_callback: bool = False):
    set_setup_done(user_id)
    _setup_state.pop(user_id, None)
    text = t("setup_done", lang)
    if is_callback:
        await update_or_query.edit_message_text(text)
        await update_or_query.message.reply_text("🎉", reply_markup=main_keyboard(lang))
    else:
        await update_or_query.message.reply_text(text, reply_markup=main_keyboard(lang))

async def handle_setup_skip_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    lang    = get_lang(user_id) or "en"
    step    = query.data.split(":")[1]
    if step == "daily_limit":
        await _ask_monthly_budget(query, user_id, lang, is_callback=True)
    elif step == "monthly_budget":
        await _ask_categories(query, user_id, lang, is_callback=True)

async def handle_setup_cat_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    lang    = get_lang(user_id) or "en"
    choice  = query.data.split(":")[1]
    set_categories_on(user_id, choice == "yes")
    await _complete_setup(query, user_id, lang, is_callback=True)


# ── Settings ───────────────────────────────────────────────────────────────────

async def cmd_settings(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_allowed(user_id):
        await update.message.reply_text(t("promo", get_promo_lang(update)), parse_mode="Markdown")
        return
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
        reply_markup=settings_keyboard(lang, get_categories_on(user_id), get_reminders_on(user_id))
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
    elif action == "toggle_cat":
        new_val = not get_categories_on(user_id)
        set_categories_on(user_id, new_val)
        await query.edit_message_text(t("categories_on" if new_val else "categories_off", lang))
    elif action == "toggle_rem":
        new_val = not get_reminders_on(user_id)
        set_reminders_on(user_id, new_val)
        await query.edit_message_text(t("reminders_on" if new_val else "reminders_off", lang))
    elif action == "export":
        await _do_export(query.message, user_id, lang, cur, is_callback_msg=True)
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


# ── Category picker callback ────────────────────────────────────────────────────

async def handle_pickcat_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """User picked a category for their pending expense."""
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    lang    = get_lang(user_id) or "en"
    cur     = get_currency(user_id)
    cat_key = query.data.split(":")[1]

    pending = _pending_expense.pop(user_id, None)
    if not pending:
        await query.edit_message_text(t("generic_error", lang))
        return

    value = pending["value"]
    entry_id = add_entry(user_id, value, "expense", category=cat_key)

    await query.edit_message_text(
        f"{t('expense', lang)}: -{fmt(value)} {cur}\n🏷 {cat_name(cat_key, lang)}"
    )
    await _send_expense_summary(query.message, user_id, lang, cur, value, entry_id)


# ── Text / amount handler ───────────────────────────────────────────────────────

AMOUNT_RE = re.compile(r"^([+-])(\d[\d\s.,]*)$")

async def handle_amount(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if not is_allowed(user_id):
        await update.message.reply_text(t("promo", get_promo_lang(update)), parse_mode="Markdown")
        return

    ensure_user(user_id)
    text = update.message.text.strip()

    # ── setup not done ──
    if not is_setup_done(user_id):
        state = _setup_state.get(user_id)
        lang  = get_lang(user_id) or "en"

        if state == "balance":
            raw = text.replace(" ","").replace(",","").replace(".","")
            try:
                amount = float(raw)
                if amount < 0: raise ValueError
            except ValueError:
                await update.message.reply_text(t("invalid_balance", lang)); return
            await _finish_setup(update, user_id, lang, amount)

        elif state == "daily_limit":
            raw = text.replace(" ","").replace(",","").replace(".","")
            try:
                amount = float(raw)
                if amount < 0: raise ValueError
            except ValueError:
                await update.message.reply_text(t("invalid_balance", lang)); return
            if amount > 0:
                set_daily_limit(user_id, amount)
                cur = get_currency(user_id)
                await update.message.reply_text(t("setlimit_done", lang, limit=fmt(amount), cur=cur))
            await _ask_monthly_budget(update, user_id, lang, is_callback=False)

        elif state == "monthly_budget":
            raw = text.replace(" ","").replace(",","").replace(".","")
            try:
                amount = float(raw)
                if amount < 0: raise ValueError
            except ValueError:
                await update.message.reply_text(t("invalid_balance", lang)); return
            if amount > 0:
                set_monthly_budget(user_id, amount)
                cur = get_currency(user_id)
                await update.message.reply_text(t("budget_set", lang, budget=fmt(amount), cur=cur))
            await _ask_categories(update, user_id, lang, is_callback=False)

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

    # ── if categories are on and this is an expense, ask for category first ──
    if entry_type == "expense" and get_categories_on(user_id):
        _pending_expense[user_id] = {"value": value}
        await update.message.reply_text(
            t("pick_category", lang, amount=fmt(value), cur=cur),
            reply_markup=category_picker_keyboard(lang)
        )
        return

    entry_id = add_entry(user_id, value, entry_type)

    if entry_type == "expense":
        await _send_expense_summary(update.message, user_id, lang, cur, value, entry_id)
    else:
        await _send_income_summary(update.message, user_id, lang, cur, value, entry_id)


async def _send_income_summary(message, user_id, lang, cur, value, entry_id):
    today   = get_today_stats(user_id)
    overall = get_all_stats(user_id)
    bal     = get_balance(user_id)
    bal_sign = "+" if bal >= 0 else "-"

    parts = [
        f"{t('income', lang)}: +{fmt(value)} {cur}\n",
        f"{t('today', lang)}",
        f"  💸 {t('spent', lang)}: {fmt(today['expenses'])} {cur}",
        f"  💵 {t('earned', lang)}: {fmt(today['income'])} {cur}\n",
        f"{t('all_time', lang)}",
        f"  💸 {t('spent', lang)}: {fmt(overall['expenses'])} {cur}",
        f"  💵 {t('earned', lang)}: {fmt(overall['income'])} {cur}",
        f"  💰 {t('balance', lang)}: {bal_sign}{fmt(abs(bal))} {cur}",
    ]
    if overall["income"] > 0:
        parts += ["", t("pct_of_earned_income", lang, pct=pct(value, overall["income"]))]

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(t("undo_btn", lang), callback_data=f"undo:{entry_id}")]
    ])
    await message.reply_text("\n".join(parts), reply_markup=keyboard)


async def _send_expense_summary(message, user_id, lang, cur, value, entry_id):
    today   = get_today_stats(user_id)
    overall = get_all_stats(user_id)
    bal     = get_balance(user_id)
    bal_sign = "+" if bal >= 0 else "-"

    parts = [
        f"{t('expense', lang)}: -{fmt(value)} {cur}\n",
        f"{t('today', lang)}",
        f"  💸 {t('spent', lang)}: {fmt(today['expenses'])} {cur}",
        f"  💵 {t('earned', lang)}: {fmt(today['income'])} {cur}\n",
        f"{t('all_time', lang)}",
        f"  💸 {t('spent', lang)}: {fmt(overall['expenses'])} {cur}",
        f"  💵 {t('earned', lang)}: {fmt(overall['income'])} {cur}",
        f"  💰 {t('balance', lang)}: {bal_sign}{fmt(abs(bal))} {cur}",
    ]

    month_stats  = get_month_stats(user_id)
    limit        = get_daily_limit(user_id)
    budget       = get_monthly_budget(user_id)
    month_inc    = month_stats["income"]
    month_spent  = month_stats["expenses"]

    smart = []
    if limit > 0:
        spent_t   = today["expenses"]
        daily_pct = pct(spent_t, limit)
        smart.append(t("smart_daily", lang, bar=progress_bar(daily_pct), p=daily_pct,
                       spent=fmt(spent_t), limit=fmt(limit), cur=cur))
    if budget > 0:
        bud_pct = pct(month_spent, budget)
        smart.append(t("smart_budget", lang, bar=progress_bar(bud_pct), p=bud_pct,
                       spent=fmt(month_spent), budget=fmt(budget), cur=cur))
    if month_inc > 0:
        inc_pct = pct(month_spent, month_inc)
        smart.append(t("smart_income", lang, bar=progress_bar(inc_pct), p=inc_pct,
                       spent=fmt(month_spent), income=fmt(month_inc), cur=cur))
    if bal > 0:
        bal_pct = pct(value, bal)
        smart.append(t("smart_balance", lang, bar=progress_bar(bal_pct), p=bal_pct,
                       spent=fmt(value), balance=fmt(bal), cur=cur))
    if smart:
        parts += ["", t("smart_title", lang)] + smart

    if limit > 0:
        spent_t = today["expenses"]
        if spent_t >= limit:
            parts += ["", t("limit_over", lang, spent=fmt(spent_t), limit=fmt(limit), cur=cur)]
        elif spent_t >= limit * NEAR_THRESHOLD:
            parts += ["", t("limit_near", lang, pct=pct(spent_t, limit), spent=fmt(spent_t), limit=fmt(limit), cur=cur)]

    if budget > 0:
        if month_spent >= budget:
            parts += ["", t("budget_over", lang, spent=fmt(month_spent), budget=fmt(budget), cur=cur)]
        elif month_spent >= budget * NEAR_THRESHOLD:
            parts += ["", t("budget_warn", lang, pct=pct(month_spent, budget), spent=fmt(month_spent), budget=fmt(budget), cur=cur)]

    this_week = get_week_stats(user_id)["expenses"]
    last_week = get_last_week_expenses(user_id)
    if last_week > 0 and this_week > last_week * SPIKE_RATIO:
        parts += ["", t("week_spike", lang, pct=pct(this_week - last_week, last_week))]

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(t("undo_btn", lang), callback_data=f"undo:{entry_id}")]
    ])
    await message.reply_text("\n".join(parts), reply_markup=keyboard)


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


# ── Summary helpers ────────────────────────────────────────────────────────────

def _sl(stats: dict, lang: str, cur: str) -> str:
    bal = stats["income"] - stats["expenses"]
    sign = "+" if bal >= 0 else "-"
    return (f"💸 {t('spent', lang)}: {fmt(stats['expenses'])} {cur}\n"
            f"💵 {t('earned', lang)}: {fmt(stats['income'])} {cur}\n"
            f"💰 {t('balance', lang)}: {sign}{fmt(abs(bal))} {cur}")

async def _guard(update: Update):
    uid = update.effective_user.id
    if not is_allowed(uid):
        await update.message.reply_text(t("promo", get_promo_lang(update)), parse_mode="Markdown")
        return None, None, None
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
    stats = get_week_stats(uid)
    text = f"{t('sum_week', lang)}\n\n{_sl(stats, lang, cur)}"

    # top category this week (if categories used)
    cats = get_week_by_category(uid)
    if cats:
        top_cat, top_amt = cats[0]
        text += f"\n\n{t('top_category', lang)}: {cat_name(top_cat, lang)} — {fmt(top_amt)} {cur}"

    await update.message.reply_text(text)

    # send weekly chart if there's any expense data
    try:
        daily = get_week_daily_totals(uid)
        if daily:
            chart_buf = generate_week_chart(daily, currency=cur, lang=lang)
            await update.message.reply_photo(
                photo=chart_buf, caption=t("week_chart_caption", lang)
            )
    except Exception as e:
        logger.warning(f"Chart generation failed for user {uid}: {e}")

async def _show_month(update: Update, ctx):
    uid, lang, cur = await _guard(update)
    if uid is None: return
    stats = get_month_stats(uid)
    text = f"{t('sum_month', lang)}\n\n{_sl(stats, lang, cur)}"
    cats = get_month_by_category(uid)
    if cats:
        top_cat, top_amt = cats[0]
        text += f"\n\n{t('top_category', lang)}: {cat_name(top_cat, lang)} — {fmt(top_amt)} {cur}"
    await update.message.reply_text(text)

async def _show_balance(update: Update, ctx):
    uid, lang, cur = await _guard(update)
    if uid is None: return
    bal  = get_balance(uid)
    sign = "+" if bal >= 0 else "-"
    emoji = "🟢" if bal >= 0 else "🔴"
    await update.message.reply_text(
        f"{emoji} {t('cur_balance', lang)}\n\n💰 {sign}{fmt(abs(bal))} {cur}")

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
    promo_lang = get_promo_lang(update)

    if ctx.args and len(ctx.args) > 0:
        token = ctx.args[0]
        if token.startswith("inv"):
            if use_invite_token(token):
                allow_user(user_id)
                await update.message.reply_text(t("invite_used", promo_lang))
                ensure_user(user_id)
                await start_setup(update, user_id)
                return
            else:
                await update.message.reply_text(t("invite_invalid", promo_lang))
                return

    if not is_allowed(user_id):
        await update.message.reply_text(t("promo", promo_lang), parse_mode="Markdown")
        return

    ensure_user(user_id)
    if not is_setup_done(user_id):
        await start_setup(update, user_id); return
    lang = get_lang(user_id) or "en"
    name = update.effective_user.first_name or ""
    await update.message.reply_text(
        t("welcome", lang, name=name), reply_markup=main_keyboard(lang))


# ── Export ────────────────────────────────────────────────────────────────────

async def _do_export(message, user_id: int, lang: str, cur: str, is_callback_msg: bool = False):
    entries = get_all_entries(user_id)
    if not entries:
        await message.reply_text(t("export_empty", lang))
        return
    try:
        bal = get_balance(user_id)
        excel_buf = generate_excel(entries, cur, lang, bal)
        excel_buf.name = "expenses.xlsx"
        await message.reply_document(
            document=excel_buf,
            filename="expenses.xlsx",
            caption=t("export_caption", lang)
        )
    except Exception as e:
        logger.error(f"Export failed for user {user_id}: {e}")
        await message.reply_text(t("generic_error", lang))

async def cmd_export(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid, lang, cur = await _guard(update)
    if uid is None: return
    await update.message.reply_text(t("export_generating", lang))
    await _do_export(update.message, uid, lang, cur)


# ── Admin / Owner commands ──────────────────────────────────────────────────────

async def cmd_allow(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != get_owner_id():
        await update.message.reply_text(t("owner_only", "en")); return
    if not ctx.args:
        await update.message.reply_text(t("allow_usage", "en")); return
    try:
        uid = int(ctx.args[0])
    except ValueError:
        await update.message.reply_text("❌ Invalid ID"); return
    allow_user(uid)
    await update.message.reply_text(t("allow_done", "en", id=uid))

async def cmd_deny(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != get_owner_id():
        await update.message.reply_text(t("owner_only", "en")); return
    if not ctx.args:
        await update.message.reply_text(t("deny_usage", "en")); return
    try:
        uid = int(ctx.args[0])
    except ValueError:
        await update.message.reply_text("❌ Invalid ID"); return
    deny_user(uid)
    await update.message.reply_text(t("deny_done", "en", id=uid))

async def cmd_users(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != get_owner_id():
        await update.message.reply_text(t("owner_only", "en")); return
    users = get_allowed_users()
    if not users:
        await update.message.reply_text(t("users_empty", "en")); return
    lines = [t("users_title", "en"), ""]
    for i, uid in enumerate(users, 1):
        lines.append(f"{i}. {uid}")
    lines.append(f"\nTotal: {len(users)}")
    await update.message.reply_text("\n".join(lines))

async def cmd_invite(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != get_owner_id():
        await update.message.reply_text(t("owner_only", "en")); return
    lang = get_lang(update.effective_user.id) or "en"
    token = "inv" + secrets.token_hex(8)
    create_invite_token(token)
    bot_username = (await ctx.bot.get_me()).username
    link = f"https://t.me/{bot_username}?start={token}"
    await update.message.reply_text(
        t("invite_text", lang, link=link),
        reply_markup=invite_share_keyboard(link, lang)
    )


# ── Share & other utility commands ──────────────────────────────────────────────

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

async def cmd_help(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid, lang, _ = await _guard(update)
    if uid is None: return
    await update.message.reply_text(t("help", lang))

async def cmd_myid(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid  = update.effective_user.id
    lang = get_lang(uid) or "en"
    await update.message.reply_text(t("myid", lang, id=uid))

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


# ── Global error handler ────────────────────────────────────────────────────────

async def error_handler(update: object, ctx: ContextTypes.DEFAULT_TYPE):
    """Catch-all so the bot never crashes on unexpected errors."""
    logger.error(f"Update {update} caused error: {ctx.error}", exc_info=ctx.error)
    try:
        if isinstance(update, Update) and update.effective_message:
            user_id = update.effective_user.id if update.effective_user else None
            lang = get_lang(user_id) if user_id else "en"
            lang = lang or "en"
            await update.effective_message.reply_text(t("generic_error", lang))
    except Exception:
        pass  # never let the error handler itself crash
