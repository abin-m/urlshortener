# Observability

Stack: Prometheus → Alertmanager + Grafana. All wired via Docker Compose.

## Metrics

Exposed at `GET /metrics` (Prometheus text format).

Key metrics:

| Metric | Type | Description |
|--------|------|-------------|
| `urlshortener_requests_total` | Counter | Requests by method, path, status |
| `urlshortener_request_duration_seconds` | Histogram | Latency by endpoint |

## Grafana

- URL: http://localhost:3000 (default creds: `admin/admin`)
- Dashboard auto-provisioned from `infra/grafana/provisioning/`

## Alerts

Defined in `infra/alerts.yml`, routed via `infra/alertmanager.yml`.

To reload Prometheus config without restart:

```bash
curl -X POST http://localhost:9090/-/reload
```
