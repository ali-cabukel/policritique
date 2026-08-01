"""Shared async SQLAlchemy engine and session factory."""

from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from policritique.db.session import create_engine, create_session_factory
from policritique.settings import get_settings

_engine: AsyncEngine | None = None
_session_maker: async_sessionmaker[AsyncSession] | None = None


def get_engine() -> AsyncEngine:
    global _engine
    if _engine is None:
        _engine = create_engine(get_settings())
    return _engine


def get_session_maker() -> async_sessionmaker[AsyncSession]:
    global _session_maker
    if _session_maker is None:
        _session_maker = create_session_factory(get_engine())
    return _session_maker


async def get_async_session() -> AsyncGenerator[AsyncSession]:
    async with get_session_maker()() as session:
        yield session


async def dispose_engine() -> None:
    global _engine, _session_maker
    if _engine is not None:
        await _engine.dispose()
    _engine = None
    _session_maker = None
