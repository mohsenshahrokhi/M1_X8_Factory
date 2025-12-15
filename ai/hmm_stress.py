# ai/hmm_stress.py

import numpy as np
from hmmlearn.hmm import GaussianHMM


class HMMStressDetector:
    """
    Hidden Markov Model for Market Stress Detection
    ------------------------------------------------
    - 0.0  → WARMUP / LOW STRESS
    - >0.0 → NORMALIZED STRESS SCORE
    """

    def __init__(self, n_states: int = 2, min_obs: int = 50):
        self.model = GaussianHMM(
            n_components=n_states,
            covariance_type="diag",
            n_iter=200,
            random_state=42,
        )
        self.min_obs = min_obs
        self._trained = False

    def detect(self, X: np.ndarray) -> float:
        """
        Parameters
        ----------
        X : np.ndarray
            Shape (n_samples, n_features)

        Returns
        -------
        float
            Stress score in [0.0, 1.0]
        """

        if X is None or len(X) < self.min_obs:
            return 0.0  # WARMUP

        # ---- Remove NaN / Inf (CRITICAL FIX) ----
        X = np.asarray(X, dtype=float)
        mask = np.isfinite(X).all(axis=1)
        X = X[mask]

        if len(X) < self.min_obs:
            return 0.0  # WARMUP after cleaning

        try:
            # ---- Fit only once (or periodically retrain later) ----
            if not self._trained:
                self.model.fit(X)
                self._trained = True

            # ---- Predict Regime ----
            states = self.model.predict(X)

            # Assume higher mean variance = stress regime
            covars = self.model.covars_.mean(axis=1)
            stress_state = int(np.argmax(covars))

            # Stress score = probability of stress state
            stress_score = float(np.mean(states == stress_state))

            return np.clip(stress_score, 0.0, 1.0)

        except Exception:
            # Hard safety — never crash Orchestrator
            return 0.0
