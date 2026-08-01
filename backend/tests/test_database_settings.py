"""Tests for database and LLM settings."""

from policritique.settings import Settings


def test_default_uses_sqlite():
    settings = Settings(_env_file=None)
    assert settings.is_sqlite
    assert settings.resolved_database_url.startswith("sqlite+aiosqlite:///")


def test_postgresql_url_normalized_to_asyncpg():
    settings = Settings(
        _env_file=None,
        DATABASE_URL="postgresql://user:pass@localhost:5432/postgres",
    )
    assert settings.resolved_database_url == (
        "postgresql+asyncpg://user:pass@localhost:5432/postgres"
    )
    assert not settings.is_sqlite


def test_database_schema_trimmed():
    settings = Settings(_env_file=None, DATABASE_SCHEMA="  policritique  ")
    assert settings.database_schema == "policritique"


def test_resolved_llm_provider_prefers_openai_in_auto():
    settings = Settings(_env_file=None, OPENAI_API_KEY="sk-test")
    assert settings.resolved_llm_provider() == "openai"


def test_resolved_llm_provider_falls_back_to_lmstudio():
    settings = Settings(_env_file=None, LLM_PROVIDER="auto")
    assert settings.resolved_llm_provider() == "lmstudio"
