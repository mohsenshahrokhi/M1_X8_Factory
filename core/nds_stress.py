import numpy as np

class NDSStressEngine:
    def __init__(
        self,
        alpha_k: float = 1.0,
        eps: float = 1e-8,
        clip_max: float = 5.0
    ):
        self.alpha_k = alpha_k
        self.eps = eps
        self.clip_max = clip_max

    def compute_pressure(self, cycle_htf: np.ndarray) -> float:
        """
        P_k(t) = α_k * dC_k(t)/dt
        """
        if len(cycle_htf) < 2:
            return 0.0

        slope = np.gradient(cycle_htf)[-1]
        return self.alpha_k * abs(slope)

    def compute_nodal_capacity(self, nodes_ltf: np.ndarray) -> float:
        """
        Σ |Δn(k+1)|
        """
        if len(nodes_ltf) < 2:
            return self.eps

        deltas = np.diff(nodes_ltf)
        return np.sum(np.abs(deltas)) + self.eps

    def stress(self, cycle_htf: np.ndarray, nodes_ltf: np.ndarray) -> float:
        pressure = self.compute_pressure(cycle_htf)
        capacity = self.compute_nodal_capacity(nodes_ltf)

        stress = pressure / capacity
        return float(np.clip(stress, 0.0, self.clip_max))
