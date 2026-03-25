import logging
from pathlib import Path

from src.domain.exceptions import MigrationError
from src.infrastructure.database import Database

logger = logging.getLogger(__name__)

VERSIONS_DIR = Path(__file__).parent / "versions"


def run_migrations(db: Database) -> None:
    _ensure_migrations_table(db)
    applied = _get_applied(db)

    sql_files = sorted(VERSIONS_DIR.glob("*.sql"))
    new_count = 0

    for sql_file in sql_files:
        version = sql_file.stem
        if version in applied:
            continue

        logger.info("Applying migration: %s", version)
        sql = sql_file.read_text(encoding="utf-8")

        try:
            with db.cursor(dict_cursor=False) as cur:
                cur.execute(sql)
                cur.execute(
                    "INSERT INTO _migrations (version) VALUES (%s)",
                    (version,),
                )
            new_count += 1
        except Exception as e:
            raise MigrationError(f"Migration {version} failed: {e}") from e

    if new_count:
        logger.info("Applied %d new migration(s)", new_count)
    else:
        logger.info("Database is up to date")


def _ensure_migrations_table(db: Database) -> None:
    with db.cursor(dict_cursor=False) as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS _migrations (
                version VARCHAR(255) PRIMARY KEY,
                applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
        """)


def _get_applied(db: Database) -> set[str]:
    with db.cursor() as cur:
        cur.execute("SELECT version FROM _migrations ORDER BY version")
        return {row["version"] for row in cur.fetchall()}
