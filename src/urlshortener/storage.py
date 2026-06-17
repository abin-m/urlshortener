from __future__ import annotations

import logging
from datetime import datetime

from sqlalchemy import BigInteger, Engine, String, func, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    pass


class Link(Base):
    __tablename__ = "links"

    code: Mapped[str] = mapped_column(String, primary_key=True)
    url: Mapped[str] = mapped_column(String, nullable=False)
    visits: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())


class CodeExistsError(Exception):
    pass


class LinkNotFoundError(Exception):
    pass


class LinkStore:
    """Data access for short links over a SQLAlchemy engine."""

    def __init__(self, engine: Engine) -> None:
        self._engine = engine
        self._session_factory = sessionmaker(bind=engine)

    def init_schema(self) -> None:
        Base.metadata.create_all(self._engine)
        logger.info("Schema initialised")

    def create(self, code: str, url: str) -> None:
        """Raises CodeExistsError on duplicate code."""
        with self._session_factory() as session:
            session.add(Link(code=code, url=url))
            try:
                session.commit()
            except IntegrityError as exc:
                session.rollback()
                raise CodeExistsError(code) from exc

    def get_stats(self, code: str) -> tuple[str, int]:
        """Raises LinkNotFoundError if code absent."""
        with self._session_factory() as session:
            link = session.get(Link, code)
        if link is None:
            raise LinkNotFoundError(code)
        return link.url, link.visits

    def resolve_and_count(self, code: str) -> str:
        """Raises LinkNotFoundError if code absent."""
        with self._session_factory() as session:
            row = session.execute(
                update(Link)
                .where(Link.code == code)
                .values(visits=Link.visits + 1)
                .returning(Link.url)
            ).first()
            session.commit()
        if row is None:
            raise LinkNotFoundError(code)
        return str(row[0])

    def ping(self) -> None:
        """Raises if DB unreachable."""
        with self._session_factory() as session:
            session.execute(select(1))
