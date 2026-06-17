# urlshortener

A self-hosted URL shortener. Shorten a URL, get a redirect, track visit counts. That's it.



## API

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/shorten` | Create a short link |
| `GET` | `/{code}` | Redirect to original URL (307) |
| `GET` | `/stats/{code}` | Visit count + original URL |
| `GET` | `/healthz` | Liveness + DB connectivity check |

```bash
# shorten
curl -X POST http://localhost:8000/shorten \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/some/long/path"}'
# {"code": "aB3kR7z", "short_url": "http://localhost:8000/aB3kR7z"}

# stats
curl http://localhost:8000/stats/aB3kR7z
# {"code": "aB3kR7z", "url": "https://example.com/some/long/path", "visits": 4}
```

---

## Running locally

**Prerequisites:** Python 3.11, a running PostgreSQL instance.

```bash
pip install -e .

# point at your DB (or rely on the default below)
export URLSHORTENER_DATABASE_URL="postgresql+psycopg://user:pass@localhost:5432/urlshortener"

urlshortener serve
# listening on http://127.0.0.1:8000
```

---

## Docker Compose

Spins up Postgres + app together:

```bash
docker compose up -d 
```


---

## Configuration

All settings are environment variables with the `URLSHORTENER_` prefix.

| Variable | Default | Description |
|----------|---------|-------------|
| `URLSHORTENER_DATABASE_URL` | `postgresql+psycopg://urlshortener:urlshortener@localhost:5432/urlshortener` | SQLAlchemy connection string |
| `URLSHORTENER_BASE_URL` | `http://localhost:8000` | Public base URL used when building short links |
| `URLSHORTENER_HOST` | `127.0.0.1` | Bind address |
| `URLSHORTENER_PORT` | `8000` | Bind port |
| `URLSHORTENER_CODE_LENGTH` | `7` | Length of generated short codes (4–32) |
| `URLSHORTENER_LOG_LEVEL` | `INFO` | Root log level |

---

## Development

```bash
pip install -e ".[test]"

pytest          # runs tests + coverage
mypy src        # strict type checking
```

> Tests use an in-memory fake store 


## License

MIT
