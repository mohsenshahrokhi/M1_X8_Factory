import time
import uuid
from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class ExecutionRecord:
    """
    Single execution attempt registry entry
    """
    execution_id: str
    symbol: str
    side: str
    size: float
    limit_price: float
    timestamp: float
    status: str = "CREATED"       # CREATED | SENT | FILLED | REJECTED
    order_id: Optional[int] = None
    reject_reason: Optional[str] = None
    fill_price: Optional[float] = None
    latency_ms: Optional[float] = None


class ExecutionRegistry:
    """
    Execution Registry
    Phase‑7C core + Phase‑10A intent deduplication

    Tracks all execution attempts with full lifecycle visibility
    """

    def __init__(self, max_records: int = 1000):
        self.max_records = max_records
        self._records: Dict[str, ExecutionRecord] = {}

    # --------------------------------------------------
    # Creation
    # --------------------------------------------------
    def create(self, exec_plan) -> str:
        execution_id = str(uuid.uuid4())

        record = ExecutionRecord(
            execution_id=execution_id,
            symbol=exec_plan.symbol,
            side=exec_plan.side,
            size=exec_plan.size,
            limit_price=exec_plan.limit_price,
            timestamp=time.time()
        )

        self._records[execution_id] = record
        self._trim_if_needed()
        return execution_id

    # --------------------------------------------------
    # Phase‑10A: Intent Deduplication
    # --------------------------------------------------
    def has_similar(self, intent) -> bool:
        """
        Prevent duplicate execution intents
        (same symbol / side / limit price, still active)
        """
        for record in self._records.values():
            if (
                record.symbol == intent.symbol
                and record.side == intent.side
                and abs(record.limit_price - intent.limit_price) < 1e-6
                and record.status in ("CREATED", "SENT")
            ):
                return True
        return False

    # --------------------------------------------------
    # State Transitions
    # --------------------------------------------------
    def mark_sent(self, execution_id: str):
        record = self._records.get(execution_id)
        if record:
            record.status = "SENT"

    def mark_filled(self, execution_id: str, order_id: int = None, fill_price: float = None):
        record = self._records.get(execution_id)
        if record:
            record.status = "FILLED"
            record.order_id = order_id
            record.fill_price = fill_price
            record.latency_ms = (time.time() - record.timestamp) * 1000

    def mark_rejected(self, execution_id: str, reason: str):
        record = self._records.get(execution_id)
        if record:
            record.status = "REJECTED"
            record.reject_reason = reason
            record.latency_ms = (time.time() - record.timestamp) * 1000

    # --------------------------------------------------
    # Query
    # --------------------------------------------------
    def get(self, execution_id: str) -> Optional[ExecutionRecord]:
        return self._records.get(execution_id)

    def all(self) -> Dict[str, ExecutionRecord]:
        return dict(self._records)

    def stats(self) -> dict:
        total = len(self._records)
        filled = sum(1 for r in self._records.values() if r.status == "FILLED")
        rejected = sum(1 for r in self._records.values() if r.status == "REJECTED")

        return {
            "total": total,
            "filled": filled,
            "rejected": rejected,
            "fill_ratio": filled / total if total > 0 else 0.0,
            "reject_ratio": rejected / total if total > 0 else 0.0,
        }

    # --------------------------------------------------
    # Internal
    # --------------------------------------------------
    def _trim_if_needed(self):
        if len(self._records) <= self.max_records:
            return

        # Remove oldest records first
        sorted_items = sorted(
            self._records.items(),
            key=lambda item: item[1].timestamp
        )

        overflow = len(self._records) - self.max_records
        for i in range(overflow):
            del self._records[sorted_items[i][0]]
