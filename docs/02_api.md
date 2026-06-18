# API

Base URL: `http://localhost:8000`

| Method | Path            | Description               |
|--------|-----------------|---------------------------|
| POST   | `/shorten`      | Create short link         |
| GET    | `/{code}`       | Redirect (307)            |
| GET    | `/stats/{code}` | Visit count + original URL|
| GET    | `/healthz`      | Liveness + DB check       |
| GET    | `/metrics`      | Prometheus metrics        |

## Examples

```bash
# shorten
curl -X POST http://localhost:8000/shorten \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/long/path"}'
# {"code": "aB3kR7z", "short_url": "http://localhost:8000/aB3kR7z"}

# redirect (follow it)
curl -L http://localhost:8000/aB3kR7z

# stats
curl http://localhost:8000/stats/aB3kR7z
# {"code": "aB3kR7z", "url": "https://example.com/long/path", "visits": 4}
```
