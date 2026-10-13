"""Procedural-only generator: no model, pure terrain + hydrology + biome."""

from __future__ import annotations

import numpy as np

from fantasy_map_forge.core import hydrology, terrain
from fantasy_map_forge.generators.base import GenerationRequest
from fantasy_map_forge.models.biome import classify
from fantasy_map_forge.models.map_document import MapDocument
from fantasy_map_forge.utils.logging import get_logger
from fantasy_map_forge.utils.rng import seed_everything, spawn

log = get_logger(__name__)


class ProceduralGenerator:
    """Deterministic terrain generator with no AI dependency."""

    def generate(self, request: GenerationRequest) -> MapDocument:
        rng = seed_everything(request.seed)
        log.info("procedural generate name=%s seed=%d", request.name, request.seed)

        elevation = terrain.fractal_elevation(
            request.width, request.height, spawn(rng, 1)
        )
        elevation = terrain.thermal_erosion(elevation, iterations=6000)
        filled = hydrology.fill_depressions(elevation)
        hydrology.extract_rivers(filled)

        moisture = self._moisture_field(request.width, request.height, spawn(rng, 2))
        temperature = self._temperature_field(request.height, elevation)

        return MapDocument(
            name=request.name,
            seed=request.seed,
            width=request.width,
            height=request.height,
            elevation=elevation,
            moisture=moisture,
            temperature=temperature,
        )

    def preview(self, request: GenerationRequest, max_dim: int = 256) -> np.ndarray:
        doc = self.generate(request)
        step = max(1, doc.width // max_dim)
        elev = doc.elevation[::step, ::step]
        norm = (elev - elev.min()) / (elev.max() - elev.min() + 1e-9)
        gray = (norm * 255).astype(np.uint8)
        return np.stack([gray, gray, gray], axis=-1)

    @staticmethod
    def _moisture_field(width: int, height: int, rng: np.random.Generator) -> np.ndarray:
        raw = rng.random((height, width), dtype=np.float32)
        return (raw * 0.7 + 0.15).clip(0.0, 1.0)

    @staticmethod
    def _temperature_field(height: int, elevation: np.ndarray) -> np.ndarray:
        latitude = np.linspace(28.0, -28.0, height, dtype=np.float32)[:, None]
        lapse = elevation * (6.5 / 1000.0)
        return (latitude - lapse).astype(np.float32)

    @staticmethod
    def biome_map(doc: MapDocument) -> np.ndarray:
        out = np.empty(doc.shape(), dtype=object)
        for y in range(doc.height):
            for x in range(doc.width):
                out[y, x] = classify(
                    float(doc.temperature[y, x]),
                    float(doc.moisture[y, x]),
                    float(doc.elevation[y, x]),
                )
        return out