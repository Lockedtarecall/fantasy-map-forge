"""Generator protocol shared by procedural and AI backends."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import numpy as np

from fantasy_map_forge.models.map_document import MapDocument


@dataclass(slots=True)
class GenerationRequest:
    name: str
    seed: int
    width: int
    height: int
    profile: str = "parchment_classic"
    prompt: str | None = None
    use_ai: bool = True


class Generator(Protocol):
    def generate(self, request: GenerationRequest) -> MapDocument:
        """Produce a MapDocument. Must be deterministic for a given seed."""
        ...

    def preview(self, request: GenerationRequest, max_dim: int = 256) -> np.ndarray:
        """Return a downsampled RGB preview array of shape (h, w, 3) uint8."""
        ...