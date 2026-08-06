import logging
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.models.order import Order, OrderItem
from src.domain.enums import OrderStatus

logger = logging.getLogger(__name__)

DEFAULT_VELOCITY_WINDOW_DAYS = 7


@dataclass
class VelocityMetric:
    warehouse_id: int
    sku_id: int
    total_quantity_sold: int
    velocity_per_day: float
    window_days: int


class DemandVelocityService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def calculate_all_velocities(
        self,
        window_days: int = DEFAULT_VELOCITY_WINDOW_DAYS,
    ) -> list[VelocityMetric]:
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=window_days)

        stmt = (
            select(
                OrderItem.allocated_warehouse_id.label("warehouse_id"),
                OrderItem.sku_id.label("sku_id"),
                func.sum(OrderItem.allocated_quantity).label("total_qty"),
            )
            .join(Order, Order.id == OrderItem.order_id)
            .where(
                OrderItem.allocated_warehouse_id.is_not(None),
                Order.created_at >= cutoff_date,
                Order.status.in_([
                    OrderStatus.ALLOCATED,
                    OrderStatus.PARTIALLY_ALLOCATED,
                    OrderStatus.COMPLETED,
                ]),
            )
            .group_by(OrderItem.allocated_warehouse_id, OrderItem.sku_id)
        )

        result = await self.db.execute(stmt)
        rows = result.all()

        metrics = []
        for row in rows:
            total_qty = int(row.total_qty or 0)
            velocity = total_qty / window_days

            metrics.append(
                VelocityMetric(
                    warehouse_id=row.warehouse_id,
                    sku_id=row.sku_id,
                    total_quantity_sold=total_qty,
                    velocity_per_day=round(velocity, 3),
                    window_days=window_days,
                )
            )

        logger.info(
            f"Calculated velocity for {len(metrics)} warehouse-sku combinations "
            f"(window={window_days} days)"
        )
        return metrics