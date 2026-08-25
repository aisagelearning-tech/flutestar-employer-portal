import os

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    # python-dotenv is optional; in production, environment variables are
    # expected to be set directly by the process manager / hosting platform.
    pass

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# DATABASE_URL is configurable via environment variable so the same codebase
# can run against local SQLite in development and PostgreSQL in production.
# Falls back to the existing local SQLite file if not set.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./flutestar.db")

# connect_args is only needed/valid for SQLite.
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()