import logging
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db_session
from src.domain.models.transfer_order import TransferOrder
from src.domain.enums import TransferStatus
from src.domain.schemas.transfer import TransferOrderResponseSchema, TransferRejectRequestSchema
from src.services.transfer_service import TransferService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/v1/transfers", tags=["transfer-orders"])


@router.get("", response_model=list[TransferOrderResponseSchema])
async def list_transfers(
    status_filter: str | None = Query(None, alias="status"),
    warehouse_id: int | None = Query(None),
    db: AsyncSession = Depends(get_db_session),
) -> list[TransferOrderResponseSchema]:
    stmt = select(TransferOrder)

    if status_filter:
        stmt = stmt.where(TransferOrder.status == status_filter)
    if warehouse_id:
        stmt = stmt.where(
            (TransferOrder.from_warehouse_id == warehouse_id)
            | (TransferOrder.to_warehouse_id == warehouse_id)
        )

    stmt = stmt.order_by(TransferOrder.created_at.desc())
    result = await db.execute(stmt)
    transfers = result.scalars().all()

    return [TransferOrderResponseSchema.model_validate(t) for t in transfers]


@router.get("/{transfer_id}", response_model=TransferOrderResponseSchema)
async def get_transfer_detail(
    transfer_id: int,
    db: AsyncSession = Depends(get_db_session),
) -> TransferOrderResponseSchema:
    stmt = select(TransferOrder).where(TransferOrder.id == transfer_id)
    result = await db.execute(stmt)
    transfer = result.scalar_one_or_none()

    if transfer is None:
        raise HTTPException(status_code=404, detail="Transfer order tidak ditemukan")

    return TransferOrderResponseSchema.model_validate(transfer)


@router.patch("/{transfer_id}/approve", response_model=TransferOrderResponseSchema)
async def approve_transfer(
    transfer_id: int,
    db: AsyncSession = Depends(get_db_session),
) -> TransferOrderResponseSchema:
    service = TransferService(db)
    result = await service.transition_status(transfer_id, TransferStatus.APPROVED)

    if not result.success:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"error_code": result.error_code, "message": result.error_message},
        )

    await db.commit()
    
    # ⭐ Refresh object setelah commit agar atribut terisi
    await db.refresh(result.transfer_order)
    
    return TransferOrderResponseSchema.model_validate(result.transfer_order)


@router.patch("/{transfer_id}/reject", response_model=TransferOrderResponseSchema)
async def reject_transfer(
    transfer_id: int,
    payload: TransferRejectRequestSchema,
    db: AsyncSession = Depends(get_db_session),
) -> TransferOrderResponseSchema:
    service = TransferService(db)
    result = await service.transition_status(
        transfer_id,
        TransferStatus.REJECTED,
        rejection_reason=payload.rejection_reason,
    )

    if not result.success:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"error_code": result.error_code, "message": result.error_message},
        )

    await db.commit()
    
    # ⭐ Refresh object setelah commit agar atribut terisi
    await db.refresh(result.transfer_order)
    
    return TransferOrderResponseSchema.model_validate(result.transfer_order)


@router.patch("/{transfer_id}/ship", response_model=TransferOrderResponseSchema)
async def ship_transfer(
    transfer_id: int,
    db: AsyncSession = Depends(get_db_session),
) -> TransferOrderResponseSchema:
    service = TransferService(db)
    result = await service.transition_status(transfer_id, TransferStatus.IN_TRANSIT)

    if not result.success:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"error_code": result.error_code, "message": result.error_message},
        )

    await db.commit()
    
    # ⭐ Refresh object setelah commit agar atribut terisi
    await db.refresh(result.transfer_order)
    
    return TransferOrderResponseSchema.model_validate(result.transfer_order)


@router.patch("/{transfer_id}/receive", response_model=TransferOrderResponseSchema)
async def receive_transfer(
    transfer_id: int,
    db: AsyncSession = Depends(get_db_session),
) -> TransferOrderResponseSchema:
    service = TransferService(db)
    result = await service.transition_status(transfer_id, TransferStatus.COMPLETED)

    if not result.success:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"error_code": result.error_code, "message": result.error_message},
        )

    await db.commit()
    
    # ⭐ Refresh object setelah commit agar atribut terisi
    await db.refresh(result.transfer_order)
    
    return TransferOrderResponseSchema.model_validate(result.transfer_order)