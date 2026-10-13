"""GenerateHandler — orchestrates a full map build from a request."""

from __future__ import annotations

from pathlib import Path

from fantasy_map_forge.generators.ai_painter import AIPainter
from fantasy_map_forge.generators.base import GenerationRequest
from fantasy_map_forge.generators.procedural import ProceduralGenerator
from fantasy_map_forge.models.map_document import MapDocument
from fantasy_map_forge.services.export_service import ExportService
from fantasy_map_forge.services.model_runtime import ModelRuntime
from fantasy_map_forge.utils.logging import get_logger

log = get_logger(__name__)


class GenerateHandler:
    """Ties terrain generation, AI painting, and export into one call."""

    def __init__(self, runtime: ModelRuntime | None = None) -> None:
        self._procedural = ProceduralGenerator()
        self._runtime = runtime
        self._exporter = ExportService()

    def run(self, request: GenerationRequest, out_dir: Path) -> MapDocument:
        doc = self._procedural.generate(request)
        if request.use_ai and self._runtime is not None:
            painter = AIPainter(self._runtime)
            doc = painter.paint(doc, request)
        out_dir.mkdir(parents=True, exist_ok=True)
        self._exporter.write_png(doc, out_dir / f"{request.name}.png")
        log.info("map written to %s", out_dir / f"{request.name}.png")
        return doc