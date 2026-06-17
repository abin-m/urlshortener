# syntax=docker/dockerfile:1

# Build stage
FROM python:3.12-slim AS build

ENV PIP_NO_CACHE_DIR=1 PIP_DISABLE_PIP_VERSION_CHECK=1
WORKDIR /build

COPY pyproject.toml README.md ./
COPY src ./src

RUN python -m pip install --upgrade pip build \
    && python -m build --wheel --outdir /dist

# Runtime stage 
FROM python:3.12-slim AS runtime

LABEL org.opencontainers.image.title="urlshortener" \
      org.opencontainers.image.description="A simple URL shortener service." \
      org.opencontainers.image.version="0.1.0"

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    URLSHORTENER_HOST=0.0.0.0 \
    URLSHORTENER_PORT=8000

# Run as an unprivileged user (rootless).
RUN groupadd --gid 1000 app \
    && useradd --uid 1000 --gid 1000 --no-create-home --shell /usr/sbin/nologin app

WORKDIR /app
COPY --from=build /dist/*.whl /tmp/
RUN python -m pip install /tmp/*.whl && rm -f /tmp/*.whl

USER app
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/healthz').status==200 else 1)"

ENTRYPOINT ["urlshortener", "serve"]
