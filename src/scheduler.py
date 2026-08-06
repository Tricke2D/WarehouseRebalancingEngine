import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from src.jobs.nightly_rebalance_job import run_nightly_rebalance_job

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


def setup_scheduled_jobs() -> None:
    scheduler.add_job(
        run_nightly_rebalance_job,
        trigger=CronTrigger(hour=2, minute=0),
        id="nightly_rebalance_job",
        replace_existing=True,
        misfire_grace_time=3600,
    )
    logger.info("Scheduled job registered: nightly_rebalance_job @ 02:00")


def start_scheduler() -> None:
    if not scheduler.running:
        scheduler.start()
        logger.info("APScheduler started")


def shutdown_scheduler() -> None:
    if scheduler.running:
        scheduler.shutdown(wait=True)
        logger.info("APScheduler shut down gracefully")