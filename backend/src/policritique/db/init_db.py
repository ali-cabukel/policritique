"""Create or upgrade application tables."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncEngine

from policritique.auth.models import User  # noqa: F401 — register user table
from policritique.db.models import Base


async def init_schema(engine: AsyncEngine) -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
