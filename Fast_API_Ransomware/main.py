from datetime import date

from fastapi import FastAPI, HTTPException, Query
from psycopg2.errors import UndefinedTable
from psycopg2.extras import RealDictCursor

from database import get_connection


app = FastAPI(title="Ransomware Live Search API")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/db-info")
def db_info():
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT current_database() AS database, current_user AS user")
            connection = cur.fetchone()
            cur.execute(
                """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                ORDER BY table_name
                """
            )
            tables = [row["table_name"] for row in cur.fetchall()]

    return {
        **connection,
        "tables": tables,
    }


@app.get("/cyberattacks")
def search_cyberattacks(
    event_date: date | None = None,
    event_date_start: date | None = None,
    event_date_end: date | None = None,
    country: str | None = None,
    ransomware_group: str | None = None,
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
):
    where = []
    params = []

    add_date_filter(
        where=where,
        params=params,
        column="event_date",
        exact_date=event_date,
        start_date=event_date_start,
        end_date=event_date_end,
    )
    if country:
        where.append("country ILIKE %s")
        params.append(country)
    if ransomware_group:
        where.append("ransomware_group ILIKE %s")
        params.append(f"%{ransomware_group}%")

    return query_table(
        table="cyberattacks",
        where=where,
        params=params,
        order_by="event_date DESC NULLS LAST, victim ASC",
        limit=limit,
        offset=offset,
    )


@app.get("/victims")
def search_victims(
    attackdate: date | None = None,
    attackdate_start: date | None = None,
    attackdate_end: date | None = None,
    country: str | None = None,
    group_name: str | None = None,
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
):
    where = []
    params = []

    add_date_filter(
        where=where,
        params=params,
        column="attackdate",
        exact_date=attackdate,
        start_date=attackdate_start,
        end_date=attackdate_end,
    )
    if country:
        where.append("country ILIKE %s")
        params.append(country)
    if group_name:
        where.append("group_name ILIKE %s")
        params.append(f"%{group_name}%")

    return query_table(
        table="victims",
        where=where,
        params=params,
        order_by="attackdate DESC NULLS LAST, victim ASC",
        limit=limit,
        offset=offset,
    )


def add_date_filter(where, params, column, exact_date, start_date, end_date):
    if exact_date:
        where.append(f"{column} = %s")
        params.append(exact_date)
        return

    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=400,
            detail=f"{column}_start must be before or equal to {column}_end.",
        )

    if start_date:
        where.append(f"{column} >= %s")
        params.append(start_date)
    if end_date:
        where.append(f"{column} <= %s")
        params.append(end_date)


def query_table(table, where, params, order_by, limit, offset):
    where_sql = f"WHERE {' AND '.join(where)}" if where else ""
    count_sql = f"SELECT COUNT(*) AS total FROM {table} {where_sql}"
    data_sql = f"""
        SELECT *
        FROM {table}
        {where_sql}
        ORDER BY {order_by}
        LIMIT %s OFFSET %s
    """

    try:
        with get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(count_sql, params)
                total = cur.fetchone()["total"]

                cur.execute(data_sql, [*params, limit, offset])
                items = cur.fetchall()
    except UndefinedTable as exc:
        raise HTTPException(
            status_code=500,
            detail=(
                f"Table '{table}' does not exist in the connected database. "
                "Check POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER, "
                "POSTGRES_PASSWORD, or DATABASE_URL."
            ),
        ) from exc

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "items": items,
    }
