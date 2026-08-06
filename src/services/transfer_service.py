import logging
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.models.transfer_order import TransferOrder
from src.domain.models.stock_level import StockLevel
from src.domain.enums import TransferStatus

logger = logging.getLogger(__name__)

VALID_TRANSITIONS: dict[str, list[str]] = {
    TransferStatus.SUGGESTED: [TransferStatus.APPROVED, TransferStatus.REJECTED],
    TransferStatus.APPROVED: [TransferStatus.IN_TRANSIT],
    TransferStatus.IN_TRANSIT: [TransferStatus.COMPLETED],
    TransferStatus.COMPLETED: [],
    TransferStatus.REJECTED: [],
}


@dataclass
class TransferTransitionResult:
    success: bool
    transfer_order: TransferOrder | None = None
    error_code: str | None = None
    error_message: str | None = None


class InsufficientStockError(Exception):
    pass


class TransferService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def transition_status(
        self,
        transfer_id: int,
        new_status: str,
        rejection_reason: str | None = None,
    ) -> TransferTransitionResult:
        stmt = (
            select(TransferOrder)
            .where(TransferOrder.id == transfer_id)
            .with_for_update()
        )
        result = await self.db.execute(stmt)
        transfer = result.scalar_one_or_none()

        if transfer is None:
            return TransferTransitionResult(
                success=False,
                error_code="TRANSFER_NOT_FOUND",
                error_message=f"Transfer order dengan id={transfer_id} tidak ditemukan",
            )

        allowed_next_states = VALID_TRANSITIONS.get(transfer.status, [])
        if new_status not in allowed_next_states:
            return TransferTransitionResult(
                success=False,
                error_code="ILLEGAL_TRANSITION",
                error_message=(
                    f"Tidak bisa transisi dari '{transfer.status}' ke '{new_status}'. "
                    f"Transisi yang diizinkan dari status ini: {allowed_next_states}"
                ),
            )

        try:
            if new_status == TransferStatus.IN_TRANSIT:
                await self._deduct_stock_from_source(transfer)
            elif new_status == TransferStatus.COMPLETED:
                await self._add_stock_to_destination(transfer)
            elif new_status == TransferStatus.REJECTED:
                if not rejection_reason:
                    return TransferTransitionResult(
                        success=False,
                        error_code="REJECTION_REASON_REQUIRED",
                        error_message="Alasan penolakan wajib diisi",
                    )
                transfer.rejection_reason = rejection_reason

            transfer.status = new_status
            await self.db.flush()

            logger.info(
                f"Transfer {transfer.transfer_number} transitioned to {new_status}"
            )

            return TransferTransitionResult(success=True, transfer_order=transfer)

        except InsufficientStockError as exc:
            return TransferTransitionResult(
                success=False,
                error_code="INSUFFICIENT_SOURCE_STOCK",
                error_message=str(exc),
            )

    async def _deduct_stock_from_source(self, transfer: TransferOrder) -> None:
        stmt = (
            select(StockLevel)
            .where(
                StockLevel.warehouse_id == transfer.from_warehouse_id,
                StockLevel.sku_id == transfer.sku_id,
            )
            .with_for_update()
        )
        result = await self.db.execute(stmt)
        stock = result.scalar_one_or_none()

        if stock is None or stock.quantity < transfer.quantity:
            available = stock.quantity if stock else 0
            raise InsufficientStockError(
                f"Stock gudang asal tidak cukup. "
                f"Tersedia: {available}, Dibutuhkan: {transfer.quantity}"
            )

        stock.quantity -= transfer.quantity
        stock.version += 1
        await self.db.flush()

    async def _add_stock_to_destination(self, transfer: TransferOrder) -> None:
        stmt = (
            select(StockLevel)
            .where(
                StockLevel.warehouse_id == transfer.to_warehouse_id,
                StockLevel.sku_id == transfer.sku_id,
            )
            .with_for_update()
        )
        result = await self.db.execute(stmt)
        stock = result.scalar_one_or_none()

        if stock is None:
            stock = StockLevel(
                warehouse_id=transfer.to_warehouse_id,
                sku_id=transfer.sku_id,
                quantity=0,
                reserved_quantity=0,
                version=1,
            )
            self.db.add(stock)
            await self.db.flush()

        stock.quantity += transfer.quantity
        stock.version += 1
        await self.db.flush()