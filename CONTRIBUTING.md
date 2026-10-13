# Contributing to fantasy-map-forge

Thanks for wanting to help build the AI fantasy map generator. This repo is
the desktop toolchain: procedural terrain synthesis, diffusion-assisted
biome painting, vector export, and a Qt shell.

## Ground rules

- Python 3.11+. Type hints required on all public functions.
- `ruff` for lint/format, `mypy --strict` on `src/fantasy_map_forge/core`.
- Deterministic output: any generator path must be reproducible from its seed.
- No new runtime dependency without a note in `docs/dependencies.md`.

## Layout

```
src/fantasy_map_forge/
  core/        terrain, hydrology, biome kernels (pure, testable)
  generators/  AI + procedural map producers
  handlers/    request/command handlers (CLI + IPC)
  services/    model runtime, export, cache, project state
  models/      typed dataclasses & schema
  utils/       noise, geometry, rng, logging
  config/      settings loader + defaults
cmd/           entry points (gui, cli, worker)
tests/         pytest suite
docs/          architecture + format notes
```

## Workflow

1. Fork, branch off `main`: `feat/<area>-<short>`.
2. `pip install -e ".[dev]"` then `pre-commit install`.
3. `pytest -q` and `ruff check .` must pass.
4. Open a PR describing the seed you tested and the map it produced.

## Reporting map regressions

Attach the project file (`*.fmg`) and the seed. A map that can't be
reproduced from its seed is a bug, not a taste difference.