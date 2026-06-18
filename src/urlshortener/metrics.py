from __future__ import annotations

from prometheus_client import Counter, Histogram, REGISTRY  # noqa: F401

HTTP_REQUESTS = Counter(
    "urlshortener_http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status_code"],
)

HTTP_REQUEST_DURATION = Histogram(
    "urlshortener_http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "path"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0),
)

LINKS_CREATED = Counter(
    "urlshortener_links_created_total",
    "Total short links successfully created",
)

REDIRECTS = Counter(
    "urlshortener_redirects_total",
    "Total redirects served",
)
