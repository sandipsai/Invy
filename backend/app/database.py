# database.py — one place for everything SQLAlchemy needs to talk to the DB.

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from .config import get_settings

settings = get_settings()

engine = create_engine(
    settings.database_url,
    # SQLite-specific: allows the same connection to be used across threads.
    # FastAPI runs handlers concurrently so this is required.
    connect_args={"check_same_thread": False},
    # Echo=True prints every SQL statement to the console — great for
    # learning. Set to False in production.
    echo=settings.debug,
)

# Enable WAL mode for SQLite: allows concurrent reads during writes,
# which prevents "database is locked" errors during development.
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA foreign_keys=ON")  # enforce FK constraints in SQLite
    cursor.close()


# SessionLocal is a factory — calling it gives you a fresh session object.
# autocommit=False means changes only persist when you explicitly call commit().
# autoflush=False means SQLAlchemy won't auto-send pending changes to the DB
# mid-transaction (prevents surprises).
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Parent class for all ORM models. Registers tables with SQLAlchemy."""
    pass


def get_db():
    """
    FastAPI dependency that provides a DB session per request.

    'yield' makes this a generator — code before yield runs before the
    handler, code after yield (in finally) runs after — even on errors.
    This guarantees the session is always closed.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()