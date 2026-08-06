from datetime import datetime
from sqlalchemy import String, Numeric, Text, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base


class SKU(Base):
    __tablename__ = "skus"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    unit_price: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    weight_kg: Mapped[float] = mapped_column(Numeric(8, 3), default=0.0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    stock_levels: Mapped[list["StockLevel"]] = relationship(
        "StockLevel", back_populates="sku", lazy="noload"
    )

    def __repr__(self) -> str:
        return f"<SKU code={self.code} name={self.name}>"