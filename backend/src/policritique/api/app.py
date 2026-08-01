"""FastAPI application factory."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from policritique.api.routers import constituencies, elections, manifestos, members, parties
from policritique.api.static_web import mount_static_web
from policritique.auth.deps import auth_backend, fastapi_users
from policritique.auth.models import User  # noqa: F401 — register user table
from policritique.auth.schemas import UserCreate, UserRead, UserUpdate
from policritique.db.engine import dispose_engine, get_engine
from policritique.db.init_db import init_schema
from policritique.settings import get_settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_schema(get_engine())
    yield
    await dispose_engine()


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="policritique API",
        description="Query UK political open data — elections, MPs, and manifestos.",
        version="0.1.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(
        fastapi_users.get_auth_router(auth_backend),
        prefix="/api/auth/jwt",
        tags=["auth"],
    )
    app.include_router(
        fastapi_users.get_register_router(UserRead, UserCreate),
        prefix="/api/auth",
        tags=["auth"],
    )
    app.include_router(
        fastapi_users.get_users_router(UserRead, UserUpdate),
        prefix="/api/users",
        tags=["users"],
    )
    app.include_router(parties.router, prefix="/api")
    app.include_router(elections.router, prefix="/api")
    app.include_router(constituencies.router, prefix="/api")
    app.include_router(members.router, prefix="/api")
    app.include_router(manifestos.router, prefix="/api")

    @app.get("/health", tags=["health"])
    async def health() -> dict[str, str | bool | None]:
        return {
            "status": "ok",
            "database": "postgres" if not settings.is_sqlite else "sqlite",
            "database_schema": settings.database_schema or None,
            "llm_provider": settings.llm_provider,
            "llm_active": settings.resolved_llm_provider(),
            "openai_configured": settings.has_openai_api_key(),
        }

    mount_static_web(app, settings.static_dir_path)

    return app
