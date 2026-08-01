"""Click + Rich CLI for UK political data collection."""

from __future__ import annotations

import asyncio

import click

from policritique.collectors.elections import collect_general_elections
from policritique.collectors.manifestos import collect_manifestos
from policritique.collectors.members import collect_members
from policritique.db.store import Database
from policritique.parliament.psephology import DEFAULT_PARLIAMENTS


def _run(coro) -> None:
    asyncio.run(coro)


@click.group()
@click.version_option(package_name="policritique", prog_name="policritique")
def cli() -> None:
    """Collect and analyse UK political open data."""


@cli.command("init-db")
def init_db() -> None:
    """Create or migrate the database schema."""

    async def _init() -> None:
        from policritique.auth.models import User  # noqa: F401 — register user table

        db = Database()
        try:
            await db.init()
        finally:
            await db.close()

    _run(_init())


@cli.command("collect-elections")
@click.option(
    "--parliament",
    "parliament_ids",
    multiple=True,
    type=int,
    help=f"Parliament period to import (default: {', '.join(map(str, DEFAULT_PARLIAMENTS))})",
)
def collect_elections(parliament_ids: tuple[int, ...]) -> None:
    """Import general election results from UK Parliament psephology CSVs."""

    async def _collect() -> None:
        db = Database()
        try:
            db.ensure_exists()
            await collect_general_elections(
                db,
                parliament_ids=list(parliament_ids) or None,
            )
        finally:
            await db.close()

    _run(_collect())


@cli.command("collect-members")
@click.option(
    "--all-members",
    is_flag=True,
    help="Include former as well as current Commons members (default: current only).",
)
def collect_members_cmd(all_members: bool) -> None:
    """Import MPs from the Members API and contact details from MNIS."""

    async def _collect() -> None:
        db = Database()
        try:
            db.ensure_exists()
            await collect_members(db, current_only=not all_members)
        finally:
            await db.close()

    _run(_collect())


@cli.command("collect-manifestos")
@click.option("--skip-project", is_flag=True, help="Skip Manifesto Project API import.")
@click.option("--skip-pdfs", is_flag=True, help="Skip official/archived party PDF import.")
def collect_manifestos_cmd(skip_project: bool, skip_pdfs: bool) -> None:
    """Import manifestos from Manifesto Project and party PDF sources."""

    async def _collect() -> None:
        db = Database()
        try:
            db.ensure_exists()
            await collect_manifestos(
                db,
                include_project=not skip_project,
                include_pdfs=not skip_pdfs,
            )
        finally:
            await db.close()

    _run(_collect())


def main() -> None:
    cli()


if __name__ == "__main__":
    main()
