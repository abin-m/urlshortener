from __future__ import annotations

import logging
import secrets
import string
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, HttpUrl
from sqlalchemy import Engine, create_engine

from .config import Settings
from .storage import CodeExistsError, LinkNotFoundError, LinkStore

logger = logging.getLogger(__name__)

_ALPHABET = string.ascii_letters + string.digits
_MAX_ATTEMPTS = 5


class ShortenRequest(BaseModel):
    url: HttpUrl


class LinkResponse(BaseModel):
    code: str
    short_url: str


def _make_code(length: int) -> str:
    return "".join(secrets.choice(_ALPHABET) for _ in range(length))


def create_app(settings: Settings, store: LinkStore | None = None) -> FastAPI:
    """``store`` exists for test injection; production builds it from settings."""
    engine: Engine | None = None
    if store is None:
        engine = create_engine(settings.database_url)
        store = LinkStore(engine)

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        if engine is not None:
            store.init_schema()
        logger.info("Application started")
        yield
        if engine is not None:
            engine.dispose()
        logger.info("Application stopped")

    app = FastAPI(title="URL Shortener", version="0.1.0", lifespan=lifespan)

    @app.get("/healthz")
    def healthz() -> dict[str, str]:
        try:
            store.ping()
        except Exception as exc:  # noqa: BLE001 - report as unhealthy
            raise HTTPException(
                status_code=503, detail="database unavailable") from exc
        return {"status": "ok"}

    @app.post("/shorten", response_model=LinkResponse, status_code=201)
    def shorten(payload: ShortenRequest) -> LinkResponse:
        for _ in range(_MAX_ATTEMPTS):
            code = _make_code(settings.code_length)
            try:
                store.create(code, str(payload.url))
            except CodeExistsError:
                continue
            return LinkResponse(
                code=code, short_url=f"{settings.base_url.rstrip('/')}/{code}"
            )
        raise HTTPException(
            status_code=500, detail="could not generate a unique code")

    @app.get("/stats/{code}")
    def stats(code: str) -> dict[str, object]:
        try:
            url, visits = store.get_stats(code)
        except LinkNotFoundError as exc:
            raise HTTPException(
                status_code=404, detail="code not found") from exc
        return {"code": code, "url": url, "visits": visits}

    @app.get("/{code}")
    def redirect(code: str) -> RedirectResponse:
        try:
            url = store.resolve_and_count(code)
        except LinkNotFoundError as exc:
            raise HTTPException(
                status_code=404, detail="code not found") from exc
        return RedirectResponse(url=url, status_code=307)

    return app
