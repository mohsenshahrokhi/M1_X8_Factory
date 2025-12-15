import time
from collections import deque


class ExecutionMetrics:
    """
    Phase‑10B.1 Execution Metrics
    ----------------------------
    Tracks:
    - sent / filled / rejected
    - rolling reject ratio
    - rolling latency (ms)
    """

    def __init__(self, kill_switch, window_sec: int = 60):
        self.kill_switch = kill_switch
        self.window_sec = window_sec
        self.reset()

    def reset(self):
        self.sent = 0
        self.rejected = 0
        self.filled = 0

        self.events = deque()        # (timestamp, success)
        self.latencies = deque()     # (timestamp, latency_ms)

        self.triggered = False
        self.avg_latency_ms = 0.0

    # ============================
    # Events
    # ============================
    def on_send(self):
        self.sent += 1
        self.events.append((time.time(), True))

    def on_reject(self, reason: str):
        self.rejected += 1
        self.events.append((time.time(), False))

        if self.reject_ratio_window() > 0.50 and not self.triggered:
            self.triggered = True
            if self.kill_switch:
                self.kill_switch.trigger(
                    reason=f"Execution Reject Spike: {reason}"
                )

    def on_fill(self, latency_ms: float):
        self.filled += 1
        now = time.time()

        self.latencies.append((now, latency_ms))

        # purge old latency samples
        while self.latencies and now - self.latencies[0][0] > self.window_sec:
            self.latencies.popleft()

        if self.latencies:
            self.avg_latency_ms = (
                sum(l for _, l in self.latencies) / len(self.latencies)
            )

    # ============================
    # Metrics
    # ============================
    def reject_ratio_window(self) -> float:
        now = time.time()

        while self.events and now - self.events[0][0] > self.window_sec:
            self.events.popleft()

        total = len(self.events)
        if total == 0:
            return 0.0

        rejects = sum(1 for _, success in self.events if not success)
        return rejects / total
