"""ModelRuntime — loads an ONNX diffusion model and renders tiles.

Only load model files you trust. The loader does not sandbox graph
execution; a malicious graph can read process memory.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np

from fantasy_map_forge.models.map_document import MapDocument, TileSpec
from fantasy_map_forge.utils.logging import get_logger

log = get_logger(__name__)


class ModelRuntime:
    """Wraps an ONNX session for tile rendering.

    `render_tile` writes an RGB float32 tile of shape
    `(tile.size, tile.size, 3)` into `doc`-attached storage. The session is
    created lazily on first render; failures raise `RuntimeError` with the
    underlying ONNX message.
    """

    def __init__(self, model_path: Path, guidance_scale: float = 7.5, steps: int = 28) -> None:
        self._model_path = Path(model_path)
        self._guidance = guidance_scale
        self._steps = steps
        self._session = None
        self._text_encoder = None

    def _ensure_session(self) -> None:
        if self._session is not None:
            return
        if not self._model_path.exists():
            raise RuntimeError(f"model not found: {self._model_path}")
        try:
            import onnxruntime as ort

            providers = ["CUDAExecutionProvider", "CPUExecutionProvider"]
            self._session = ort.InferenceSession(str(self._model_path), providers=providers)
        except Exception as exc:  # noqa: BLE001 — surface as RuntimeError
            raise RuntimeError(f"failed to load model {self._model_path}: {exc}") from exc
        log.info("model loaded: %s", self._model_path.name)

    def render_tile(self, doc: MapDocument, tile: TileSpec) -> np.ndarray:
        self._ensure_session()
        height = doc.elevation[
            tile.origin_y : tile.origin_y +