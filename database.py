import sqlite3
import os
from datetime import datetime
import pytz

DB_PATH = os.environ.get("DB_PATH", "expenses.db")
_db_dir = os.path.dirname(DB_PATH)
if _db_dir:
    os.makedirs(_db_dir, exist_ok=True)

TASHKENT_TZ = pytz.timezone("Asia/Tashkent")
DEFAULT_DAILY_LIMIT = 100000

# Default expense categories (icon, key) — key is used for lang lookup
EXPENSE_CATEGORIES = [
    ("🍔", "food"),
    ("🚗", "transport"),
    ("🏠", "home"),
    ("💊", "health"),
    ("🎮", "fun"),
    ("👕", "clothes"),
    ("📚", "education"),
    ("📦", "other"),
]


def get_conn():
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_conn() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS entries (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     INTEGER NOT NULL,
                amount      REAL    NOT NULL,
                type        TEXT    NOT NULL CHECK(type IN ('expense','income')),
                category    TEXT    DEFAULT NULL,
                created_at  TEXT    NOT NULL
            );
            CREATE TABLE IF NOT EXISTS shares (
                owner_id    INTEGER NOT NULL,
                viewer_id   INTEGER NOT NULL,
                PRIMARY KEY (owner_id, viewer_id)
            );
            CREATE TABLE IF NOT EXISTS users (
                user_id         INTEGER PRIMARY KEY,
                lang            TEXT    NOT NULL DEFAULT 'en',
                currency        TEXT    NOT NULL DEFAULT 'UZS',
                daily_limit     REAL    NOT NULL DEFAULT 100000,
                monthly_budget  REAL    NOT NULL DEFAULT 0,
                initial_balance REAL    NOT NULL DEFAULT 0,
                setup_done      INTEGER NOT NULL DEFAULT 0,
                reminders_on    INTEGER NOT NULL DEFAULT 1,
                categories_on   INTEGER NOT NULL DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS whitelist (
                user_id   INTEGER PRIMARY KEY,
                added_at  TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS invite_tokens (
                token      TEXT PRIMARY KEY,
                created_at TEXT NOT NULL,
                used       INTEGER NOT NULL DEFAULT 0
            );
            CREATE INDEX IF NOT EXISTS idx_entries_user_date
                ON entries(user_id, created_at);
        """)
        for col, defval in [
            ("currency",       "TEXT NOT NULL DEFAULT 'UZS'"),
            ("initial_balance","REAL NOT NULL DEFAULT 0"),
            ("setup_done",     "INTEGER NOT NULL DEFAULT 0"),
            ("monthly_budget", "REAL NOT NULL DEFAULT 0"),
            ("reminders_on",   "INTEGER NOT NULL DEFAULT 1"),
            ("categories_on",  "INTEGER NOT NULL DEFAULT 0"),
        ]:
            try:
                conn.execute(f"ALTER TABLE users ADD COLUMN {col} {defval}")
            except Exception:
                pass
        try:
            conn.execute("ALTER TABLE entries ADD COLUMN category TEXT DEFAULT NULL")
        except Exception:
            pass


def now_tashkent():
    return datetime.now(TASHKENT_TZ).strftime("%Y-%m-%d %H:%M:%S")

def today_str():
    return datetime.now(TASHKENT_TZ).strftime("%Y-%m-%d")


# ── User helpers ──────────────────────────────────────────────────────────────

def ensure_user(user_id: int):
    with get_conn() as conn:
        conn.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))

def get_user(user_id: int) -> dict:
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM users WHERE user_id=?", (user_id,)).fetchone()
        if row:
            return dict(row)
        return {"lang": None, "currency": "UZS", "daily_limit": DEFAULT_DAILY_LIMIT,
                "monthly_budget": 0, "initial_balance": 0, "setup_done": 0,
                "reminders_on": 1, "categories_on": 0}

def is_setup_done(user_id: int) -> bool:
    return bool(get_user(user_id).get("setup_done", 0))

def set_setup_done(user_id: int):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO users (user_id,setup_done) VALUES (?,1) "
            "ON CONFLICT(user_id) DO UPDATE SET setup_done=1", (user_id,))

def get_lang(user_id: int):
    u = get_user(user_id)
    return u.get("lang") if u.get("setup_done") else None

def set_lang(user_id: int, lang: str):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO users (user_id,lang) VALUES (?,?) "
            "ON CONFLICT(user_id) DO UPDATE SET lang=excluded.lang", (user_id, lang))

def get_currency(user_id: int) -> str:
    return get_user(user_id).get("currency", "UZS")

def set_currency(user_id: int, currency: str):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO users (user_id,currency) VALUES (?,?) "
            "ON CONFLICT(user_id) DO UPDATE SET currency=excluded.currency", (user_id, currency))

def get_daily_limit(user_id: int) -> float:
    return get_user(user_id).get("daily_limit", DEFAULT_DAILY_LIMIT)

def set_daily_limit(user_id: int, limit: float):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO users (user_id,daily_limit) VALUES (?,?) "
            "ON CONFLICT(user_id) DO UPDATE SET daily_limit=excluded.daily_limit", (user_id, limit))

def get_monthly_budget(user_id: int) -> float:
    return get_user(user_id).get("monthly_budget", 0)

def set_monthly_budget(user_id: int, budget: float):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO users (user_id,monthly_budget) VALUES (?,?) "
            "ON CONFLICT(user_id) DO UPDATE SET monthly_budget=excluded.monthly_budget", (user_id, budget))

def get_initial_balance(user_id: int) -> float:
    return get_user(user_id).get("initial_balance", 0)

def set_initial_balance(user_id: int, amount: float):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO users (user_id,initial_balance) VALUES (?,?) "
            "ON CONFLICT(user_id) DO UPDATE SET initial_balance=excluded.initial_balance", (user_id, amount))

def get_reminders_on(user_id: int) -> bool:
    return bool(get_user(user_id).get("reminders_on", 1))

def set_reminders_on(user_id: int, on: bool):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO users (user_id,reminders_on) VALUES (?,?) "
            "ON CONFLICT(user_id) DO UPDATE SET reminders_on=excluded.reminders_on",
            (user_id, 1 if on else 0))

def get_categories_on(user_id: int) -> bool:
    return bool(get_user(user_id).get("categories_on", 0))

def set_categories_on(user_id: int, on: bool):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO users (user_id,categories_on) VALUES (?,?) "
            "ON CONFLICT(user_id) DO UPDATE SET categories_on=excluded.categories_on",
            (user_id, 1 if on else 0))

def reset_all(user_id: int):
    with get_conn() as conn:
        conn.execute("DELETE FROM entries WHERE user_id=?", (user_id,))
        conn.execute("UPDATE users SET initial_balance=0 WHERE user_id=?", (user_id,))

def reset_today(user_id: int):
    today = today_str()
    with get_conn() as conn:
        conn.execute(
            "DELETE FROM entries WHERE user_id=? AND date(created_at)=?", (user_id, today))


# ── Entries ───────────────────────────────────────────────────────────────────

def add_entry(user_id: int, amount: float, entry_type: str, category: str = None) -> int:
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO entries (user_id,amount,type,category,created_at) VALUES (?,?,?,?,?)",
            (user_id, abs(amount), entry_type, category, now_tashkent()))
        return cur.lastrowid

def delete_entry(entry_id: int, user_id: int) -> bool:
    with get_conn() as conn:
        cur = conn.execute(
            "DELETE FROM entries WHERE id=? AND user_id=?", (entry_id, user_id))
        return cur.rowcount > 0

def _sum_query(user_id: int, date_filter: str = "") -> dict:
    sql = f"""
        SELECT
            COALESCE(SUM(CASE WHEN type='expense' THEN amount ELSE 0 END),0) AS expenses,
            COALESCE(SUM(CASE WHEN type='income'  THEN amount ELSE 0 END),0) AS income
        FROM entries WHERE user_id=? {date_filter}
    """
    with get_conn() as conn:
        row = conn.execute(sql, (user_id,)).fetchone()
        return {"expenses": row["expenses"], "income": row["income"]}

def get_today_stats(user_id: int) -> dict:
    return _sum_query(user_id, f"AND date(created_at)='{today_str()}'")

def get_week_stats(user_id: int) -> dict:
    return _sum_query(user_id,
        "AND date(created_at) >= date('now','weekday 0','-7 days','localtime')")

def get_last_week_expenses(user_id: int) -> float:
    sql = """SELECT COALESCE(SUM(amount),0) AS total FROM entries
        WHERE user_id=? AND type='expense'
          AND date(created_at) >= date('now','weekday 0','-14 days','localtime')
          AND date(created_at) <  date('now','weekday 0','-7 days','localtime')"""
    with get_conn() as conn:
        return conn.execute(sql, (user_id,)).fetchone()["total"]

def get_month_stats(user_id: int) -> dict:
    now = datetime.now(TASHKENT_TZ)
    return _sum_query(user_id, f"AND date(created_at)>='{now.year}-{now.month:02d}-01'")

def get_all_stats(user_id: int) -> dict:
    return _sum_query(user_id)

def get_balance(user_id: int) -> float:
    stats = get_all_stats(user_id)
    return get_initial_balance(user_id) + stats["income"] - stats["expenses"]


# ── Category breakdown ─────────────────────────────────────────────────────────

def get_week_by_category(user_id: int) -> list:
    """Return [(category, total)] for this week's expenses, sorted desc."""
    sql = """
        SELECT COALESCE(category,'other') AS cat, SUM(amount) AS total
        FROM entries
        WHERE user_id=? AND type='expense'
          AND date(created_at) >= date('now','weekday 0','-7 days','localtime')
        GROUP BY cat ORDER BY total DESC
    """
    with get_conn() as conn:
        rows = conn.execute(sql, (user_id,)).fetchall()
        return [(r["cat"], r["total"]) for r in rows]

def get_month_by_category(user_id: int) -> list:
    now = datetime.now(TASHKENT_TZ)
    sql = f"""
        SELECT COALESCE(category,'other') AS cat, SUM(amount) AS total
        FROM entries
        WHERE user_id=? AND type='expense'
          AND date(created_at) >= '{now.year}-{now.month:02d}-01'
        GROUP BY cat ORDER BY total DESC
    """
    with get_conn() as conn:
        rows = conn.execute(sql, (user_id,)).fetchall()
        return [(r["cat"], r["total"]) for r in rows]

def get_week_daily_totals(user_id: int) -> list:
    """Return [(date_str, expense_total)] for the last 7 days, oldest first."""
    sql = """
        SELECT date(created_at) AS d, COALESCE(SUM(amount),0) AS total
        FROM entries
        WHERE user_id=? AND type='expense'
          AND date(created_at) >= date('now','-6 days','localtime')
        GROUP BY d ORDER BY d ASC
    """
    with get_conn() as conn:
        rows = conn.execute(sql, (user_id,)).fetchall()
        return [(r["d"], r["total"]) for r in rows]

def get_all_entries(user_id: int) -> list:
    """Return all entries for export, newest first."""
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT amount, type, category, created_at FROM entries "
            "WHERE user_id=? ORDER BY created_at DESC", (user_id,)
        ).fetchall()
        return [dict(r) for r in rows]


# ── Whitelist ─────────────────────────────────────────────────────────────────

def get_owner_id() -> int:
    val = os.environ.get("OWNER_ID", "0").strip()
    try:
        return int(val)
    except ValueError:
        return 0


def is_allowed(user_id: int) -> bool:
    owner = get_owner_id()
    if owner == 0:
        return True
    if user_id == owner:
        return True
    with get_conn() as conn:
        row = conn.execute(
            "SELECT 1 FROM whitelist WHERE user_id=?", (user_id,)
        ).fetchone()
        return row is not None


def allow_user(user_id: int):
    with get_conn() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO whitelist (user_id, added_at) VALUES (?,?)",
            (user_id, now_tashkent())
        )


