"""Tests for static web fallback routing."""

from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

from policritique.api.static_web import mount_static_web


def test_spa_fallback_serves_index_for_client_route(tmp_path: Path) -> None:
    static_dir = tmp_path / "static"
    static_dir.mkdir()
    (static_dir / "index.html").write_text(
        "<html><body>policritique</body></html>",
        encoding="utf-8",
    )

    app = FastAPI()
    mount_static_web(app, static_dir)
    client = TestClient(app)

    response = client.get("/elections")

    assert response.status_code == 200
    assert "policritique" in response.text


def test_static_asset_served_from_root(tmp_path: Path) -> None:
    static_dir = tmp_path / "static"
    static_dir.mkdir()
    (static_dir / "index.html").write_text("<html></html>", encoding="utf-8")
    (static_dir / "favicon.svg").write_text("<svg></svg>", encoding="utf-8")

    app = FastAPI()
    mount_static_web(app, static_dir)
    client = TestClient(app)

    response = client.get("/favicon.svg")

    assert response.status_code == 200
    assert "<svg>" in response.text
