"""AI biome painting: tiled diffusion call wrapped around a terrain skeleton."""

from __future__ import annotations

import numpy as np

from fantasy_map_forge.generators.base import GenerationRequest
from fantasy_map_forge.models.map_document import MapDocument, TileSpec
from fantasy_map_forge.services.model_runtime import ModelRuntime
from fantasy_map_forge.utils.logging import get_logger

log = get_logger(__name__)


class AIPainter:
    """Paints biome/ink texture over a terrain document using a diffusion model.

    The painter tiles the map into `tile_size` squares and feeds the model
    the terrain height + a text prompt per tile. Overlap of `tile_size // 8`
    pixels is blended with a cosine ramp to hide seams.
    """

    def __init__(self, runtime: ModelRuntime, tile_size: int = 512) -> None:
        self._runtime = runtime
        self._tile_size = tile_size

    def paint(self, doc: MapDocument, request: GenerationRequest) -> MapDocument:
        if not request.use_ai:
            return doc
        overlap = self._tile_size // 8
        stride = self._tile_size - overlap
        tiles: list[TileSpec] = []
        for oy in range(0, doc.height, stride):
            for ox in range(0, doc.width, stride):
                tiles.append(
                    TileSpec(
                        origin_x=ox,
                        origin_y=oy,
                        size=self._tile_size,
                        prompt=request.prompt or "",
                        profile=request.profile,
                        seed=request.seed ^ (ox * 73856093) ^ (oy * 19349663),
                    )
                )
        log.info("painter queued %d tiles for %s", len(tiles), doc.name)
        doc.tiles = tiles
        for tile in tiles:
            self._runtime.render_tile(doc, tile)
        return doc

    @staticmethod
    def blend_seam(a: np.ndarray, b: np.ndarray, overlap: int) -> np.ndarray:
        """Cosine-blend two tile edges across `overlap` pixels."""
        ramp = 0.5 - 0.5 * np.cos(np.linspace(0, np.pi, overlap, dtype=np.float32))
        ramp = ramp[:, None, None] if a.ndim == 3 else ramp
        return a * (1.0 - ramp) + b * ramp