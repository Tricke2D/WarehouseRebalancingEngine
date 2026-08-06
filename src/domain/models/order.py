from datetime import datetime
from sqlalchemy import Integer, String, Numeric, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base
from src.domain.enums import OrderStatus


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    order_number: Mapped[str] = mapped_column(
        String(30), unique=True, nullable=False, index=True
    )
    customer_name: Mapped[str] = mapped_column(String(200), nullable=False)
    customer_email: Mapped[str] = mapped_column(String(200), nullable=False)
    delivery_latitude: Mapped[float] = mapped_column(Numeric(10, 7), nullable=False)
    delivery_longitude: Mapped[float] = mapped_column(Numeric(10, 7), nullable=False)
    status: Mapped[str] = mapped_column(
        String(30),
        default=OrderStatus.PENDING,
        nullable=False,
        index=True
    )
    rejection_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    items: Mapped[list["OrderItem"]] = relationship(
        "OrderItem", back_populates="order", lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<Order number={self.order_number} status={self.status}>"


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("orders.id"), nullable=False, index=True
    )
    sku_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("skus.id"), nullable=False
    )
    allocated_warehouse_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("warehouses.id"), nullable=True
    )
    requested_quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    allocated_quantity: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    order: Mapped["Order"] = relationship("Order", back_populates="items")

    def __repr__(self) -> str:
        return (
            f"<OrderItem order_id={self.order_id} "
            f"sku_id={self.sku_id} qty={self.requested_quantity}>"
        )