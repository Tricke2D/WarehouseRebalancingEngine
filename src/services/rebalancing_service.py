import logging
from dataclasses import dataclass
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.models.stock_level import StockLevel
from src.domain.models.transfer_order import TransferOrder
from src.domain.enums import TransferStatus
from src.services.demand_velocity_service import VelocityMetric

logger = logging.getLogger(__name__)

OVERSUPPLY_MULTIPLIER = 2.0
UNDERSUPPLY_MULTIPLIER = 0.5
MIN_TRANSFER_QUANTITY = 1


@dataclass
class ImbalanceCandidate:
    warehouse_id: int
    sku_id: int
    current_stock: int
    velocity: float
    avg_demand: float
    imbalance_type: str
    magnitude: int


@dataclass
class TransferSuggestion:
    from_warehouse_id: int
    to_warehouse_id: int
    sku_id: int
    quantity: int
    reason: str


class RebalancingService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def generate_transfer_suggestions(
        self,
        velocities: list[VelocityMetric],
    ) -> list[TransferOrder]:
        velocity_by_sku: dict[int, list[VelocityMetric]] = {}
        for v in velocities:
            velocity_by_sku.setdefault(v.sku_id, []).append(v)

        all_suggestions: list[TransferOrder] = []

        for sku_id, sku_velocities in velocity_by_sku.items():
            candidates = await self._detect_imbalance_for_sku(sku_id, sku_velocities)
            suggestions = self._pair_and_generate_suggestions(candidates)

            for suggestion in suggestions:
                transfer_order = await self._create_transfer_order(suggestion)
                all_suggestions.append(transfer_order)

        logger.info(f"Generated {len(all_suggestions)} transfer suggestions total")
        return all_suggestions

    async def _detect_imbalance_for_sku(
        self,
        sku_id: int,
        sku_velocities: list[VelocityMetric],
    ) -> list[ImbalanceCandidate]:
        stmt = select(StockLevel).where(StockLevel.sku_id == sku_id)
        result = await self.db.execute(stmt)
        stock_levels = result.scalars().all()

        if not stock_levels:
            return []

        velocity_map = {v.warehouse_id: v.velocity_per_day for v in sku_velocities}
        all_velocities = [velocity_map.get(sl.warehouse_id, 0.0) for sl in stock_levels]
        avg_demand = sum(all_velocities) / len(all_velocities) if all_velocities else 0.0

        if avg_demand == 0:
            return []

        candidates: list[ImbalanceCandidate] = []

        for stock in stock_levels:
            velocity = velocity_map.get(stock.warehouse_id, 0.0)
            available = stock.available_quantity

            oversupply_threshold = OVERSUPPLY_MULTIPLIER * avg_demand
            undersupply_threshold = UNDERSUPPLY_MULTIPLIER * avg_demand

            if available > oversupply_threshold:
                # ⭐ PERBAIKAN: pastikan excess minimal 1
                excess = int(available - oversupply_threshold)
                if excess < 1:
                    excess = 1
                candidates.append(
                    ImbalanceCandidate(
                        warehouse_id=stock.warehouse_id,
                        sku_id=sku_id,
                        current_stock=available,
                        velocity=velocity,
                        avg_demand=avg_demand,
                        imbalance_type="OVERSUPPLY",
                        magnitude=excess,
                    )
                )
            elif available < undersupply_threshold:
                # ⭐ PERBAIKAN: pastikan shortage minimal 1
                shortage = int(undersupply_threshold - available)
                if shortage < 1:
                    shortage = 1
                candidates.append(
                    ImbalanceCandidate(
                        warehouse_id=stock.warehouse_id,
                        sku_id=sku_id,
                        current_stock=available,
                        velocity=velocity,
                        avg_demand=avg_demand,
                        imbalance_type="UNDERSUPPLY",
                        magnitude=shortage,
                    )
                )

        return candidates

    def _pair_and_generate_suggestions(
        self,
        candidates: list[ImbalanceCandidate],
    ) -> list[TransferSuggestion]:
        oversupply_list = sorted(
            [c for c in candidates if c.imbalance_type == "OVERSUPPLY"],
            key=lambda c: c.magnitude,
            reverse=True,
        )
        undersupply_list = sorted(
            [c for c in candidates if c.imbalance_type == "UNDERSUPPLY"],
            key=lambda c: c.magnitude,
            reverse=True,
        )

        suggestions: list[TransferSuggestion] = []

        over_idx, under_idx = 0, 0
        while over_idx < len(oversupply_list) and under_idx < len(undersupply_list):
            over_candidate = oversupply_list[over_idx]
            under_candidate = undersupply_list[under_idx]

            # ⭐ PERBAIKAN: transfer_qty = MIN(excess, shortage)
            transfer_qty = min(over_candidate.magnitude, under_candidate.magnitude)

            # ⭐ PERBAIKAN: pastikan transfer_qty >= 1
            if transfer_qty >= MIN_TRANSFER_QUANTITY:
                suggestions.append(
                    TransferSuggestion(
                        from_warehouse_id=over_candidate.warehouse_id,
                        to_warehouse_id=under_candidate.warehouse_id,
                        sku_id=over_candidate.sku_id,
                        quantity=transfer_qty,
                        reason=(
                            f"Gudang {over_candidate.warehouse_id} oversupply "
                            f"(stock={over_candidate.current_stock}, "
                            f"avg_demand={over_candidate.avg_demand:.2f}/hari). "
                            f"Gudang {under_candidate.warehouse_id} undersupply "
                            f"(stock={under_candidate.current_stock}, "
                            f"avg_demand={under_candidate.avg_demand:.2f}/hari). "
                            f"Transfer {transfer_qty} unit untuk rebalance."
                        ),
                    )
                )

            # Update magnitude sisa setelah transfer
            over_candidate.magnitude -= transfer_qty
            under_candidate.magnitude -= transfer_qty

            # Pindah ke kandidat berikutnya jika magnitude sudah habis
            if over_candidate.magnitude <= 0:
                over_idx += 1
            if under_candidate.magnitude <= 0:
                under_idx += 1

        return suggestions

    async def _create_transfer_order(
        self,
        suggestion: TransferSuggestion,
    ) -> TransferOrder:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")
        transfer_number = f"TRF-{timestamp}"

        transfer_order = TransferOrder(
            transfer_number=transfer_number,
            from_warehouse_id=suggestion.from_warehouse_id,
            to_warehouse_id=suggestion.to_warehouse_id,
            sku_id=suggestion.sku_id,
            quantity=suggestion.quantity,
            status=TransferStatus.SUGGESTED,
            suggestion_reason=suggestion.reason,
        )

        self.db.add(transfer_order)
        await self.db.flush()

        logger.info(
            f"Transfer suggestion created: {transfer_number} "
            f"from={suggestion.from_warehouse_id} to={suggestion.to_warehouse_id} "
            f"sku={suggestion.sku_id} qty={suggestion.quantity}"
        )
        return transfer_order