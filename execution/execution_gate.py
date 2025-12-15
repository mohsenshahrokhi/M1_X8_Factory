# execution/execution_gate.py

import time
from execution.execution_registry import ExecutionRegistry
from execution.execution_metrics import ExecutionMetrics
from execution.feedback_controller import ExecutionFeedbackController


class ExecutionGate:
    """
    Phase‑10B.1 Execution Gate
    -------------------------
    Adaptive, feedback‑aware, intent‑safe
    """

    def __init__(self, adapter, kill_switch=None):
        self.adapter = adapter
        self.kill_switch = kill_switch

        self.registry = ExecutionRegistry()
        self.metrics = ExecutionMetrics(kill_switch=kill_switch)
        self.feedback = ExecutionFeedbackController(
            kill_switch=kill_switch
        )

        print("✅ [10B.1] ExecutionGate armed")

    def send(self, intent):

        # ============================
        # HARD KILL
        # ============================
        if self.kill_switch and self.kill_switch.is_triggered():
            return {"success": False, "reason": "KILL_SWITCH_ACTIVE"}

        # ============================
        # FEEDBACK PAUSE
        # ============================
        if not self.feedback.allow_send():
            return {
                "success": False,
                "reason": "EXECUTION_PAUSED_BY_FEEDBACK",
            }

        # ============================
        # DUPLICATE GUARD
        # ============================
        if self.registry.has_similar(intent):
            return {
                "success": False,
                "reason": "DUPLICATE_INTENT",
            }

        # ============================
        # ADAPTIVE SIZE (IMMUTABLE)
        # ============================
        adjusted_size = self.feedback.adjust_size(intent.size)

        exec_intent = type(intent)(
            symbol=intent.symbol,
            side=intent.side,
            size=adjusted_size,
            limit_price=intent.limit_price,
            stop_price=intent.stop_price,      # ✅ FIX
        )

        # ============================
        # ADAPTIVE THROTTLE
        # ============================
        throttle = getattr(self.feedback, "throttle", 1.0)
        if throttle < 1.0:
            time.sleep((1.0 - throttle) * 0.5)

        # ============================
        # REGISTER
        # ============================
        execution_id = self.registry.create(exec_intent)
        self.registry.mark_sent(execution_id)
        self.metrics.on_send()

        # ============================
        # EXECUTE
        # ============================
        t0 = time.time()
        result = self.adapter.execute(exec_intent)
        latency_ms = (time.time() - t0) * 1000

        # ============================
        # REJECT PATH
        # ============================
        if not result.get("success", False):
            self.registry.mark_rejected(
                execution_id,
                result.get("reason", "UNKNOWN"),
            )
            self.metrics.on_reject(
                result.get("reason", "UNKNOWN"),
            )
            self.feedback.evaluate(self.metrics)
            return result

        # ============================
        # FILL PATH
        # ============================
        self.registry.mark_filled(
            execution_id,
            order_id=result.get("order_id", -1),
            fill_price=result.get(
                "fill_price",
                exec_intent.limit_price,
            ),
        )

        self.metrics.on_fill(latency_ms)
        self.feedback.evaluate(self.metrics)

        return result
