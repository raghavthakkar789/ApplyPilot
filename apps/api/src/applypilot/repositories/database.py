from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from applypilot.core.config import get_settings


class Base(DeclarativeBase):
    pass


engine = create_engine(get_settings().database_dsn(), pool_pre_ping=True)
SessionFactory = sessionmaker(bind=engine, expire_on_commit=False)


def build_session_factory() -> sessionmaker[Session]:
    return SessionFactory


def get_database_session() -> Generator[Session]:
    session = SessionFactory()
    try:
        yield session
    finally:
        session.close()
