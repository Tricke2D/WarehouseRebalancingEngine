from datetime import datetime
from pydantic import BaseModel, Field


class TransferOrderResponseSchema(BaseModel):
    id: int
    transfer_number: str
    from_warehouse_id: int
    to_warehouse_id: int
    sku_id: int
    quantity: int
    status: str
    suggestion_reason: str | None = None
    rejection_reason: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TransferRejectRequestSchema(BaseModel):
    rejection_reason: str = Field(
        ..., 
        min_length=5, 
        max_length=500,
        description="Alasan penolakan transfer, wajib diisi"
    )