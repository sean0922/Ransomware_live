import os
import time
from datetime import date, datetime

import psycopg2
from psycopg2 import sql
from psycopg2.extras import execute_values


def db_config(dbname=None):
    return {
        "host": os.getenv("POSTGRES_HOST", "postgres"),
        "port": os.getenv("POSTGRES_PORT", "5432"),
        "dbname": dbname or os.getenv("POSTGRES_DB", "ransomware_live"),
        "user": os.getenv("POSTGRES_USER", "postgres"),
        "password": os.getenv("POSTGRES_PASSWORD", "postgres"),
    }


def get_connection():
    database_url = os.getenv("DATABASE_URL")
    last_error = None

    for _ in range(10):
        try:
            if database_url:
                return psycopg2.connect(database_url)

            return psycopg2.connect(**db_config())
        except psycopg2.OperationalError as exc:
            last_error = exc
            time.sleep(2)

    raise last_error


def parse_date(value):
    if not value:
        return None
    if isinstance(value, date):
        return value
    value = str(value).strip()
    if not value:
        return None

    for fmt in ("%Y-%m-%d", "%Y/%m/%d"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            pass

    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).date()
    except ValueError:
        pass

    return None


def empty_to_none(value):
    if value == "":
        return None
    return value


def ensure_database():
    if os.getenv("DATABASE_URL"):
        return

    target_db = os.getenv("POSTGRES_DB", "ransomware_live")
    maintenance_db = os.getenv("POSTGRES_MAINTENANCE_DB", "postgres")

    if target_db == maintenance_db:
        return

    last_error = None
    for _ in range(10):
        try:
            with psycopg2.connect(**db_config(dbname=maintenance_db)) as conn:
                conn.autocommit = True
                with conn.cursor() as cur:
                    cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (target_db,))
                    if cur.fetchone():
                        return
                    cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(target_db)))
                    return
        except psycopg2.OperationalError as exc:
            last_error = exc
            time.sleep(2)

    raise last_error


def init_db():
    ensure_database()

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS victims (
                    id TEXT PRIMARY KEY,
                    discovered_date DATE,
                    attackdate DATE,
                    victim TEXT,
                    group_name TEXT,
                    description TEXT,
                    post_url TEXT,
                    country TEXT,
                    country_full TEXT,
                    activity TEXT,
                    screenshot TEXT,
                    fetched_year INTEGER NOT NULL,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS cyberattacks (
                    source_key TEXT PRIMARY KEY,
                    event_date DATE,
                    victim TEXT,
                    domain TEXT,
                    country TEXT,
                    country_full TEXT,
                    summary TEXT,
                    title TEXT,
                    url TEXT,
                    ransomware_group TEXT,
                    fetched_year INTEGER NOT NULL,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                )
                """
            )


def upsert_victims(rows):
    rows = dedupe_rows(rows, key_index=0)
    if not rows:
        return 0

    sql = """
        INSERT INTO victims (
            id, discovered_date, attackdate, victim, group_name, description,
            post_url, country, country_full, activity, screenshot, fetched_year
        )
        VALUES %s
        ON CONFLICT (id) DO UPDATE SET
            discovered_date = EXCLUDED.discovered_date,
            attackdate = EXCLUDED.attackdate,
            victim = EXCLUDED.victim,
            group_name = EXCLUDED.group_name,
            description = EXCLUDED.description,
            post_url = EXCLUDED.post_url,
            country = EXCLUDED.country,
            country_full = EXCLUDED.country_full,
            activity = EXCLUDED.activity,
            screenshot = EXCLUDED.screenshot,
            fetched_year = EXCLUDED.fetched_year,
            updated_at = NOW()
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            execute_values(cur, sql, rows)
    return len(rows)


def upsert_cyberattacks(rows):
    rows = dedupe_rows(rows, key_index=0)
    if not rows:
        return 0

    sql = """
        INSERT INTO cyberattacks (
            source_key, event_date, victim, domain, country, country_full,
            summary, title, url, ransomware_group, fetched_year
        )
        VALUES %s
        ON CONFLICT (source_key) DO UPDATE SET
            event_date = EXCLUDED.event_date,
            victim = EXCLUDED.victim,
            domain = EXCLUDED.domain,
            country = EXCLUDED.country,
            country_full = EXCLUDED.country_full,
            summary = EXCLUDED.summary,
            title = EXCLUDED.title,
            url = EXCLUDED.url,
            ransomware_group = EXCLUDED.ransomware_group,
            fetched_year = EXCLUDED.fetched_year,
            updated_at = NOW()
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            execute_values(cur, sql, rows)
    return len(rows)


def dedupe_rows(rows, key_index):
    deduped = {}
    for row in rows:
        key = row[key_index]
        if key is not None:
            deduped[key] = row
    return list(deduped.values())
