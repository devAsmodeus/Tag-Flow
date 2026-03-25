import logging
from collections.abc import Generator
from contextlib import contextmanager

from psycopg2 import pool
from psycopg2.extras import RealDictCursor

logger = logging.getLogger(__name__)


class Database:
    def __init__(self, dsn: str, min_conn: int = 1, max_conn: int = 5) -> None:
        self._pool = pool.ThreadedConnectionPool(min_conn, max_conn, dsn)
        logger.info("Database connection pool created")

    @contextmanager
    def connection(self) -> Generator:
        conn = self._pool.getconn()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            self._pool.putconn(conn)

    @contextmanager
    def cursor(self, dict_cursor: bool = True) -> Generator:
        with self.connection() as conn:
            cursor_factory = RealDictCursor if dict_cursor else None
            with conn.cursor(cursor_factory=cursor_factory) as cur:
                yield cur

    def close(self) -> None:
        self._pool.closeall()
        logger.info("Database connection pool closed")
