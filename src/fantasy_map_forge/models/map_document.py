"""MapDocument — the serializable unit the editor and exporter share."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import numpy as np


@dataclass(slots=True)
class TileSpec:
    origin_x: int
    origin_y: int
    size: int
    prompt: str
    profile: str
    seed: int


@dataclass(slots=True)
class MapDocument:
    name: str
    seed: int
    width: int
    height: int
    elevation: np.ndarray          # float32, shape (height, width), meters
    moisture: np.ndarray           # float32, 0..1
    temperature: np.ndarray        # float32, deg C
    tiles: list[TileSpec] = field(default_factory=list)
    source_path: Path | None = None

    def shape(self) -> tuple[int, int]:
        return (self.height, self.width)

    def sea_mask(self, sea_level_m: float) -> np.ndarray:
        """Boolean mask, True where a cell is below sea level."""
        return self.elevation < sea_level_m