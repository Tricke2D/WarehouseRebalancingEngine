from alembic import op
import sqlalchemy as sa

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Table: warehouses
    op.create_table(
        "warehouses",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("code", sa.String(20), unique=True, nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("latitude", sa.Numeric(10, 7), nullable=False),
        sa.Column("longitude", sa.Numeric(10, 7), nullable=False),
        sa.Column("city", sa.String(100), nullable=False),
        sa.Column("is_active", sa.Boolean(), default=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_warehouses_code", "warehouses", ["code"])

    # 2. Table: skus
    op.create_table(
        "skus",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("code", sa.String(50), unique=True, nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("unit_price", sa.Numeric(12, 2), nullable=False),
        sa.Column("weight_kg", sa.Numeric(8, 3), default=0.0),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_skus_code", "skus", ["code"])

    # 3. Table: stock_levels
    op.create_table(
        "stock_levels",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("warehouse_id", sa.Integer(), sa.ForeignKey("warehouses.id"), nullable=False),
        sa.Column("sku_id", sa.Integer(), sa.ForeignKey("skus.id"), nullable=False),
        sa.Column("quantity", sa.Integer(), default=0, nullable=False),
        sa.Column("reserved_quantity", sa.Integer(), default=0, nullable=False),
        sa.Column("version", sa.Integer(), default=1, nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("warehouse_id", "sku_id", name="uq_stock_warehouse_sku"),
        sa.CheckConstraint("quantity >= 0", name="ck_stock_quantity_non_negative"),
        sa.CheckConstraint("reserved_quantity >= 0", name="ck_stock_reserved_non_negative"),
        sa.CheckConstraint("quantity >= reserved_quantity", name="ck_stock_available_non_negative"),
    )
    op.create_index("ix_stock_warehouse_id", "stock_levels", ["warehouse_id"])
    op.create_index("ix_stock_sku_id", "stock_levels", ["sku_id"])

    # 4. Table: orders
    op.create_table(
        "orders",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("order_number", sa.String(30), unique=True, nullable=False),
        sa.Column("customer_name", sa.String(200), nullable=False),
        sa.Column("customer_email", sa.String(200), nullable=False),
        sa.Column("delivery_latitude", sa.Numeric(10, 7), nullable=False),
        sa.Column("delivery_longitude", sa.Numeric(10, 7), nullable=False),
        sa.Column("status", sa.String(30), default="PENDING", nullable=False),
        sa.Column("rejection_reason", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_orders_number", "orders", ["order_number"])
    op.create_index("ix_orders_status", "orders", ["status"])

    # 5. Table: order_items
    op.create_table(
        "order_items",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("order_id", sa.Integer(), sa.ForeignKey("orders.id"), nullable=False),
        sa.Column("sku_id", sa.Integer(), sa.ForeignKey("skus.id"), nullable=False),
        sa.Column("allocated_warehouse_id", sa.Integer(), sa.ForeignKey("warehouses.id"), nullable=True),
        sa.Column("requested_quantity", sa.Integer(), nullable=False),
        sa.Column("allocated_quantity", sa.Integer(), default=0, nullable=False),
    )
    op.create_index("ix_order_items_order_id", "order_items", ["order_id"])

    # 6. Table: transfer_orders
    op.create_table(
        "transfer_orders",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("transfer_number", sa.String(30), unique=True, nullable=False),
        sa.Column("from_warehouse_id", sa.Integer(), sa.ForeignKey("warehouses.id"), nullable=False),
        sa.Column("to_warehouse_id", sa.Integer(), sa.ForeignKey("warehouses.id"), nullable=False),
        sa.Column("sku_id", sa.Integer(), sa.ForeignKey("skus.id"), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(20), default="SUGGESTED", nullable=False),
        sa.Column("rejection_reason", sa.Text(), nullable=True),
        sa.Column("suggestion_reason", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_transfer_orders_number", "transfer_orders", ["transfer_number"])
    op.create_index("ix_transfer_orders_status", "transfer_orders", ["status"])


def downgrade() -> None:
    op.drop_table("transfer_orders")
    op.drop_table("order_items")
    op.drop_table("orders")
    op.drop_table("stock_levels")
    op.drop_table("skus")
    op.drop_table("warehouses")