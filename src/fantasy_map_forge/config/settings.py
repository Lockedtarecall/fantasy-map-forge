"""Settings loader: merges default.yaml, user config, and env overrides."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

CONFIG_DIR = Path(__file__).resolve().parents[3] / "config"
DEFAULT_PATH = CONFIG_DIR / "default.yaml"


@dataclass(slots=True)
class TerrainSettings:
    width: int = 2048
    height: int = 2048
    seed: int = 0
    octaves: int = 7
    lacunarity: float = 2.0
    persistence: float = 0.5
    sea_level: float = 0.42
    erosion_iterations: int = 45000


@dataclass(slots=True)
class AISettings:
    backend: str = "onnx"
    model_path: str = "models/fantasy_biome_v2.onnx"
    tile_size: int = 512
    guidance_scale: float = 7.5
    steps: int = 28


@dataclass(slots=True)
class Settings:
    terrain: TerrainSettings = field(default_factory=TerrainSettings)
    ai: AISettings = field(default_factory=AISettings)
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Settings":
        return cls(
            terrain=TerrainSettings(**data.get("terrain", {})),
            ai=AISettings(**data.get("ai", {})),
            raw=data,
        )


def load_settings(user_path: Path | None = None) -> Settings:
    """Load settings, layering user config over defaults.

    *Env override `FMG_CONFIG` wins over `user_path`.*
    Raises `FileNotFoundError` if the default config is missing.
    """
    merged: dict[str, Any] = yaml.safe_load(DEFAULT_PATH.read_text(encoding="utf-8")) or {}

    env_path = os.environ.get("FMG_CONFIG")
    chosen = Path(env_path) if env_path else user_path
    if chosen and chosen.exists():
        override = yaml.safe_load(chosen.read_text(encoding="utf-8")) or {}
        merged = _deep_merge(merged, override)

    return Settings.from_dict(merged)


def _deep_merge(base: dict[str, Any], patch: dict[str, Any]) -> dict[str, Any]:
    out = dict(base)
    for key, value in patch.items():
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = _deep_merge(out[key], value)
        else:
            out[key] = value
    return out