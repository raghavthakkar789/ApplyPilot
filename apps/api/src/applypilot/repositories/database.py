from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from applypilot.core.config import get_settings


class Base(DeclarativeBase):
    pass


def build_session_factory() -> sessionmaker[Session]:
    engine = create_engine(get_settings().database_url, pool_pre_ping=True)
    return sessionmaker(bind=engine, expire_on_commit=False)


def get_database_session() -> Generator[Session]:
    session = build_session_factory()()
    try:
        yield session
    finally:
        session.close()
