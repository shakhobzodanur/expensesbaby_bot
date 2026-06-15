# -*- coding: utf-8 -*-
LANGUAGES  = {"en": "English 🇬🇧", "ru": "Русский 🇷🇺", "uz": "O'zbekcha 🇺🇿"}
CURRENCIES = ["UZS", "USD", "RUB"]

TEXTS = {
    # setup
    "choose_language": {"en":"🌐 Choose your language:","ru":"🌐 Выберите язык:","uz":"🌐 Tilni tanlang:"},
    "choose_currency": {"en":"💱 Choose your currency:","ru":"💱 Выберите валюту:","uz":"💱 Valyutani tanlang:"},
    "enter_balance":   {
        "en":"💰 What is your current balance?\n\nEnter amount (e.g. 5000000) or 0 to start from zero:",
        "ru":"💰 Какой у вас текущий баланс?\n\nВведите сумму (например 5000000) или 0:",
        "uz":"💰 Hozirgi balansingiz qancha?\n\nSummani kiriting (masalan 5000000) yoki 0:",
    },
    "balance_set":  {"en":"✅ Balance set to {bal} {cur}.","ru":"✅ Баланс: {bal} {cur}.","uz":"✅ Balans {bal} {cur} belgilandi."},
    "setup_done":   {
        "en":"🎉 All set!\n\nSend +200000 for income or -45000 for expense.\nTap the 📋 menu button anytime.",
        "ru":"🎉 Готово!\n\nОтправьте +200000 для дохода или -45000 для расхода.\nНажмите кнопку 📋 для меню.",
        "uz":"🎉 Tayyor!\n\nDaromad uchun +200000, xarajat uchun -45000 yuboring.\n📋 menyu tugmasini bosing.",
    },
    "invalid_balance":{"en":"❌ Please enter a valid number.","ru":"❌ Введите корректное число.","uz":"❌ To'g'ri raqam kiriting."},

    # menu buttons (reply keyboard)
    "btn_today":    {"en":"📅 Today",    "ru":"📅 Сегодня",  "uz":"📅 Bugun"},
    "btn_week":     {"en":"📆 Week",     "ru":"📆 Неделя",   "uz":"📆 Hafta"},
    "btn_month":    {"en":"🗓 Month",    "ru":"🗓 Месяц",    "uz":"🗓 Oy"},
    "btn_balance":  {"en":"💰 Balance",  "ru":"💰 Баланс",   "uz":"💰 Balans"},
    "btn_settings": {"en":"⚙️ Settings", "ru":"⚙️ Настройки","uz":"⚙️ Sozlamalar"},
    "btn_help":     {"en":"❓ Help",     "ru":"❓ Помощь",   "uz":"❓ Yordam"},

    # settings inline
    "settings_title": {"en":"⚙️ Settings","ru":"⚙️ Настройки","uz":"⚙️ Sozlamalar"},
    "set_language":   {"en":"🌐 Language",      "ru":"🌐 Язык",          "uz":"🌐 Til"},
    "set_currency":   {"en":"💱 Currency",      "ru":"💱 Валюта",        "uz":"💱 Valyuta"},
    "set_balance":    {"en":"💰 Update Balance","ru":"💰 Изменить баланс","uz":"💰 Balansni o'zgartirish"},
    "set_limit":      {"en":"🎯 Daily Limit",   "ru":"🎯 Дневной лимит", "uz":"🎯 Kunlik limit"},
    "set_budget":     {"en":"📊 Monthly Budget","ru":"📊 Месячный бюджет","uz":"📊 Oylik byudjet"},
    "reset_today_btn":{"en":"📅 Reset Today",   "ru":"📅 Сбросить сегодня","uz":"📅 Bugunni nolga tushirish"},
    "reset_all_btn":  {"en":"🔄 Reset Everything","ru":"🔄 Сбросить всё","uz":"🔄 Hammasini nolga tushirish"},
    "language_set":   {"en":"✅ Language: English","ru":"✅ Язык: русский","uz":"✅ Til: o'zbekcha"},
    "currency_set":   {"en":"✅ Currency set to {cur}.","ru":"✅ Валюта: {cur}.","uz":"✅ Valyuta {cur} ga o'zgartirildi."},

    # budget
    "enter_budget":  {
        "en":"📊 Enter your monthly budget (0 to disable):",
        "ru":"📊 Введите месячный бюджет (0 — отключить):",
        "uz":"📊 Oylik byudjetingizni kiriting (o'chirish uchun 0):",
    },
    "budget_set":    {"en":"✅ Monthly budget: {budget} {cur}.","ru":"✅ Месячный бюджет: {budget} {cur}.","uz":"✅ Oylik byudjet: {budget} {cur}."},
    "budget_warn":   {"en":"📊 {pct}% of monthly budget used ({spent}/{budget} {cur})","ru":"📊 Использовано {pct}% месячного бюджета ({spent}/{budget} {cur})","uz":"📊 Oylik byudjetning {pct}% ishlatildi ({spent}/{budget} {cur})"},
    "budget_over":   {"en":"🚨 Monthly budget exceeded! {spent} {cur} spent (budget: {budget} {cur})","ru":"🚨 Месячный бюджет превышен! Потрачено {spent} {cur} (бюджет: {budget} {cur})","uz":"🚨 Oylik byudjet oshib ketdi! {spent} {cur} sarflandi (byudjet: {budget} {cur})"},

    # reset
    "reset_confirm":      {"en":"⚠️ Delete ALL entries and reset balance to 0?\n\nAre you sure?","ru":"⚠️ Удалить ВСЕ записи и обнулить баланс?\n\nВы уверены?","uz":"⚠️ Barcha yozuvlarni o'chirib, balansni nolga tushirasizmi?"},
    "reset_today_confirm":{"en":"⚠️ Delete only TODAY's entries?\n\nAre you sure?","ru":"⚠️ Удалить записи только за СЕГОДНЯ?\n\nВы уверены?","uz":"⚠️ Faqat BUGUNGI yozuvlarni o'chirasizmi?"},
    "reset_yes":          {"en":"✅ Yes","ru":"✅ Да","uz":"✅ Ha"},
    "reset_no":           {"en":"❌ Cancel","ru":"❌ Отмена","uz":"❌ Bekor qilish"},
    "reset_done":         {"en":"🔄 Everything reset to zero.","ru":"🔄 Всё сброшено до нуля.","uz":"🔄 Hammasi nolga tushirildi."},
    "reset_today_done":   {"en":"📅 Today's entries deleted.","ru":"📅 Записи за сегодня удалены.","uz":"📅 Bugungi yozuvlar o'chirildi."},
    "reset_cancelled":    {"en":"✅ Cancelled.","ru":"✅ Отменено.","uz":"✅ Bekor qilindi."},

    # entry labels
    "expense":  {"en":"🔴 Expense","ru":"🔴 Расход","uz":"🔴 Xarajat"},
    "income":   {"en":"✅ Income", "ru":"✅ Доход", "uz":"✅ Daromad"},
    "today":    {"en":"📅 Today",  "ru":"📅 Сегодня","uz":"📅 Bugun"},
    "all_time": {"en":"📊 All Time","ru":"📊 За всё время","uz":"📊 Umumiy"},
    "spent":    {"en":"Spent",  "ru":"Расход","uz":"Xarajat"},
    "earned":   {"en":"Earned", "ru":"Доход", "uz":"Daromad"},
    "balance":  {"en":"Balance","ru":"Баланс","uz":"Balans"},
    "updated":  {"en":"Updated","ru":"Обновлено","uz":"Yangilandi"},

    # percentages
    "pct_of_balance":      {"en":"📉 {pct}% of your balance","ru":"📉 {pct}% от баланса","uz":"📉 Balansingizning {pct}%"},
    "pct_spent_of_earned": {"en":"💡 {pct}% of total earned spent","ru":"💡 {pct}% от доходов потрачено","uz":"💡 Jami daromadning {pct}% sarflandi"},
    "pct_of_earned_income":{"en":"📈 +{pct}% to total earnings","ru":"📈 +{pct}% к общему доходу","uz":"📈 Umumiy daromadga +{pct}%"},

    # daily limit
    "limit_near": {"en":"⚠️ {pct}% of daily limit used! ({spent}/{limit} {cur})","ru":"⚠️ {pct}% дневного лимита использовано! ({spent}/{limit} {cur})","uz":"⚠️ Kunlik limitning {pct}% ishlatildi! ({spent}/{limit} {cur})"},
    "limit_over": {"en":"🚨 Daily limit exceeded! {spent} {cur} (limit: {limit} {cur})","ru":"🚨 Дневной лимит превышен! {spent} {cur} (лимит: {limit} {cur})","uz":"🚨 Kunlik limit oshdi! {spent} {cur} (limit: {limit} {cur})"},
    "week_spike": {"en":"📈 {pct}% more spending than last week!","ru":"📈 Трат на {pct}% больше, чем на прошлой неделе!","uz":"📈 O'tgan haftaga qaraganda {pct}% ko'p!"},

    # setlimit / setbudget prompts
    "setlimit_usage":   {"en":"Current daily limit: {limit} {cur}\n\nEnter new limit:","ru":"Текущий лимит: {limit} {cur}\n\nВведите новый лимит:","uz":"Joriy limit: {limit} {cur}\n\nYangi limit kiriting:"},
    "setlimit_done":    {"en":"✅ Daily limit: {limit} {cur}.","ru":"✅ Дневной лимит: {limit} {cur}.","uz":"✅ Kunlik limit: {limit} {cur}."},
    "setlimit_invalid": {"en":"❌ Enter a valid number.","ru":"❌ Введите корректное число.","uz":"❌ To'g'ri raqam kiriting."},

    # summaries
    "sum_today": {"en":"📅 Today's Summary","ru":"📅 Итог за сегодня","uz":"📅 Bugungi hisobot"},
    "sum_week":  {"en":"📆 This Week",      "ru":"📆 За эту неделю","uz":"📆 Shu hafta"},
    "sum_month": {"en":"🗓 This Month",     "ru":"🗓 За этот месяц","uz":"🗓 Shu oy"},
    "sum_all":   {"en":"📊 All Time",       "ru":"📊 За всё время", "uz":"📊 Umumiy"},
    "cur_balance":{"en":"Current Balance",  "ru":"Текущий баланс",  "uz":"Joriy balans"},

    # undo
    "undo_btn":  {"en":"↩️ Undo","ru":"↩️ Отменить","uz":"↩️ Bekor qilish"},
    "undo_done": {"en":"↩️ Entry removed.","ru":"↩️ Запись удалена.","uz":"↩️ Yozuv o'chirildi."},
    "undo_fail": {"en":"❌ Already removed.","ru":"❌ Уже удалено.","uz":"❌ Allaqachon o'chirilgan."},

    # errors
    "invalid_number":{"en":"❌ Invalid. Example: +200000 or -45000","ru":"❌ Неверно. Пример: +200000 или -45000","uz":"❌ Noto'g'ri. Masalan: +200000 yoki -45000"},

    # share
    "share_usage":    {"en":"Ask them to send /myid, then:\n/share <their_id>","ru":"Попросите отправить /myid, затем:\n/share <их_id>","uz":"Ulardan /myid yuborishni so'rang, keyin:\n/share <ularning_id>"},
    "share_done":     {"en":"✅ User {id} can view your stats with /viewstats.","ru":"✅ Пользователь {id} может видеть статистику.","uz":"✅ {id} foydalanuvchi statistikangizni ko'ra oladi."},
    "share_self":     {"en":"❌ Can't share with yourself.","ru":"❌ Нельзя поделиться с собой.","uz":"❌ O'zingiz bilan ulasha olmaysiz."},
    "share_invalid":  {"en":"❌ Invalid ID.","ru":"❌ Неверный ID.","uz":"❌ Noto'g'ri ID."},
    "unshare_usage":  {"en":"Usage: /unshare <id>","ru":"Использование: /unshare <id>","uz":"Foydalanish: /unshare <id>"},
    "unshare_done":   {"en":"✅ Access removed for {id}.","ru":"✅ Доступ для {id} убран.","uz":"✅ {id} uchun ruxsat olib tashlandi."},
    "myid":           {"en":"🆔 Your ID: {id}","ru":"🆔 Ваш ID: {id}","uz":"🆔 ID raqamingiz: {id}"},
    "viewstats_none": {"en":"❌ No shared stats. Your ID: {id}","ru":"❌ Нет статистики. Ваш ID: {id}","uz":"❌ Ulashilgan statistika yo'q. ID: {id}"},
    "viewstats_title":{"en":"📊 Shared Stats","ru":"📊 Общая статистика","uz":"📊 Ulashilgan statistika"},
    "user":           {"en":"User","ru":"Пользователь","uz":"Foydalanuvchi"},

    # welcome / help
    "welcome": {
        "en":"👋 Hello {name}!\n\nSend +200000 for income or -45000 for expense.\nUse the menu buttons below ⬇️",
        "ru":"👋 Привет, {name}!\n\nОтправьте +200000 для дохода или -45000 для расхода.\nИспользуйте кнопки меню ⬇️",
        "uz":"👋 Salom, {name}!\n\nDaromad uchun +200000, xarajat uchun -45000 yuboring.\nQuyidagi menyu tugmalaridan foydalaning ⬇️",
    },
    "help": {
        "en":"📖 Send +200000 or -45000 to log.\nTap ↩️ Undo to remove the last entry.\n\nMenu buttons:\n📅 Today — today's summary\n📆 Week — weekly summary\n🗓 Month — monthly summary\n💰 Balance — current balance\n⚙️ Settings — change everything\n❓ Help — this message\n\nOther commands:\n/all — all time totals\n/myid — your Telegram ID\n/share <id> — share stats\n/viewstats — shared stats",
        "ru":"📖 Отправьте +200000 или -45000 для записи.\nНажмите ↩️ Отменить чтобы удалить последнюю запись.\n\nКнопки меню:\n📅 Сегодня\n📆 Неделя\n🗓 Месяц\n💰 Баланс\n⚙️ Настройки\n❓ Помощь\n\nДругие команды:\n/all — за всё время\n/myid — ваш ID\n/share <id> — поделиться\n/viewstats — общая статистика",
        "uz":"📖 +200000 yoki -45000 yuboring.\n↩️ Bekor qilish tugmasi oxirgi yozuvni o'chiradi.\n\nMenyu tugmalari:\n📅 Bugun\n📆 Hafta\n🗓 Oy\n💰 Balans\n⚙️ Sozlamalar\n❓ Yordam\n\nBoshqa buyruqlar:\n/all — umumiy\n/myid — ID\n/share <id> — ulashish\n/viewstats — ulashilgan statistika",
    },

    # scheduled
    "daily_summary":  {"en":"📅 Daily Summary", "ru":"📅 Итог дня",    "uz":"📅 Kunlik hisobot"},
    "weekly_summary": {"en":"📆 Weekly Summary","ru":"📆 Итог недели","uz":"📆 Haftalik hisobot"},
}


def t(key: str, lang: str, **kwargs) -> str:
    lang = lang if lang in ("en","ru","uz") else "en"
    tmpl = TEXTS.get(key, {}).get(lang) or TEXTS.get(key, {}).get("en", key)
    return tmpl.format(**kwargs) if kwargs else tmpl
