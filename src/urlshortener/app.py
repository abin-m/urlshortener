from __future__ import annotations

import logging
import secrets
import string
import time
from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import RedirectResponse
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from pydantic import BaseModel, HttpUrl
from sqlalchemy import Engine, create_engine
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response as StarletteResponse

from .config import Settings
from .metrics import HTTP_REQUEST_DURATION, HTTP_REQUESTS, LINKS_CREATED, REDIRECTS
from .storage import CodeExistsError, LinkNotFoundError, LinkStore

logger = logging.getLogger(__name__)

_ALPHABET = string.ascii_letters + string.digits
_MAX_ATTEMPTS = 5


class _MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[StarletteResponse]],
    ) -> StarletteResponse:
        if request.url.path == "/metrics":
            return await call_next(request)

        start = time.perf_counter()
        response = await call_next(request)
        duration = time.perf_counter() - start

        route = request.scope.get("route")
        path = route.path if route else request.url.path

        HTTP_REQUESTS.labels(request.method, path, response.status_code).inc()
        HTTP_REQUEST_DURATION.labels(request.method, path).observe(duration)

        return response


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
    app.add_middleware(_MetricsMiddleware)

    @app.get("/metrics", include_in_schema=False)
    def metrics_endpoint() -> Response:
        return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

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
            LINKS_CREATED.inc()
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
        REDIRECTS.inc()
        return RedirectResponse(url=url, status_code=307)

    return app
