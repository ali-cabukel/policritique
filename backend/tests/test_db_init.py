import pytest
from sqlalchemy import inspect

from policritique.auth.models import User  # noqa: F401 — register user table
from policritique.db.engine import get_engine
from policritique.db.models import Base
from policritique.db.store import Database


@pytest.mark.asyncio
async def test_init_db_creates_all_tables():
    db = Database()
    await db.init()

    async with get_engine().connect() as conn:
        table_names = await conn.run_sync(
            lambda sync_conn: set(inspect(sync_conn).get_table_names())
        )

    expected = {table.name for table in Base.metadata.sorted_tables}
    assert expected.issubset(table_names)
