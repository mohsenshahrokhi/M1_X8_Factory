import time
from collections import deque


class ExecutionMetrics:
    """
    Rolling execution quality metrics
    """

    def __init__(self, window: int = 50):
        self.window = window
        self.sends = deque(maxlen=window)
        self.fills = deque(maxlen=window)
        self.rejects = deque(maxlen=window)
        self.latencies = deque(maxlen=window)

    def on_send(self):
        self.sends.append(time.time())

    def on_fill(self, latency_sec: float):
        self.fills.append(time.time())
        self.latencies.append(latency_sec)

    def on_reject(self, reason: str):
        self.rejects.append((time.time(), reason))

    # --------------------------
    # Computed Metrics
    # --------------------------
    def reject_rate(self) -> float:
        total = len(self.sends)
        return len(self.rejects) / total if total > 0 else 0.0

    def avg_latency(self) -> float:
        if not self.latencies:
            return 0.0
        return sum(self.latencies) / len(self.latencies)
# metrics.py

class WarmUpMetrics:
    def __init__(self):
        self.iterations = 0
        self.accept_count = 0
        self.confidences = []

    def record(self, verdict):
        self.iterations += 1
        self.confidences.append(verdict.confidence)

        if verdict.accept:
            self.accept_count += 1

    def summary(self):
        if self.iterations == 0:
            return {}

        return {
            "iterations": self.iterations,
            "accept_ratio": round(self.accept_count / self.iterations, 4),
            "avg_confidence": round(
                sum(self.confidences) / len(self.confidences), 4
            ),
            "max_confidence": round(max(self.confidences), 4),
        }
