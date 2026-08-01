"""Serve a Vite static build from FastAPI (Cloud Run bundled mode)."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

_RESERVED_PREFIXES = (
    "api",
    "health",
    "docs",
    "openapi.json",
    "redoc",
)


def mount_static_web(app: FastAPI, static_dir: Path | None) -> None:
    if static_dir is None or not static_dir.is_dir():
        return

    vite_assets = static_dir / "assets"
    if vite_assets.is_dir():
        app.mount("/assets", StaticFiles(directory=vite_assets), name="vite_assets")

    @app.get("/", include_in_schema=False)
    async def web_index() -> FileResponse:
        return _file_response(static_dir / "index.html")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def web_fallback(full_path: str) -> FileResponse:
        if full_path.startswith("assets/"):
            raise HTTPException(status_code=404, detail="Not found")
        if full_path.split("/", 1)[0] in _RESERVED_PREFIXES:
            raise HTTPException(status_code=404, detail="Not found")

        candidate = _resolve_static_file(static_dir, full_path)
        if candidate is not None:
            return FileResponse(candidate)

        index = static_dir / "index.html"
        if index.is_file():
            return FileResponse(index)
        raise HTTPException(status_code=404, detail="Not found")


def _resolve_static_file(static_dir: Path, full_path: str) -> Path | None:
    cleaned = full_path.strip("/")
    if not cleaned:
        return static_dir / "index.html" if (static_dir / "index.html").is_file() else None

    candidate = static_dir / cleaned
    if candidate.is_file():
        return candidate
    return None


def _file_response(path: Path) -> FileResponse:
    if not path.is_file():
        raise HTTPException(status_code=404, detail="Not found")
    return FileResponse(path)
