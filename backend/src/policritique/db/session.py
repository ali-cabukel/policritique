"""Async SQLAlchemy engine and session factory."""

from __future__ import annotations

from sqlalchemy import event
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from policritique.db.schema import qualified_schema
from policritique.settings import Settings, get_settings


def create_engine(settings: Settings | None = None) -> AsyncEngine:
    settings = settings or get_settings()
    url = settings.resolved_database_url
    connect_args: dict = {}
    if settings.is_sqlite:
        connect_args["check_same_thread"] = False

    engine = create_async_engine(url, connect_args=connect_args)

    if settings.is_sqlite:

        @event.listens_for(engine.sync_engine, "connect")
        def _set_sqlite_pragma(dbapi_connection, connection_record) -> None:
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    elif schema := qualified_schema():

        @event.listens_for(engine.sync_engine, "connect")
        def _set_postgres_search_path(dbapi_connection, connection_record) -> None:
            cursor = dbapi_connection.cursor()
            cursor.execute(f'CREATE SCHEMA IF NOT EXISTS "{schema}"')
            cursor.execute(f'SET search_path TO "{schema}", public')
            cursor.close()

    return engine


def create_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(engine, expire_on_commit=False)
