import logging
from collections.abc import Callable

from apscheduler.schedulers.blocking import BlockingScheduler

logger = logging.getLogger(__name__)


def run_scheduled(func: Callable, interval_minutes: int) -> None:
    scheduler = BlockingScheduler()
    scheduler.add_job(
        func,
        "interval",
        minutes=interval_minutes,
        misfire_grace_time=300,
        max_instances=1,
    )
    logger.info("Scheduler started, running every %d minutes", interval_minutes)
    # Run immediately on start
    func()
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler stopped")
