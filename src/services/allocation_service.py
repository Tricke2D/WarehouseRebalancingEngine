from dataclasses import dataclass
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.models.warehouse import Warehouse
from src.domain.models.stock_level import StockLevel


@dataclass
class AllocationRequest:
    sku_id: int
    quantity: int
    delivery_latitude: float
    delivery_longitude: float


@dataclass
class AllocationResult:
    success: bool
    is_split: bool = False
    allocations: list[tuple[int, int]] = None
    error_code: str | None = None
    error_message: str | None = None


class AllocationService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def allocate_order(self, request: AllocationRequest) -> AllocationResult:
        # Cari gudang pertama yang punya stock cukup
        stmt = (
            select(Warehouse, StockLevel)
            .join(StockLevel, StockLevel.warehouse_id == Warehouse.id)
            .where(
                Warehouse.is_active == True,
                StockLevel.sku_id == request.sku_id,
                (StockLevel.quantity - StockLevel.reserved_quantity) >= request.quantity,
            )
            .limit(1)
        )

        result = await self.db.execute(stmt)
        row = result.first()

        if not row:
            return AllocationResult(
                success=False,
                allocations=[],
                error_code="NO_STOCK",
                error_message="Tidak ada gudang dengan stock cukup",
            )

        warehouse, stock = row
        
        # Reserve stock
        stock.reserved_quantity += request.quantity
        stock.version += 1
        await self.db.flush()

        return AllocationResult(
            success=True,
            is_split=False,
            allocations=[(warehouse.id, request.quantity)],
        )