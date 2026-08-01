"""Async database persistence via SQLAlchemy."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from policritique.console import info, warn
from policritique.db.engine import get_engine, get_session_maker
from policritique.db.init_db import init_schema
from policritique.db.models import SyncLog
from policritique.settings import Settings, get_settings


def _now() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")


class Database:
    def __init__(self, path: Path | None = None) -> None:
        settings = get_settings()
        self.settings: Settings = settings
        self.path = path or settings.resolved_db_path
        self._engine = get_engine()
        self._sessions = get_session_maker()

    async def close(self) -> None:
        pass

    async def init(self) -> Path:
        if self.settings.is_sqlite:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            existed = self.path.exists()
        else:
            existed = True

        await init_schema(self._engine)

        if self.settings.is_sqlite:
            if existed and self.path.exists():
                warn(f"Database already exists: [bold]{self.path}[/bold]")
                info("Schema up to date")
            else:
                info(f"Created database: [bold]{self.path}[/bold]")
        else:
            info("Postgres schema up to date")

        return self.path

    def ensure_exists(self) -> None:
        if self.settings.is_sqlite and not self.path.exists():
            raise FileNotFoundError(
                f"Database not found at {self.path}. Run: policritique init-db"
            )

    async def log_sync(self, entity_type: str, entity_ref: str, status: str, message: str) -> None:
        async with self._sessions() as session:
            session.add(
                SyncLog(
                    entity_type=entity_type,
                    entity_ref=entity_ref,
                    status=status,
                    message=message,
                    synced_at=_now(),
                )
            )
            await session.commit()
