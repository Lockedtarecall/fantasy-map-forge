"""Biome enumeration and climate lookup table."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Biome(Enum):
    OCEAN = "ocean"
    BEACH = "beach"
    GRASSLAND = "grassland"
    TEMPERATE_FOREST = "temperate_forest"
    RAINFOREST = "rainforest"
    SAVANNA = "savanna"
    DESERT = "desert"
    TAIGA = "taiga"
    TUNDRA = "tundra"
    MOUNTAIN = "mountain"
    SNOW_PEAK = "snow_peak"
    SWAMP = "swamp"


@dataclass(frozen=True, slots=True)
class BiomeBand:
    biome: Biome
    temp_min: float
    temp_max: float
    moisture_min: float


# Whittaker-style bands, temperature in deg C annual mean, moisture 0..1.
BIOME_TABLE: tuple[BiomeBand, ...] = (
    BiomeBand(Biome.SNOW_PEAK, -60.0, -5.0, 0.0),
    BiomeBand(Biome.TUNDRA, -5.0, 2.0, 0.0),
    BiomeBand(Biome.TAIGA, 2.0, 8.0, 0.15),
    BiomeBand(Biome.TEMPERATE_FOREST, 8.0, 20.0, 0.35),
    BiomeBand(Biome.GRASSLAND, 8.0, 22.0, 0.15),
    BiomeBand(Biome.RAINFOREST, 20.0, 40.0, 0.6),
    BiomeBand(Biome.SAVANNA, 20.0, 34.0, 0.2),
    BiomeBand(Biome.DESERT, 22.0, 50.0, 0.0),
)


def classify(temperature_c: float, moisture: float, elevation_m: float) -> Biome:
    """Return the biome for a climate sample.

    `elevation_m` above 4200 m forces `SNOW_PEAK` regardless of latitude.
    """
    if elevation_m > 4200.0:
        return Biome.SNOW_PEAK
    best: BiomeBand | None = None
    for band in BIOME_TABLE:
        if band.temp_min <= temperature_c <= band.temp_max and moisture >= band.moisture_min:
            if best is None or band.moisture_min > best.moisture_min:
                best = band
    return best.biome if best else Biome.GRASSLAND