from datetime import datetime
from sqlalchemy import Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base
from src.domain.enums import TransferStatus


class TransferOrder(Base):
    __tablename__ = "transfer_orders"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    transfer_number: Mapped[str] = mapped_column(
        String(30), unique=True, nullable=False, index=True
    )
    from_warehouse_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("warehouses.id"), nullable=False, index=True
    )
    to_warehouse_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("warehouses.id"), nullable=False, index=True
    )
    sku_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("skus.id"), nullable=False
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(
        String(20),
        default=TransferStatus.SUGGESTED,
        nullable=False,
        index=True
    )
    rejection_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    suggestion_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    def __repr__(self) -> str:
        return (
            f"<TransferOrder number={self.transfer_number} "
            f"from={self.from_warehouse_id} to={self.to_warehouse_id} "
            f"status={self.status}>"
        )