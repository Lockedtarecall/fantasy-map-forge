# Security Policy — fantasy-map-forge

## Scope

This policy covers the desktop application, its Python packages, the
model-loading path, and the on-disk project format.

## Supported versions

| Version | Supported |
|---------|-----------|
| 0.7.x   | yes       |
| 0.6.x   | security fixes only |
| < 0.6   | no        |

## Reporting a vulnerability

Email `security@fantasy-map-forge.dev` with a description, repro steps,
and the affected version. Do not open a public issue for memory-safety or
model-deserialization bugs.

We aim to acknowledge within 72 hours.

## Known risk surfaces

- **Model deserialization.** `.onnx` and `.gguf` are loaded through
  `services/model_runtime.py`. Only load model files from sources you
  trust; the loader does not sandbox graph execution.
- **Plugin scripts.** `generators/plugins/` executes user Python in the
  same process. Treat third-party generators as untrusted code.
- **Project files.** `*.fmg` is a zipped bundle; the importer refuses
  paths that escape the extraction root (see `services/project_io.py`).

## Hardening checklist for releases

- [ ] Pin `onnxruntime` and `numpy` in the lockfile.
- [ ] Run `pip-audit` in CI.
- [ ] Verify the exporter has no shell-out on user filenames.