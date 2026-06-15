import sqlite3
import os
from datetime import datetime
import pytz

DB_PATH = os.environ.get("DB_PATH", "expenses.db")

# Auto-create directory if it doesn't exist (e.g. /data on Railway)
_db_dir = os.path.dirname(DB_PATH)
if _db_dir:
    os.makedirs(_db_dir, exist_ok=True)

TASHKENT_TZ = pytz.timezone("Asia/Tashkent")

DEFAULT_DAILY_LIMIT = 100000  # UZS


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
                user_id      INTEGER PRIMARY KEY,
                lang         TEXT    NOT NULL DEFAULT 'en',
                daily_limit  REAL    NOT NULL DEFAULT 100000
            );

            CREATE INDEX IF NOT EXISTS idx_entries_user_date
                ON entries(user_id, created_at);
        """)


def now_tashkent():
    return datetime.now(TASHKENT_TZ).strftime("%Y-%m-%d %H:%M:%S")


def today_str():
    return datetime.now(TASHKENT_TZ).strftime("%Y-%m-%d")


# -- User settings (language + daily limit) --

def ensure_user(user_id: int):
    with get_conn() as conn:
        conn.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))


def get_lang(user_id: int):
    """Return language code or None if user never picked one."""
    with get_conn() as conn:
        row = conn.execute("SELECT lang FROM users WHERE user_id=?", (user_id,)).fetchone()
        return row["lang"] if row else None


def set_lang(user_id: int, lang: str):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO users (user_id, lang) VALUES (?,?) "
            "ON CONFLICT(user_id) DO UPDATE SET lang=excluded.lang",
            (user_id, lang)
        )


def get_daily_limit(user_id: int) -> float:
    with get_conn() as conn:
        row = conn.execute("SELECT daily_limit FROM users WHERE user_id=?", (user_id,)).fetchone()
        return row["daily_limit"] if row else DEFAULT_DAILY_LIMIT


def set_daily_limit(user_id: int, limit: float):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO users (user_id, daily_limit) VALUES (?,?) "
            "ON CONFLICT(user_id) DO UPDATE SET daily_limit=excluded.daily_limit",
            (user_id, limit)
        )


# -- Entries --

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
        FROM entries
        WHERE user_id=? {date_filter}
    """
    with get_conn() as conn:
        row = conn.execute(sql, (user_id,)).fetchone()
        return {"expenses": row["expenses"], "income": row["income"]}


def get_today_stats(user_id: int) -> dict:
    today = today_str()
    return _sum_query(user_id, f"AND date(created_at)='{today}'")


def get_week_stats(user_id: int) -> dict:
    return _sum_query(
        user_id,
        "AND date(created_at) >= date('now','weekday 0','-7 days','localtime')"
    )


def get_last_week_expenses(user_id: int) -> float:
    """Total expenses of the previous week (7-14 days ago window)."""
    sql = """
        SELECT COALESCE(SUM(amount),0) AS total
        FROM entries
        WHERE user_id=? AND type='expense'
          AND date(created_at) >= date('now','weekday 0','-14 days','localtime')
          AND date(created_at) <  date('now','weekday 0','-7 days','localtime')
    """
    with get_conn() as conn:
        row = conn.execute(sql, (user_id,)).fetchone()
        return row["total"]


def get_month_stats(user_id: int) -> dict:
    now = datetime.now(TASHKENT_TZ)
    month_start = f"{now.year}-{now.month:02d}-01"
    return _sum_query(user_id, f"AND date(created_at)>='{month_start}'")


def get_all_stats(user_id: int) -> dict:
    return _sum_query(user_id)


def get_balance(user_id: int) -> float:
    stats = get_all_stats(user_id)
    return stats["income"] - stats["expenses"]


# -- Share helpers --

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
