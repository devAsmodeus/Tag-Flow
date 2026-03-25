import argparse
import logging

from src.infrastructure.config import Settings
from src.infrastructure.container import Container
from src.infrastructure.logger import setup_logging
from src.infrastructure.migrations import run_migrations
from src.infrastructure.scheduler import run_scheduled

logger = logging.getLogger(__name__)


def main() -> None:
    parser = argparse.ArgumentParser(description="Tag-Flow: marketplace review automation")
    parser.add_argument("--once", action="store_true", help="Run pipeline once and exit")
    parser.add_argument("--migrate", action="store_true", help="Run database migrations and exit")
    args = parser.parse_args()

    settings = Settings()
    setup_logging(settings.log_level)

    container = Container(settings)

    if args.migrate:
        run_migrations(container.db)
        container.close()
        return

    run_migrations(container.db)

    if args.once:
        logger.info("Running pipeline once")
        container.pipeline.run()
    else:
        logger.info("Starting scheduled pipeline (every %d min)", settings.poll_interval_minutes)
        run_scheduled(container.pipeline.run, settings.poll_interval_minutes)

    container.close()


if __name__ == "__main__":
    main()
