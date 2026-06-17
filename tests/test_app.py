from __future__ import annotations

import os
import pytest

from fastapi.testclient import TestClient
from urlshortener.app import create_app
from urlshortener.config import Settings
from urlshortener.storage import CodeExistsError, LinkNotFoundError


class FakeStore:
    """In-memory stand-in for LinkStore."""

    def __init__(self) -> None:
        self._data: dict[str, list[object]] = {}  # code -> [url, visits]

    def create(self, code: str, url: str) -> None:
        if code in self._data:
            raise CodeExistsError(code)
        self._data[code] = [url, 0]

    def get_stats(self, code: str) -> tuple[str, int]:
        if code not in self._data:
            raise LinkNotFoundError(code)
        url, visits = self._data[code]
        return str(url), int(visits)  # type: ignore[arg-type]

    def resolve_and_count(self, code: str) -> str:
        if code not in self._data:
            raise LinkNotFoundError(code)
        self._data[code][1] = int(self._data[code][1]) + \
            1  # type: ignore[arg-type]
        return str(self._data[code][0])

    def ping(self) -> None:
        return None


@pytest.fixture()
def client() -> TestClient:
    settings = Settings(base_url="http://testserver", code_length=6)
    app = create_app(settings, store=FakeStore())  # type: ignore[arg-type]
    with TestClient(app) as test_client:
        yield test_client


def test_healthz_returns_ok(client: TestClient) -> None:
    resp = client.get("/healthz")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_shorten_returns_code_of_configured_length(client: TestClient) -> None:
    resp = client.post("/shorten", json={"url": "https://example.com"})
    assert resp.status_code == 201
    body = resp.json()
    assert len(body["code"]) == 6
    assert body["short_url"].endswith(body["code"])


def test_shorten_then_redirect_round_trips(client: TestClient) -> None:
    code = client.post(
        "/shorten", json={"url": "https://example.com"}).json()["code"]
    redirect = client.get(f"/{code}", follow_redirects=False)
    assert redirect.status_code == 307
    assert redirect.headers["location"] == "https://example.com/"


def test_stats_reflects_visit_count(client: TestClient) -> None:
    code = client.post(
        "/shorten", json={"url": "https://example.com"}).json()["code"]
    client.get(f"/{code}", follow_redirects=False)
    client.get(f"/{code}", follow_redirects=False)
    assert client.get(f"/stats/{code}").json()["visits"] == 2


def test_unknown_code_returns_404(client: TestClient) -> None:
    assert client.get("/nope").status_code == 404
    assert client.get("/stats/nope").status_code == 404


def test_invalid_url_returns_422(client: TestClient) -> None:
    assert client.post(
        "/shorten", json={"url": "not-a-url"}).status_code == 422


def test_settings_read_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for key in list(os.environ):
        if key.startswith("URLSHORTENER_"):
            monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("URLSHORTENER_PORT", "9999")
    assert Settings().port == 9999
