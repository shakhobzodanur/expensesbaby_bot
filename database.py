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


def get_conn():
    conn = sqlite3.connect(DB_PATH)
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
                initial_balance REAL    NOT NULL DEFAULT 0,
                setup_done      INTEGER NOT NULL DEFAULT 0
            );

            CREATE INDEX IF NOT EXISTS idx_entries_user_date
                ON entries(user_id, created_at);
        """)
        # migrate: add columns if they don't exist yet
        try:
            conn.execute("ALTER TABLE users ADD COLUMN currency TEXT NOT NULL DEFAULT 'UZS'")
        except Exception:
            pass
        try:
            conn.execute("ALTER TABLE users ADD COLUMN initial_balance REAL NOT NULL DEFAULT 0")
        except Exception:
            pass
        try:
            conn.execute("ALTER TABLE users ADD COLUMN setup_done INTEGER NOT NULL DEFAULT 0")
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
                "initial_balance": 0, "setup_done": 0}


def is_setup_done(user_id: int) -> bool:
    u = get_user(user_id)
    return bool(u.get("setup_done", 0))


def set_setup_done(user_id: int):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO users (user_id, setup_done) VALUES (?,1) "
            "ON CONFLICT(user_id) DO UPDATE SET setup_done=1", (user_id,)
        )


def get_lang(user_id: int):
    u = get_user(user_id)
    return u.get("lang") if u.get("setup_done") else None


def set_lang(user_id: int, lang: str):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO users (user_id, lang) VALUES (?,?) "
            "ON CONFLICT(user_id) DO UPDATE SET lang=excluded.lang",
            (user_id, lang)
        )


def get_currency(user_id: int) -> str:
    return get_user(user_id).get("currency", "UZS")


def set_currency(user_id: int, currency: str):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO users (user_id, currency) VALUES (?,?) "
            "ON CONFLICT(user_id) DO UPDATE SET currency=excluded.currency",
            (user_id, currency)
        )


def get_daily_limit(user_id: int) -> float:
    return get_user(user_id).get("daily_limit", DEFAULT_DAILY_LIMIT)


def set_daily_limit(user_id: int, limit: float):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO users (user_id, daily_limit) VALUES (?,?) "
            "ON CONFLICT(user_id) DO UPDATE SET daily_limit=excluded.daily_limit",
            (user_id, limit)
        )


def get_initial_balance(user_id: int) -> float:
    return get_user(user_id).get("initial_balance", 0)


def set_initial_balance(user_id: int, amount: float):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO users (user_id, initial_balance) VALUES (?,?) "
            "ON CONFLICT(user_id) DO UPDATE SET initial_balance=excluded.initial_balance",
            (user_id, amount)
        )


def reset_all(user_id: int):
    """Delete all entries and reset initial balance to 0."""
    with get_conn() as conn:
        conn.execute("DELETE FROM entries WHERE user_id=?", (user_id,))
        conn.execute(
            "UPDATE users SET initial_balance=0 WHERE user_id=?", (user_id,)
        )


# ── Entries ───────────────────────────────────────────────────────────────────

def add_entry(user_id: int, amount: float, entry_type: str) -> int:
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO entries (user_id, amount, type, created_at) VALUES (?,?,?,?)",
            (user_id, abs(amount), entry_type, now_tashkent())
        )
        return cur.lastrowid


def delete_entry(entry_id: int, user_id: int) -> bool:
    with get_conn() as conn:
        cur = conn.execute(
            "DELETE FROM entries WHERE id=? AND user_id=?", (entry_id, user_id)
        )
        return cur.rowcount > 0


def _sum_query(user_id: int, date_filter: str = "") -> dict:
    sql = f"""
        SELECT
            COALESCE(SUM(CASE WHEN type='expense' THEN amount ELSE 0 END), 0) AS expenses,
            COALESCE(SUM(CASE WHEN type='income'  THEN amount ELSE 0 END), 0) AS income
        FROM entries WHERE user_id=? {date_filter}
    """
    with get_conn() as conn:
        row = conn.execute(sql, (user_id,)).fetchone()
        return {"expenses": row["expenses"], "income": row["income"]}


def get_today_stats(user_id: int) -> dict:
    return _sum_query(user_id, f"AND date(created_at)='{today_str()}'")


def get_week_stats(user_id: int) -> dict:
    return _sum_query(
        user_id,
        "AND date(created_at) >= date('now','weekday 0','-7 days','localtime')"
    )


def get_last_week_expenses(user_id: int) -> float:
    sql = """
        SELECT COALESCE(SUM(amount),0) AS total FROM entries
        WHERE user_id=? AND type='expense'
          AND date(created_at) >= date('now','weekday 0','-14 days','localtime')
          AND date(created_at) <  date('now','weekday 0','-7 days','localtime')
    """
    with get_conn() as conn:
        return conn.execute(sql, (user_id,)).fetchone()["total"]


def get_month_stats(user_id: int) -> dict:
    now = datetime.now(TASHKENT_TZ)
    return _sum_query(user_id, f"AND date(created_at)>='{now.year}-{now.month:02d}-01'")


def get_all_stats(user_id: int) -> dict:
    return _sum_query(user_id)


def get_balance(user_id: int) -> float:
    stats = get_all_stats(user_id)
    initial = get_initial_balance(user_id)
    return initial + stats["income"] - stats["expenses"]


# ── Share helpers ─────────────────────────────────────────────────────────────

def add_share(owner_id: int, viewer_id: int):
    with get_conn() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO shares (owner_id, viewer_id) VALUES (?,?)",
            (owner_id, viewer_id)
        )


def remove_share(owner_id: int, viewer_id: int):
    with get_conn() as conn:
        conn.execute(
            "DELETE FROM shares WHERE owner_id=? AND viewer_id=?", (owner_id, viewer_id)
        )


def get_shared_owners(viewer_id: int) -> list:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT owner_id FROM shares WHERE viewer_id=?", (viewer_id,)
        ).fetchall()
        return [r["owner_id"] for r in rows]


def get_viewers(owner_id: int) -> list:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT viewer_id FROM shares WHERE owner_id=?", (owner_id,)
        ).fetchall()
        return [r["viewer_id"] for r in rows]


def get_all_user_ids() -> list:
    with get_conn() as conn:
        rows = conn.execute("SELECT DISTINCT user_id FROM entries").fetchall()
        return [r["user_id"] for r in rows]
