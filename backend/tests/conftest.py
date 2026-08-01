"""Shared pytest fixtures."""

from __future__ import annotations

import pytest

from policritique.db.engine import dispose_engine
from policritique.settings import get_settings


@pytest.fixture(autouse=True)
def isolated_test_db(monkeypatch: pytest.MonkeyPatch, tmp_path):
    db_path = tmp_path / "policritique.db"
    monkeypatch.setenv("DB_PATH", str(db_path))
    monkeypatch.delenv("DATABASE_URL", raising=False)
    get_settings.cache_clear()
    yield db_path
    get_settings.cache_clear()


@pytest.fixture(autouse=True)
async def reset_engine():
    yield
    await dispose_engine()
