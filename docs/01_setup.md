# Setup

## Prerequisites

- Python 3.11+
- PostgreSQL 16 (or Docker)

## Local (no Docker)

```bash
pip install -e .

export URLSHORTENER_DATABASE_URL="postgresql+psycopg://user:pass@localhost:5432/urlshortener"

urlshortener serve
# → http://127.0.0.1:8000
```

## Docker Compose (recommended)

```bash
cp .env.example .env   # fill in POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB

docker compose up -d
```

Starts: app, postgres, prometheus, alertmanager, grafana.

| Service     | URL                       |
|-------------|---------------------------|
| App         | http://localhost:8000     |
| Grafana     | http://localhost:3000     |
| Prometheus  | http://localhost:9090     |
| Alertmanager| http://localhost:9093     |
