# Development

## Install

```bash
pip install -e ".[test]"
```

## Tests

```bash
pytest          # runs suite + coverage
mypy src        # strict type check
tox             # full matrix (lint + types + tests)
```

Tests use an in-memory fake store — no real DB needed.

## Project layout

```
src/urlshortener/
  app.py       # FastAPI routes
  storage.py   # DB layer (SQLAlchemy)
  config.py    # Settings (pydantic-settings)
  metrics.py   # Prometheus instrumentation
infra/
  prometheus.yml
  alerts.yml
  alertmanager.yml
  grafana/     # provisioned dashboards
```

## Adding a route

1. Add handler in `app.py`
2. Add storage method in `storage.py` if DB needed
3. Write test in `tests/` against the fake store
