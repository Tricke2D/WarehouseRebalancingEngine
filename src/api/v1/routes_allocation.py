from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db_session
from src.domain.schemas.allocation import AllocationRequestSchema, AllocationResponseSchema
from src.services.allocation_service import AllocationService, AllocationRequest

router = APIRouter(prefix="/v1/orders", tags=["order-allocation"])


@router.post(
    "/allocate",
    response_model=AllocationResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def allocate_order(
    payload: AllocationRequestSchema,
    db: AsyncSession = Depends(get_db_session),
) -> AllocationResponseSchema:
    service = AllocationService(db)
    
    request = AllocationRequest(
        sku_id=payload.sku_id,
        quantity=payload.quantity,
        delivery_latitude=payload.delivery_latitude,
        delivery_longitude=payload.delivery_longitude,
    )

    result = await service.allocate_order(request)

    if result.success:
        await db.commit()
        return AllocationResponseSchema(
            success=True,
            allocations=[
                {"warehouse_id": wh_id, "quantity": qty}
                for wh_id, qty in result.allocations
            ],
            is_split=result.is_split,
            message="Stock berhasil di-reserve",
        )
    else:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error_code": result.error_code,
                "message": result.error_message,
            },
        )