"""Ensure ORM DDL is valid on Postgres (Cloud Run uses Supabase)."""

from sqlalchemy.dialects import postgresql, sqlite
from sqlalchemy.schema import CreateTable

from policritique.db.models import Party


def _create_table_sql(dialect) -> str:
    return str(CreateTable(Party.__table__).compile(dialect=dialect()))


def test_collected_at_default_is_postgres_compatible():
    ddl = _create_table_sql(postgresql.dialect)
    assert "datetime(" not in ddl
    assert "CURRENT_TIMESTAMP" in ddl


def test_collected_at_default_is_sqlite_compatible():
    ddl = _create_table_sql(sqlite.dialect)
    assert "CURRENT_TIMESTAMP" in ddl
