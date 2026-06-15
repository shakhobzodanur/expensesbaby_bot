# -*- coding: utf-8 -*-
"""All bot texts in English, Russian and Uzbek."""

LANGUAGES = {"en": "English 🇬🇧", "ru": "Русский 🇷🇺", "uz": "O'zbekcha 🇺🇿"}

TEXTS = {
    # ── language picker ──
    "choose_language": {
        "en": "🌐 Please choose your language:",
        "ru": "🌐 Пожалуйста, выберите язык:",
        "uz": "🌐 Iltimos, tilni tanlang:",
    },
    "language_set": {
        "en": "✅ Language set to English.",
        "ru": "✅ Язык изменён на русский.",
        "uz": "✅ Til o'zbekchaga o'zgartirildi.",
    },

    # ── welcome / help ──
    "welcome": {
        "en": ("👋 Hello {name}!\n\n"
               "I track your expenses and income.\n\n"
               "Just send me:\n"
               "  +200000  → income\n"
               "  -45000   → expense\n\n"
               "Commands:\n"
               "/today — today's summary\n"
               "/week — this week\n"
               "/month — this month\n"
               "/all — all time\n"
               "/balance — current balance\n"
               "/setlimit — set daily spending limit\n"
               "/language — change language\n"
               "/myid — your Telegram ID\n"
               "/share — share stats with someone\n"
               "/help — show help"),
        "ru": ("👋 Привет, {name}!\n\n"
               "Я веду учёт ваших расходов и доходов.\n\n"
               "Просто отправьте мне:\n"
               "  +200000  → доход\n"
               "  -45000   → расход\n\n"
               "Команды:\n"
               "/today — итог за сегодня\n"
               "/week — за неделю\n"
               "/month — за месяц\n"
               "/all — за всё время\n"
               "/balance — текущий баланс\n"
               "/setlimit — дневной лимит трат\n"
               "/language — сменить язык\n"
               "/myid — ваш Telegram ID\n"
               "/share — поделиться статистикой\n"
               "/help — помощь"),
        "uz": ("👋 Salom, {name}!\n\n"
               "Men xarajat va daromadlaringizni hisoblab boraman.\n\n"
               "Menga shunchaki yuboring:\n"
               "  +200000  → daromad\n"
               "  -45000   → xarajat\n\n"
               "Buyruqlar:\n"
               "/today — bugungi hisobot\n"
               "/week — shu hafta\n"
               "/month — shu oy\n"
               "/all — umumiy\n"
               "/balance — joriy balans\n"
               "/setlimit — kunlik xarajat limiti\n"
               "/language — tilni o'zgartirish\n"
               "/myid — Telegram ID raqamingiz\n"
               "/share — statistikani ulashish\n"
               "/help — yordam"),
    },
    "help": {
        "en": ("📖 How to use:\n\n"
               "Log money:\n"
               "  +200000 → earned 200,000 UZS\n"
               "  -45000 → spent 45,000 UZS\n\n"
               "After each entry you'll see an ↩️ Undo button.\n\n"
               "Commands:\n"
               "/today /week /month /all — summaries\n"
               "/balance — how much you have now\n"
               "/setlimit <amount> — daily spending limit\n"
               "/language — change language\n"
               "/myid — your Telegram ID\n"
               "/share <id> — share with someone\n"
               "/unshare <id> — remove access\n"
               "/viewstats — see stats shared with you"),
        "ru": ("📖 Как пользоваться:\n\n"
               "Записать деньги:\n"
               "  +200000 → доход 200 000 UZS\n"
               "  -45000 → расход 45 000 UZS\n\n"
               "После каждой записи появится кнопка ↩️ Отменить.\n\n"
               "Команды:\n"
               "/today /week /month /all — сводки\n"
               "/balance — сколько у вас сейчас\n"
               "/setlimit <сумма> — дневной лимит\n"
               "/language — сменить язык\n"
               "/myid — ваш Telegram ID\n"
               "/share <id> — поделиться\n"
               "/unshare <id> — убрать доступ\n"
               "/viewstats — статистика, доступная вам"),
        "uz": ("📖 Qanday foydalaniladi:\n\n"
               "Pulni yozish:\n"
               "  +200000 → 200 000 UZS daromad\n"
               "  -45000 → 45 000 UZS xarajat\n\n"
               "Har bir yozuvdan keyin ↩️ Bekor qilish tugmasi chiqadi.\n\n"
               "Buyruqlar:\n"
               "/today /week /month /all — hisobotlar\n"
               "/balance — hozir qancha mablag'ingiz bor\n"
               "/setlimit <miqdor> — kunlik limit\n"
               "/language — tilni o'zgartirish\n"
               "/myid — Telegram ID raqamingiz\n"
               "/share <id> — ulashish\n"
               "/unshare <id> — ruxsatni olib tashlash\n"
               "/viewstats — sizga ulashilgan statistika"),
    },

    # ── entry labels ──
    "expense": {"en": "🔴 Expense", "ru": "🔴 Расход", "uz": "🔴 Xarajat"},
    "income":  {"en": "✅ Income",  "ru": "✅ Доход",  "uz": "✅ Daromad"},
    "today":   {"en": "📅 Today",   "ru": "📅 Сегодня", "uz": "📅 Bugun"},
    "all_time": {"en": "📊 All Time", "ru": "📊 За всё время", "uz": "📊 Umumiy"},
    "spent":   {"en": "Spent",  "ru": "Расход", "uz": "Xarajat"},
    "earned":  {"en": "Earned", "ru": "Доход",  "uz": "Daromad"},
    "balance": {"en": "Balance", "ru": "Баланс", "uz": "Balans"},

    # ── percentages ──
    "pct_of_balance": {
        "en": "📉 This is {pct}% of your balance",
        "ru": "📉 Это {pct}% от вашего баланса",
        "uz": "📉 Bu balansingizning {pct}% qismi",
    },
    "pct_spent_of_earned": {
        "en": "💡 You've spent {pct}% of all you earned",
        "ru": "💡 Вы потратили {pct}% от всех доходов",
        "uz": "💡 Siz barcha daromadingizning {pct}% ini sarfladingiz",
    },
    "pct_of_earned_income": {
        "en": "📈 This adds {pct}% to your total earnings",
        "ru": "📈 Это добавляет {pct}% к вашим доходам",
        "uz": "📈 Bu umumiy daromadingizga {pct}% qo'shadi",
    },

    # ── daily limit warnings ──
    "limit_near": {
        "en": "⚠️ Careful! You've used {pct}% of your {limit} UZS daily limit.",
        "ru": "⚠️ Осторожно! Вы использовали {pct}% дневного лимита {limit} UZS.",
        "uz": "⚠️ Ehtiyot bo'ling! Kunlik {limit} UZS limitingizning {pct}% ini ishlatdingiz.",
    },
    "limit_over": {
        "en": "🚨 Limit exceeded! Today you spent {spent} UZS — over your {limit} UZS daily limit.",
        "ru": "🚨 Лимит превышен! Сегодня вы потратили {spent} UZS — больше дневного лимита {limit} UZS.",
        "uz": "🚨 Limit oshib ketdi! Bugun {spent} UZS sarfladingiz — kunlik {limit} UZS limitdan ko'p.",
    },

    # ── weekly spike ──
    "week_spike": {
        "en": "📈 Heads up: this week you're spending {pct}% more than last week.",
        "ru": "📈 Внимание: на этой неделе вы тратите на {pct}% больше, чем на прошлой.",
        "uz": "📈 Diqqat: bu hafta o'tgan haftaga qaraganda {pct}% ko'p sarflayapsiz.",
    },

    # ── set limit ──
    "setlimit_usage": {
        "en": "Usage: /setlimit 100000\n(Your current limit: {limit} UZS)",
        "ru": "Использование: /setlimit 100000\n(Текущий лимит: {limit} UZS)",
        "uz": "Foydalanish: /setlimit 100000\n(Joriy limit: {limit} UZS)",
    },
    "setlimit_done": {
        "en": "✅ Daily spending limit set to {limit} UZS.",
        "ru": "✅ Дневной лимит трат установлен: {limit} UZS.",
        "uz": "✅ Kunlik xarajat limiti {limit} UZS qilib belgilandi.",
    },
    "setlimit_invalid": {
        "en": "❌ Please provide a valid number. Example: /setlimit 100000",
        "ru": "❌ Введите корректное число. Пример: /setlimit 100000",
        "uz": "❌ To'g'ri raqam kiriting. Masalan: /setlimit 100000",
    },

    # ── summaries ──
    "sum_today": {"en": "📅 Today's Summary", "ru": "📅 Итог за сегодня", "uz": "📅 Bugungi hisobot"},
    "sum_week":  {"en": "📆 This Week", "ru": "📆 За эту неделю", "uz": "📆 Shu hafta"},
    "sum_month": {"en": "🗓 This Month", "ru": "🗓 За этот месяц", "uz": "🗓 Shu oy"},
    "sum_all":   {"en": "📊 All Time", "ru": "📊 За всё время", "uz": "📊 Umumiy"},
    "cur_balance": {"en": "Current Balance", "ru": "Текущий баланс", "uz": "Joriy balans"},

    # ── undo ──
    "undo_btn":  {"en": "↩️ Undo last entry", "ru": "↩️ Отменить", "uz": "↩️ Bekor qilish"},
    "undo_done": {"en": "↩️ Entry removed.", "ru": "↩️ Запись удалена.", "uz": "↩️ Yozuv o'chirildi."},
    "undo_fail": {
        "en": "❌ Could not undo — already removed.",
        "ru": "❌ Не удалось отменить — уже удалено.",
        "uz": "❌ Bekor qilib bo'lmadi — allaqachon o'chirilgan.",
    },
    "updated": {"en": "Updated", "ru": "Обновлено", "uz": "Yangilandi"},

    # ── errors ──
    "invalid_number": {
        "en": "❌ Invalid number. Example: +200000 or -45000",
        "ru": "❌ Неверное число. Пример: +200000 или -45000",
        "uz": "❌ Noto'g'ri raqam. Masalan: +200000 yoki -45000",
    },

    # ── share ──
    "share_usage": {
        "en": ("ℹ️ To share your stats:\n\n"
               "1. Ask them to send /myid to this bot\n"
               "2. They'll get their Telegram ID\n"
               "3. You send: /share <their_id>"),
        "ru": ("ℹ️ Чтобы поделиться статистикой:\n\n"
               "1. Попросите отправить /myid этому боту\n"
               "2. Они получат свой Telegram ID\n"
               "3. Вы отправляете: /share <их_id>"),
        "uz": ("ℹ️ Statistikangizni ulashish uchun:\n\n"
               "1. Ulardan shu botga /myid yuborishni so'rang\n"
               "2. Ular Telegram ID raqamini oladi\n"
               "3. Siz yuborasiz: /share <ularning_id>"),
    },
    "share_done": {
        "en": "✅ Shared! User {id} can now view your stats with /viewstats.",
        "ru": "✅ Готово! Пользователь {id} теперь видит вашу статистику через /viewstats.",
        "uz": "✅ Ulashildi! {id} foydalanuvchi endi /viewstats orqali statistikangizni ko'radi.",
    },
    "share_self": {
        "en": "❌ You can't share with yourself.",
        "ru": "❌ Нельзя поделиться с самим собой.",
        "uz": "❌ O'zingiz bilan ulasha olmaysiz.",
    },
    "share_invalid": {
        "en": "❌ Provide a valid numeric ID. Example: /share 123456789",
        "ru": "❌ Введите корректный числовой ID. Пример: /share 123456789",
        "uz": "❌ To'g'ri raqamli ID kiriting. Masalan: /share 123456789",
    },
    "unshare_usage": {
        "en": "Usage: /unshare <id>",
        "ru": "Использование: /unshare <id>",
        "uz": "Foydalanish: /unshare <id>",
    },
    "unshare_done": {
        "en": "✅ Access removed for user {id}.",
        "ru": "✅ Доступ для пользователя {id} убран.",
        "uz": "✅ {id} foydalanuvchi uchun ruxsat olib tashlandi.",
    },
    "myid": {
        "en": "🆔 Your Telegram ID: {id}\n\nShare it so someone can give you access.",
        "ru": "🆔 Ваш Telegram ID: {id}\n\nОтправьте его, чтобы вам дали доступ.",
        "uz": "🆔 Telegram ID raqamingiz: {id}\n\nKimdir sizga ruxsat berishi uchun uni ulashing.",
    },
    "viewstats_none": {
        "en": "❌ No one has shared their stats with you yet.\nYour ID: {id}",
        "ru": "❌ Никто ещё не поделился статистикой.\nВаш ID: {id}",
        "uz": "❌ Hali hech kim statistikasini ulashmagan.\nID raqamingiz: {id}",
    },
    "viewstats_title": {
        "en": "📊 Shared Stats", "ru": "📊 Доступная статистика", "uz": "📊 Ulashilgan statistika",
    },
    "user": {"en": "User", "ru": "Пользователь", "uz": "Foydalanuvchi"},

    # ── scheduled ──
    "daily_summary": {"en": "📅 Daily Summary", "ru": "📅 Итог дня", "uz": "📅 Kunlik hisobot"},
    "weekly_summary": {"en": "📆 Weekly Summary", "ru": "📆 Итог недели", "uz": "📆 Haftalik hisobot"},
}


def t(key: str, lang: str, **kwargs) -> str:
    lang = lang if lang in ("en", "ru", "uz") else "en"
    template = TEXTS.get(key, {}).get(lang) or TEXTS.get(key, {}).get("en", key)
    if kwargs:
        return template.format(**kwargs)
    return template
