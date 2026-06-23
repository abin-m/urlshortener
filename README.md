# urlshortener

Self-hosted URL shortener. Shorten URLs, redirect, track visits. 

[![CI](https://github.com/abin-m/urlshortener/actions/workflows/ci.yml/badge.svg)](https://github.com/abin-m/urlshortener/actions/workflows/ci.yml)
[![PyPI version](https://img.shields.io/pypi/v/bh-urlshortener?logo=pypi)](https://pypi.org/project/bh-urlshortener/) 
## Quickstart

**Docker Compose (recommended)**

```bash
# create an .env file by following the configs docs  
# set POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB
docker compose up -d
```

**Local**

```bash
pip install -e .
export URLSHORTENER_DATABASE_URL="postgresql+psycopg://user:pass@localhost:5432/urlshortener"
urlshortener serve
```

App runs at `http://localhost:8000`.

---

## API

| Method | Path            | Description                  |
|--------|-----------------|------------------------------|
| POST   | `/shorten`      | Create short link            |
| GET    | `/{code}`       | Redirect to original (307)   |
| GET    | `/stats/{code}` | Visit count + original URL   |
| GET    | `/healthz`      | Liveness + DB check          |
| GET    | `/metrics`      | Prometheus metrics           |

```bash
curl -X POST http://localhost:8000/shorten \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/long/path"}'
# {"code": "aB3kR7z", "short_url": "http://localhost:8000/aB3kR7z"}

curl http://localhost:8000/stats/aB3kR7z
# {"code": "aB3kR7z", "url": "https://example.com/long/path", "visits": 4}
```

---



## Development

```bash
pip install -e ".[test]"

pytest        # test + coverage
mypy src      # type check
tox           # full matrix
```

Tests run against an in-memory fake store — no DB required.

---

## Observability

Docker Compose includes Prometheus, Alertmanager, and Grafana.

| Service      | URL                       |
|--------------|---------------------------|
| Grafana      | http://localhost:3000     |
| Prometheus   | http://localhost:9090     |
| Alertmanager | http://localhost:9093     |

See [`docs/05_observability.md`](docs/05_observability.md) for details.

---

## Docs

- [`docs/01_setup.md`](docs/01_setup.md)
- [`docs/02_api.md`](docs/02_api.md)
- [`docs/03_config.md`](docs/03_config.md)
- [`docs/04_development.md`](docs/04_development.md)
- [`docs/05_observability.md`](docs/05_observability.md)

---

## License

MIT
