#app/config.py
import os
import psycopg2
from urllib.parse import urlparse

def is_db_reachable(db_uri):
    if not db_uri:
        return False

    try:
        parsed = urlparse(db_uri)
        conn = psycopg2.connect(
            dbname=parsed.path[1:],
            user=parsed.username,
            password=parsed.password,
            host=parsed.hostname,
            port=parsed.port or 5432,
            connect_timeout=3
        )
        conn.close()
        return True
    except Exception:
        return False


def resolve_database_uri():
    PG_DMZ_URI = os.getenv("POSTGRES_URI")
    PG_LOCAL_URI = os.getenv("POSTGRES_local_URI")

    if is_db_reachable(PG_DMZ_URI):
        POSTGRES_URI = PG_DMZ_URI
    else:
        POSTGRES_URI = PG_LOCAL_URI

class Config:
    SECRET_KEY = os.getenv("session_secret_key", "default")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = resolve_database_uri()

    APP_NAME = os.getenv("APP_NAME", "APP Name")
    APP_VERSION = os.getenv("APP_VERSION", "2.90.25925")
    SUPPORT_EMAIL = os.getenv("SUPPORT_EMAIL", "support@gmail.com")