import os
import time

import psycopg2
from dotenv import load_dotenv


load_dotenv()


def get_connection():
    database_url = os.getenv("DATABASE_URL")
    last_error = None

    for _ in range(10):
        try:
            if database_url:
                return psycopg2.connect(database_url)

            return psycopg2.connect(
                host=os.getenv("POSTGRES_HOST", "localhost"),
                port=os.getenv("POSTGRES_PORT", "5433"),
                dbname=os.getenv("POSTGRES_DB", "ransomware_live"),
                user=os.getenv("POSTGRES_USER", "postgres"),
                password=os.getenv("POSTGRES_PASSWORD", "postgres"),
            )
        except psycopg2.OperationalError as exc:
            last_error = exc
            time.sleep(2)

    raise last_error
