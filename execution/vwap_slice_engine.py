import time
from dataclasses import dataclass


@dataclass
class VWAPSliceConfig:
    slice_count: int = 3
    cooldown_sec: int = 2
    price_band_points: float = 5.0


class VWAPSliceEngine:
    """
    Phase‑7B – Clean VWAP Slice Execution Engine
    (No feedback, no metrics, no registry)
    """

    def __init__(
        self,
        vwap_provider,
        kill_switch,
        execution_gate,
        adapter,
    ):
        self.vwap_provider = vwap_provider
        self.kill_switch = kill_switch
        self.execution_gate = execution_gate
        self.adapter = adapter

    def execute(self, exec_plan, config: VWAPSliceConfig):

        if not self.kill_switch.can_trade():
            return

        remaining = exec_plan.size
        if remaining <= 0:
            return

        for _ in range(config.slice_count):

            if remaining <= 0 or not self.kill_switch.can_trade():
                break

            vwap = self.vwap_provider.get_vwap(exec_plan.symbol)
            if vwap is None:
                break

            slice_size = round(
                remaining / (config.slice_count),
                2
            )
            slice_size = min(slice_size, remaining)

            if slice_size <= 0:
                break

            price = self._slice_price(
                exec_plan.side,
                vwap,
                config.price_band_points
            )

            slice_plan = exec_plan.new_slice(
                size=slice_size,
                limit_price=price
            )

            if not self.execution_gate.approve(slice_plan):
                self.kill_switch.notify_execution_reject(
                    "ExecutionGate reject"
                )
                break

            result = self.adapter.send(
                slice_plan.to_execution_request()
            )

            if not result.success:
                self.kill_switch.notify_execution_reject(
                    result.reason
                )
                break

            if result.filled:
                remaining -= slice_size

            time.sleep(config.cooldown_sec)

    def _slice_price(self, side: str, vwap: float, band_pts: float) -> float:
        return vwap - band_pts if side == "BUY" else vwap + band_pts
