import time
import uuid
from execution.execution_registry import ExecutionRegistry


class MockExecutionAdapter:
    """
    Phase‑10A Mock Execution Adapter
    --------------------------------
    Dry‑Run adapter:
    - Does NOT send orders to MT5
    - Simulates latency and fills
    - Self‑contained (auto‑creates registry if not provided)
    """

    def __init__(self, registry: ExecutionRegistry = None, simulated_latency_ms: int = 5):
        self.registry = registry or ExecutionRegistry()
        self.simulated_latency_ms = simulated_latency_ms

    def execute(self, intent):
        """
        Execute an ExecutionIntent (DRY‑RUN)
        """
        start_ts = time.time()

        # Create execution record
        execution_id = self.registry.create(intent)
        self.registry.mark_sent(execution_id)

        # Simulate execution latency
        time.sleep(self.simulated_latency_ms / 1000.0)

        # Simulate fill
        fill_price = intent.limit_price
        order_id = int(uuid.uuid4().int % 1_000_000)

        self.registry.mark_filled(
            execution_id=execution_id,
            order_id=order_id,
            fill_price=fill_price
        )

        latency_ms = (time.time() - start_ts) * 1000.0

        return {
            "success": True,
            "execution_id": execution_id,
            "order_id": order_id,
            "fill_price": fill_price,
            "latency_ms": latency_ms,
            "dry_run": True,
        }