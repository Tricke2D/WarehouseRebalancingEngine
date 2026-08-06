import logging

from src.core.database import AsyncSessionFactory
from src.services.demand_velocity_service import DemandVelocityService
from src.services.rebalancing_service import RebalancingService

logger = logging.getLogger(__name__)


async def run_nightly_rebalance_job() -> None:
    logger.info("=== Starting nightly rebalance job ===")

    async with AsyncSessionFactory() as session:
        try:
            velocity_service = DemandVelocityService(session)
            velocities = await velocity_service.calculate_all_velocities()

            logger.info(f"Velocity calculated for {len(velocities)} combinations")

            rebalancing_service = RebalancingService(session)
            suggestions = await rebalancing_service.generate_transfer_suggestions(
                velocities=velocities,
            )

            await session.commit()

            logger.info(
                f"=== Nightly rebalance job completed: "
                f"{len(suggestions)} transfer suggestions generated ==="
            )

        except Exception as exc:
            await session.rollback()
            logger.error(f"Nightly rebalance job failed: {exc}", exc_info=True)
            raise