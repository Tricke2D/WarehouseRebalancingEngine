from datetime import datetime
from sqlalchemy import Integer, DateTime, ForeignKey, UniqueConstraint, func, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base


class StockLevel(Base):
    __tablename__ = "stock_levels"

    __table_args__ = (
        UniqueConstraint("warehouse_id", "sku_id", name="uq_stock_warehouse_sku"),
        CheckConstraint("quantity >= 0", name="ck_stock_quantity_non_negative"),
        CheckConstraint("reserved_quantity >= 0", name="ck_stock_reserved_non_negative"),
        CheckConstraint("quantity >= reserved_quantity", name="ck_stock_available_non_negative"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    warehouse_id: Mapped[int] = mapped_column(Integer, ForeignKey("warehouses.id"), nullable=False, index=True)
    sku_id: Mapped[int] = mapped_column(Integer, ForeignKey("skus.id"), nullable=False, index=True)
    quantity: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    reserved_quantity: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    warehouse: Mapped["Warehouse"] = relationship("Warehouse", back_populates="stock_levels")
    sku: Mapped["SKU"] = relationship("SKU", back_populates="stock_levels")

    @property
    def available_quantity(self) -> int:
        return self.quantity - self.reserved_quantity