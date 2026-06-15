# -*- coding: utf-8 -*-
LANGUAGES = {"en": "English 🇬🇧", "ru": "Русский 🇷🇺", "uz": "O'zbekcha 🇺🇿"}
CURRENCIES = ["UZS", "USD", "RUB"]

TEXTS = {
    # setup flow
    "choose_language":   {"en": "🌐 Choose your language:", "ru": "🌐 Выберите язык:", "uz": "🌐 Tilni tanlang:"},
    "choose_currency":   {"en": "💱 Choose your currency:", "ru": "💱 Выберите валюту:", "uz": "💱 Valyutani tanlang:"},
    "enter_balance":     {
        "en": "💰 What is your current balance?\n\nType the amount (e.g. 5000000) or 0 to start from zero:",
        "ru": "💰 Какой у вас текущий баланс?\n\nВведите сумму (например 5000000) или 0 чтобы начать с нуля:",
        "uz": "💰 Hozirgi balansingiz qancha?\n\nSummani kiriting (masalan 5000000) yoki 0 dan boshlash uchun 0:",
    },
    "balance_set":       {"en": "✅ Balance set to {bal} {cur}.", "ru": "✅ Баланс установлен: {bal} {cur}.", "uz": "✅ Balans {bal} {cur} qilib belgilandi."},
    "setup_done":        {
        "en": "🎉 All set! You're ready to go.\n\nSend +200000 for income or -45000 for expense.\nUse /settings anytime to change your preferences.",
        "ru": "🎉 Готово! Можно начинать.\n\nОтправьте +200000 для дохода или -45000 для расхода.\nИспользуйте /settings для изменения настроек.",
        "uz": "🎉 Tayyor! Boshlashingiz mumkin.\n\nDaromad uchun +200000, xarajat uchun -45000 yuboring.\nSozlamalar uchun /settings dan foydalaning.",
    },
    "invalid_balance":   {"en": "❌ Please enter a valid number.", "ru": "❌ Введите корректное число.", "uz": "❌ To'g'ri raqam kiriting."},

    # settings menu
    "settings_title":    {"en": "⚙️ Settings", "ru": "⚙️ Настройки", "uz": "⚙️ Sozlamalar"},
    "set_language":      {"en": "🌐 Change Language", "ru": "🌐 Изменить язык", "uz": "🌐 Tilni o'zgartirish"},
    "set_currency":      {"en": "💱 Change Currency", "ru": "💱 Изменить валюту", "uz": "💱 Valyutani o'zgartirish"},
    "set_balance":       {"en": "💰 Update Balance", "ru": "💰 Изменить баланс", "uz": "💰 Balansni o'zgartirish"},
    "set_limit":         {"en": "🎯 Daily Limit", "ru": "🎯 Дневной лимит", "uz": "🎯 Kunlik limit"},
    "reset_all_btn":     {"en": "🔄 Reset Everything", "ru": "🔄 Сбросить всё", "uz": "🔄 Hammasini nolga tushirish"},
    "language_set":      {"en": "✅ Language set to English.", "ru": "✅ Язык изменён на русский.", "uz": "✅ Til o'zbekchaga o'zgartirildi."},
    "currency_set":      {"en": "✅ Currency set to {cur}.", "ru": "✅ Валюта изменена на {cur}.", "uz": "✅ Valyuta {cur} ga o'zgartirildi."},

    # reset
    "reset_confirm":     {
        "en": "⚠️ This will delete ALL your entries and set balance to 0.\n\nAre you sure?",
        "ru": "⚠️ Это удалит ВСЕ ваши записи и обнулит баланс.\n\nВы уверены?",
        "uz": "⚠️ Bu barcha yozuvlaringizni o'chiradi va balansni nolga tushiradi.\n\nIshonchingiz komilmi?",
    },
    "reset_yes":         {"en": "✅ Yes, reset everything", "ru": "✅ Да, сбросить всё", "uz": "✅ Ha, hammasini o'chir"},
    "reset_no":          {"en": "❌ Cancel", "ru": "❌ Отмена", "uz": "❌ Bekor qilish"},
    "reset_done":        {"en": "🔄 Everything reset to zero.", "ru": "🔄 Всё сброшено до нуля.", "uz": "🔄 Hammasi nolga tushirildi."},
    "reset_cancelled":   {"en": "✅ Cancelled.", "ru": "✅ Отменено.", "uz": "✅ Bekor qilindi."},

    # entry labels
    "expense":    {"en": "🔴 Expense", "ru": "🔴 Расход", "uz": "🔴 Xarajat"},
    "income":     {"en": "✅ Income",  "ru": "✅ Доход",  "uz": "✅ Daromad"},
    "today":      {"en": "📅 Today",   "ru": "📅 Сегодня","uz": "📅 Bugun"},
    "all_time":   {"en": "📊 All Time","ru": "📊 За всё время","uz": "📊 Umumiy"},
    "spent":      {"en": "Spent",  "ru": "Расход", "uz": "Xarajat"},
    "earned":     {"en": "Earned", "ru": "Доход",  "uz": "Daromad"},
    "balance":    {"en": "Balance","ru": "Баланс", "uz": "Balans"},
    "updated":    {"en": "Updated","ru": "Обновлено","uz": "Yangilandi"},

    # percentages
    "pct_of_balance":       {"en": "📉 {pct}% of your current balance", "ru": "📉 {pct}% от текущего баланса", "uz": "📉 Joriy balansingizning {pct}%"},
    "pct_spent_of_earned":  {"en": "💡 {pct}% of total earned spent so far", "ru": "💡 {pct}% от всех доходов потрачено", "uz": "💡 Jami daromadning {pct}% sarflandi"},
    "pct_of_earned_income": {"en": "📈 +{pct}% added to total earnings", "ru": "📈 +{pct}% к общему доходу", "uz": "📈 Umumiy daromadga +{pct}% qo'shildi"},

    # warnings
    "limit_near":  {"en": "⚠️ {pct}% of your {limit} {cur} daily limit used!", "ru": "⚠️ Использовано {pct}% дневного лимита {limit} {cur}!", "uz": "⚠️ Kunlik {limit} {cur} limitingizning {pct}% ishlatildi!"},
    "limit_over":  {"en": "🚨 Daily limit exceeded! Spent {spent} {cur} (limit: {limit} {cur})", "ru": "🚨 Дневной лимит превышен! Потрачено {spent} {cur} (лимит: {limit} {cur})", "uz": "🚨 Kunlik limit oshib ketdi! {spent} {cur} sarflandi (limit: {limit} {cur})"},
    "week_spike":  {"en": "📈 Spending {pct}% more than last week!", "ru": "📈 Трат на {pct}% больше, чем на прошлой неделе!", "uz": "📈 O'tgan haftaga qaraganda {pct}% ko'p sarflayapsiz!"},

    # setlimit
    "setlimit_usage":   {"en": "Usage: /setlimit 100000\nCurrent: {limit} {cur}", "ru": "Использование: /setlimit 100000\nТекущий: {limit} {cur}", "uz": "Foydalanish: /setlimit 100000\nJoriy: {limit} {cur}"},
    "setlimit_done":    {"en": "✅ Daily limit set to {limit} {cur}.", "ru": "✅ Дневной лимит: {limit} {cur}.", "uz": "✅ Kunlik limit {limit} {cur} qilib belgilandi."},
    "setlimit_invalid": {"en": "❌ Enter a valid number. Example: /setlimit 100000", "ru": "❌ Введите корректное число. Пример: /setlimit 100000", "uz": "❌ To'g'ri raqam kiriting. Masalan: /setlimit 100000"},

    # summaries
    "sum_today":    {"en": "📅 Today's Summary",  "ru": "📅 Итог за сегодня",  "uz": "📅 Bugungi hisobot"},
    "sum_week":     {"en": "📆 This Week",         "ru": "📆 За эту неделю",    "uz": "📆 Shu hafta"},
    "sum_month":    {"en": "🗓 This Month",        "ru": "🗓 За этот месяц",   "uz": "🗓 Shu oy"},
    "sum_all":      {"en": "📊 All Time",          "ru": "📊 За всё время",     "uz": "📊 Umumiy"},
    "cur_balance":  {"en": "Current Balance",      "ru": "Текущий баланс",      "uz": "Joriy balans"},

    # undo
    "undo_btn":  {"en": "↩️ Undo last entry", "ru": "↩️ Отменить", "uz": "↩️ Bekor qilish"},
    "undo_done": {"en": "↩️ Entry removed.",  "ru": "↩️ Запись удалена.", "uz": "↩️ Yozuv o'chirildi."},
    "undo_fail": {"en": "❌ Already removed.", "ru": "❌ Уже удалено.", "uz": "❌ Allaqachon o'chirilgan."},

    # errors
    "invalid_number": {"en": "❌ Invalid. Example: +200000 or -45000", "ru": "❌ Неверно. Пример: +200000 или -45000", "uz": "❌ Noto'g'ri. Masalan: +200000 yoki -45000"},

    # share
    "share_usage":   {"en": "ℹ️ Ask them to send /myid, then use:\n/share <their_id>", "ru": "ℹ️ Попросите отправить /myid, затем:\n/share <их_id>", "uz": "ℹ️ Ulardan /myid yuborishni so'rang, keyin:\n/share <ularning_id>"},
    "share_done":    {"en": "✅ User {id} can now view your stats.", "ru": "✅ Пользователь {id} теперь видит вашу статистику.", "uz": "✅ {id} foydalanuvchi statistikangizni ko'ra oladi."},
    "share_self":    {"en": "❌ Can't share with yourself.", "ru": "❌ Нельзя поделиться с собой.", "uz": "❌ O'zingiz bilan ulasha olmaysiz."},
    "share_invalid": {"en": "❌ Invalid ID. Example: /share 123456789", "ru": "❌ Неверный ID. Пример: /share 123456789", "uz": "❌ Noto'g'ri ID. Masalan: /share 123456789"},
    "unshare_usage": {"en": "Usage: /unshare <id>", "ru": "Использование: /unshare <id>", "uz": "Foydalanish: /unshare <id>"},
    "unshare_done":  {"en": "✅ Access removed for {id}.", "ru": "✅ Доступ для {id} убран.", "uz": "✅ {id} uchun ruxsat olib tashlandi."},
    "myid":          {"en": "🆔 Your ID: {id}", "ru": "🆔 Ваш ID: {id}", "uz": "🆔 ID raqamingiz: {id}"},
    "viewstats_none":  {"en": "❌ No shared stats yet. Your ID: {id}", "ru": "❌ Нет доступной статистики. Ваш ID: {id}", "uz": "❌ Ulashilgan statistika yo'q. ID: {id}"},
    "viewstats_title": {"en": "📊 Shared Stats", "ru": "📊 Общая статистика", "uz": "📊 Ulashilgan statistika"},
    "user":            {"en": "User", "ru": "Пользователь", "uz": "Foydalanuvchi"},

    # help/welcome
    "welcome": {
        "en": "👋 Hello {name}! I track your expenses and income.\n\nSend +200000 for income or -45000 for expense.\n\nCommands:\n/today /week /month /all — summaries\n/balance — current balance\n/settings — all settings\n/myid — your Telegram ID\n/share — share with someone\n/help — this help",
        "ru": "👋 Привет, {name}! Я веду учёт доходов и расходов.\n\nОтправьте +200000 для дохода или -45000 для расхода.\n\nКоманды:\n/today /week /month /all — сводки\n/balance — текущий баланс\n/settings — все настройки\n/myid — ваш Telegram ID\n/share — поделиться\n/help — помощь",
        "uz": "👋 Salom, {name}! Men daromad va xarajatlaringizni hisoblayman.\n\nDaromad uchun +200000, xarajat uchun -45000 yuboring.\n\nBuyruqlar:\n/today /week /month /all — hisobotlar\n/balance — joriy balans\n/settings — barcha sozlamalar\n/myid — Telegram ID\n/share — ulashish\n/help — yordam",
    },
    "help": {
        "en": "📖 Send +200000 or -45000 to log money.\nAfter each entry tap ↩️ Undo to remove it.\n\n/today /week /month /all — summaries\n/balance — current balance\n/settings — change language, currency, balance, limit, or reset all\n/setlimit <amount> — set daily spending limit\n/myid — your Telegram ID\n/share <id> — share stats\n/unshare <id> — remove access\n/viewstats — view shared stats",
        "ru": "📖 Отправьте +200000 или -45000 для записи.\nПосле каждой записи нажмите ↩️ для отмены.\n\n/today /week /month /all — сводки\n/balance — текущий баланс\n/settings — язык, валюта, баланс, лимит, сброс\n/setlimit <сумма> — дневной лимит\n/myid — ваш ID\n/share <id> — поделиться\n/unshare <id> — убрать доступ\n/viewstats — доступная статистика",
        "uz": "📖 +200000 yoki -45000 yuboring.\nHar yozuvdan keyin ↩️ tugmasini bosing.\n\n/today /week /month /all — hisobotlar\n/balance — joriy balans\n/settings — til, valyuta, balans, limit, nollash\n/setlimit <miqdor> — kunlik limit\n/myid — ID raqamingiz\n/share <id> — ulashish\n/unshare <id> — ruxsatni olib tashlash\n/viewstats — ulashilgan statistika",
    },

    # scheduled
    "daily_summary":  {"en": "📅 Daily Summary",  "ru": "📅 Итог дня",     "uz": "📅 Kunlik hisobot"},
    "weekly_summary": {"en": "📆 Weekly Summary", "ru": "📆 Итог недели",  "uz": "📆 Haftalik hisobot"},
}


def t(key: str, lang: str, **kwargs) -> str:
    lang = lang if lang in ("en", "ru", "uz") else "en"
    template = TEXTS.get(key, {}).get(lang) or TEXTS.get(key, {}).get("en", key)
    return template.format(**kwargs) if kwargs else template
