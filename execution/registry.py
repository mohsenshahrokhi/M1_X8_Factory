import time
from dataclasses import dataclass, field
from collections import deque


@dataclass
class ExecutionRecord:
    execution_id: int
    symbol: str
    side: str
    size: float
    price: float
    created_at: float = field(default_factory=time.time)
    sent_at: float = None
    filled_at: float = None
    rejected_at: float = None
    status: str = "CREATED"
    reject_reason: str = None


class ExecutionRegistry:
    """
    Central execution audit log (Phase‑7C)
    """

    def __init__(self, max_records: int = 500):
        self._records = deque(maxlen=max_records)
        self._next_id = 1

    def create(self, plan) -> int:
        record = ExecutionRecord(
            execution_id=self._next_id,
            symbol=plan.symbol,
            side=plan.side,
            size=plan.size,
            price=plan.limit_price
        )
        self._records.append(record)
        self._next_id += 1
        return record.execution_id

    def mark_sent(self, execution_id: int):
        self._get(execution_id).sent_at = time.time()
        self._get(execution_id).status = "SENT"

    def mark_filled(self, execution_id: int):
        rec = self._get(execution_id)
        rec.filled_at = time.time()
        rec.status = "FILLED"

    def mark_rejected(self, execution_id: int, reason: str):
        rec = self._get(execution_id)
        rec.rejected_at = time.time()
        rec.status = "REJECTED"
        rec.reject_reason = reason

    def recent(self):
        return list(self._records)

    def _get(self, execution_id: int) -> ExecutionRecord:
        for r in self._records:
            if r.execution_id == execution_id:
                return r
        raise KeyError(f"Execution ID {execution_id} not found")
