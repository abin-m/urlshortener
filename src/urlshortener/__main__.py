from __future__ import annotations

import argparse
import logging
import os
import uvicorn

from .app import create_app
from .config import Settings


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="urlshortener",
        description="URL shortener service.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    serve = sub.add_parser("serve", help="Start the HTTP server.")
    serve.add_argument(
        "--host",
        default=os.environ.get("URLSHORTENER_HOST", "127.0.0.1"),
        help="Bind address (env: URLSHORTENER_HOST).",
    )
    serve.add_argument(
        "--port",
        type=int,
        default=int(os.environ.get("URLSHORTENER_PORT", "8000")),
        help="Bind port (env: URLSHORTENER_PORT).",
    )
    return parser


def main() -> None:
    args = _build_parser().parse_args()

    if args.command == "serve":
        settings = Settings(host=args.host, port=args.port)
        logging.basicConfig(
            level=settings.log_level.upper(),
            format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        )
        app = create_app(settings)
        uvicorn.run(app, host=settings.host, port=settings.port)


if __name__ == "__main__":
    main()
