"""Postgres schema helpers for SQLAlchemy."""

from __future__ import annotations

from sqlalchemy import MetaData

from policritique.settings import get_settings


def effective_schema() -> str | None:
    settings = get_settings()
    name = settings.database_schema.strip()
    if not name or name == "public":
        return None
    if settings.is_sqlite:
        return None
    return name


metadata = MetaData(schema=effective_schema())


def qualified_schema() -> str | None:
    return effective_schema()
