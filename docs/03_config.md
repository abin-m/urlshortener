# Configuration

All env vars use `URLSHORTENER_` prefix.

| Variable                      | Default                                                                  | Notes              |
|-------------------------------|--------------------------------------------------------------------------|--------------------|
| `URLSHORTENER_DATABASE_URL`   | `postgresql+psycopg://urlshortener:urlshortener@localhost:5432/urlshortener` | SQLAlchemy DSN |
| `URLSHORTENER_BASE_URL`       | `http://localhost:8000`                                                  | Used in short link response |
| `URLSHORTENER_HOST`           | `127.0.0.1`                                                              | Bind address       |
| `URLSHORTENER_PORT`           | `8000`                                                                   | Bind port          |
| `URLSHORTENER_CODE_LENGTH`    | `7`                                                                      | Short code length (4–32) |
| `URLSHORTENER_LOG_LEVEL`      | `INFO`                                                                   | Root log level     |

Docker Compose also needs these for Postgres:

```env
POSTGRES_USER=urlshortener
POSTGRES_PASSWORD=secret
POSTGRES_DB=urlshortener
```
