from nds.geometry.structural_geometry_engine import StructuralGeometryEngine


class GeometryEngine:
    """
    Geometry Facade — Phase‑8.2
    """

    def __init__(self):
        self._engine = StructuralGeometryEngine()

    def evaluate(self, *args, **kwargs):
        return self._engine.evaluate(*args, **kwargs)
