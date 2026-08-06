import logging
from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db_session
from src.domain.models.stock_level import StockLevel
from src.domain.models.warehouse import Warehouse
from src.domain.models.sku import SKU
from src.domain.models.transfer_order import TransferOrder
from src.domain.enums import TransferStatus

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/v1/dashboard", tags=["dashboard"])


@router.get("/heatmap")
async def get_stock_heatmap(db: AsyncSession = Depends(get_db_session)):
    wh_stmt = select(Warehouse).where(Warehouse.is_active == True)
    wh_result = await db.execute(wh_stmt)
    warehouses = wh_result.scalars().all()

    sku_stmt = select(SKU)
    sku_result = await db.execute(sku_stmt)
    skus = sku_result.scalars().all()

    stock_stmt = select(StockLevel)
    stock_result = await db.execute(stock_stmt)
    stock_levels = stock_result.scalars().all()

    cells = []
    for stock in stock_levels:
        available = stock.available_quantity
        utilization_pct = (
            round((stock.reserved_quantity / stock.quantity) * 100, 1)
            if stock.quantity > 0
            else 0.0
        )
        cells.append({
            "warehouse_id": stock.warehouse_id,
            "sku_id": stock.sku_id,
            "quantity": stock.quantity,
            "reserved_quantity": stock.reserved_quantity,
            "available": available,
            "utilization_pct": utilization_pct,
        })

    return {
        "warehouses": [
            {"id": w.id, "code": w.code, "city": w.city} for w in warehouses
        ],
        "skus": [
            {"id": s.id, "code": s.code, "name": s.name} for s in skus
        ],
        "cells": cells,
    }


@router.get("/summary")
async def get_dashboard_summary(db: AsyncSession = Depends(get_db_session)):
    total_warehouses = await db.scalar(select(func.count(Warehouse.id)))
    total_skus = await db.scalar(select(func.count(SKU.id)))
    total_stock_units = await db.scalar(select(func.sum(StockLevel.quantity))) or 0
    pending_transfers = await db.scalar(
        select(func.count(TransferOrder.id)).where(
            TransferOrder.status == TransferStatus.SUGGESTED
        )
    )

    return {
        "total_warehouses": total_warehouses,
        "total_skus": total_skus,
        "total_stock_units": int(total_stock_units),
        "pending_transfer_suggestions": pending_transfers,
    }