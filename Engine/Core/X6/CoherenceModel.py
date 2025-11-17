# Engine/Core/X6/CoherenceModel.py

class CoherenceModel:
    def compute_coherence(self, aligned, total):
        if total == 0:
            return 0
        return aligned / total