def deny_user(user_id: int):
    with get_conn() as conn:
        conn.execute("DELETE FROM whitelist WHERE user_id=?", (user_id,))


def get_allowed_users() -> list:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT user_id FROM whitelist ORDER BY added_at"
        ).fetchall()
        return [r["user_id"] for r in rows]


def create_invite_token(token: str):
    with get_conn() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO invite_tokens (token, created_at) VALUES (?,?)",
            (token, now_tashkent())
        )


def use_invite_token(token: str) -> bool:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT used FROM invite_tokens WHERE token=?", (token,)
        ).fetchone()
        if row and row["used"] == 0:
            conn.execute(
                "UPDATE invite_tokens SET used=1 WHERE token=?", (token,)
            )
            return True
        return False


# ── Share helpers ─────────────────────────────────────────────────────────────

def add_share(owner_id: int, viewer_id: int):
    with get_conn() as conn:
        conn.execute("INSERT OR IGNORE INTO shares (owner_id,viewer_id) VALUES (?,?)",
                     (owner_id, viewer_id))

def remove_share(owner_id: int, viewer_id: int):
    with get_conn() as conn:
        conn.execute("DELETE FROM shares WHERE owner_id=? AND viewer_id=?",
                     (owner_id, viewer_id))

def get_shared_owners(viewer_id: int) -> list:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT owner_id FROM shares WHERE viewer_id=?", (viewer_id,)).fetchall()
        return [r["owner_id"] for r in rows]

def get_all_user_ids() -> list:
    with get_conn() as conn:
        rows = conn.execute("SELECT DISTINCT user_id FROM entries").fetchall()
        return [r["user_id"] for r in rows]

def get_all_setup_user_ids() -> list:
    """All users who completed setup — used for reminders."""
    with get_conn() as conn:
        rows = conn.execute("SELECT user_id FROM users WHERE setup_done=1").fetchall()
        return [r["user_id"] for r in rows]
