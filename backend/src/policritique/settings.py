"""Application settings loaded from environment and .env file."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, SecretStr, computed_field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = BACKEND_ROOT.parent

LlmProviderSetting = Literal["auto", "openai", "lmstudio", "ollama"]

DEFAULT_CORS_ORIGINS = (
    "http://localhost:5173,"
    "http://127.0.0.1:5173,"
    "http://localhost:3000,"
    "http://127.0.0.1:3000,"
    "http://localhost:8000,"
    "http://127.0.0.1:8000"
)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BACKEND_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    db_path: Path | None = Field(default=None, validation_alias="DB_PATH")
    database_url: str | None = Field(default=None, validation_alias="DATABASE_URL")
    database_schema: str = Field(default="", validation_alias="DATABASE_SCHEMA")
    members_api_base_url: str = Field(
        default="https://members-api.parliament.uk",
        validation_alias="MEMBERS_API_BASE_URL",
    )
    parliament_data_base_url: str = Field(
        default="http://data.parliament.uk/membersdataplatform",
        validation_alias="PARLIAMENT_DATA_BASE_URL",
    )
    democracy_club_api_base_url: str = Field(
        default="https://candidates.democracyclub.org.uk",
        validation_alias="DEMOCRACY_CLUB_API_BASE_URL",
    )
    psephology_base_url: str = Field(
        default="https://raw.githubusercontent.com/ukparliament/psephology/main/db/data",
        validation_alias="PSEPHOLOGY_BASE_URL",
    )
    manifesto_project_api_key: str | None = Field(
        default=None,
        validation_alias="MANIFESTO_PROJECT_API_KEY",
    )
    manifesto_project_base_url: str = Field(
        default="https://manifesto-project.wzb.eu/api/v1",
        validation_alias="MANIFESTO_PROJECT_BASE_URL",
    )
    manifesto_project_core_version: str = Field(
        default="MPDS2025a",
        validation_alias="MANIFESTO_PROJECT_CORE_VERSION",
    )
    manifesto_project_metadata_version: str = Field(
        default="2025-1",
        validation_alias="MANIFESTO_PROJECT_METADATA_VERSION",
    )
    secret_key: SecretStr = Field(
        default=SecretStr("change-me-in-production"),
        validation_alias="SECRET_KEY",
    )
    jwt_lifetime_seconds: int = Field(default=3600, validation_alias="JWT_LIFETIME_SECONDS")
    cors_origins_raw: str = Field(
        default=DEFAULT_CORS_ORIGINS,
        validation_alias="CORS_ORIGINS",
    )
    api_host: str = Field(default="127.0.0.1", validation_alias="API_HOST")
    api_port: int = Field(default=8000, validation_alias="API_PORT")
    api_reload: bool = Field(default=False, validation_alias="API_RELOAD")
    static_dir: str | None = Field(default=None, validation_alias="STATIC_DIR")
    llm_provider: LlmProviderSetting = Field(default="auto", validation_alias="LLM_PROVIDER")
    openai_api_key: SecretStr | None = Field(default=None, validation_alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4o-mini", validation_alias="OPENAI_MODEL")
    lmstudio_base_url: str = Field(
        default="http://localhost:1234/v1",
        validation_alias="LMSTUDIO_BASE_URL",
    )
    lmstudio_model: str = Field(default="local-model", validation_alias="LMSTUDIO_MODEL")
    lmstudio_api_key: SecretStr = Field(
        default=SecretStr("lm-studio"),
        validation_alias="LMSTUDIO_API_KEY",
    )
    ollama_base_url: str = Field(
        default="http://127.0.0.1:11434",
        validation_alias="OLLAMA_BASE_URL",
    )
    ollama_model: str = Field(default="llama3.2", validation_alias="OLLAMA_MODEL")

    @field_validator("db_path", mode="before")
    @classmethod
    def empty_db_path_is_none(cls, value: object) -> Path | None:
        if value is None:
            return None
        if isinstance(value, str) and not value.strip():
            return None
        path = Path(value) if not isinstance(value, Path) else value
        if path == Path("."):
            return None
        return path

    @field_validator("database_url", mode="before")
    @classmethod
    def normalize_database_url(cls, value: str | None) -> str | None:
        if value is None:
            return None
        url = str(value).strip()
        if not url:
            return None
        if url.startswith("postgresql://"):
            return "postgresql+asyncpg://" + url.removeprefix("postgresql://")
        if url.startswith("postgres://"):
            return "postgresql+asyncpg://" + url.removeprefix("postgres://")
        return url

    @field_validator("database_schema", mode="before")
    @classmethod
    def normalize_database_schema(cls, value: str | None) -> str:
        if value is None:
            return ""
        return str(value).strip()

    @field_validator("static_dir", mode="before")
    @classmethod
    def empty_static_dir_is_none(cls, value: str | None) -> str | None:
        if value is None:
            return None
        if isinstance(value, str) and not value.strip():
            return None
        return value.strip()

    @computed_field  # type: ignore[prop-decorator]
    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins_raw.split(",") if origin.strip()]

    @property
    def schema_path(self) -> Path:
        return REPO_ROOT / "scripts" / "db" / "schema.sql"

    @property
    def resolved_db_path(self) -> Path:
        path = self.db_path or BACKEND_ROOT / "data" / "policritique.db"
        if not path.is_absolute():
            path = BACKEND_ROOT / path
        return path

    @property
    def is_sqlite(self) -> bool:
        return self.resolved_database_url.startswith("sqlite")

    @property
    def resolved_database_url(self) -> str:
        if self.database_url:
            return self.database_url
        return f"sqlite+aiosqlite:///{self.resolved_db_path}"

    @property
    def static_dir_path(self) -> Path | None:
        if self.static_dir is None:
            return None
        return Path(self.static_dir)

    def has_openai_api_key(self) -> bool:
        if self.openai_api_key is None:
            return False
        return bool(self.openai_api_key.get_secret_value().strip())

    def resolved_llm_provider(self) -> str | None:
        if self.llm_provider == "openai":
            return "openai" if self.has_openai_api_key() else None
        if self.llm_provider == "lmstudio":
            return "lmstudio"
        if self.llm_provider == "ollama":
            return "ollama"
        if self.has_openai_api_key():
            return "openai"
        return "lmstudio"


@lru_cache
def get_settings() -> Settings:
    return Settings()
