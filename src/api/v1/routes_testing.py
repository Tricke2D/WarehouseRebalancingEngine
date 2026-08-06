import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.database import get_db_session
from src.domain.models.stock_level import StockLevel

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/v1/testing", tags=["testing-only"])


def _ensure_not_production():
    if settings.app_env == "production":
        raise HTTPException(
            status_code=403,
            detail="Testing endpoints are disabled in production",
        )


@router.post("/reset-stock")
async def reset_stock_for_test(
    warehouse_id: int,
    sku_id: int,
    quantity: int,
    db: AsyncSession = Depends(get_db_session),
):
    _ensure_not_production()

    stmt = select(StockLevel).where(
        StockLevel.warehouse_id == warehouse_id,
        StockLevel.sku_id == sku_id,
    )
    result = await db.execute(stmt)
    stock = result.scalar_one_or_none()

    if stock is None:
        stock = StockLevel(
            warehouse_id=warehouse_id,
            sku_id=sku_id,
            quantity=quantity,
            reserved_quantity=0,
            version=1,
        )
        db.add(stock)
    else:
        stock.quantity = quantity
        stock.reserved_quantity = 0
        stock.version += 1

    await db.commit()
    logger.info(f"Stock reset: warehouse={warehouse_id} sku={sku_id} qty={quantity}")

    return {"status": "reset", "warehouse_id": warehouse_id, "sku_id": sku_id, "quantity": quantity}