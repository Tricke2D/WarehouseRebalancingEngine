from pydantic import BaseModel, Field


class AllocationRequestSchema(BaseModel):
    sku_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0)
    delivery_latitude: float = Field(..., ge=-90, le=90)
    delivery_longitude: float = Field(..., ge=-180, le=180)

    model_config = {
        "json_schema_extra": {
            "example": {
                "sku_id": 1,
                "quantity": 5,
                "delivery_latitude": -6.2088,
                "delivery_longitude": 106.8456,
            }
        }
    }


class AllocationDetailSchema(BaseModel):
    warehouse_id: int
    quantity: int


class AllocationResponseSchema(BaseModel):
    success: bool
    allocations: list[AllocationDetailSchema]
    is_split: bool = False
    message: str