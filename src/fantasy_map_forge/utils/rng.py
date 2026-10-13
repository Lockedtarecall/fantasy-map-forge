"""Deterministic RNG plumbing.

Every generator path must be reproducible from its seed, so all randomness
flows through `seed_everything` and `spawn`.
"""

from __future__ import annotations

import random

import numpy as np


def seed_everything(seed: int) -> np.random.Generator:
    """Seed Python's `random` and return a dedicated numpy Generator.

    Python's global `random` is seeded for third-party libs that use it;
    the returned Generator is the preferred source for all new code.
    """
    random.seed(seed)
    return np.random.default_rng(seed)


def spawn(parent: np.random.Generator, salt: int) -> np.random.Generator:
    """Derive a child Generator so sub-systems don't share a stream.

    `salt` is hashed into the parent's next integer; identical `(parent, salt)`
    pairs always yield identical children.
    """
    derived = int(parent.integers(0, 2**63 - 1)) ^ (salt * 0x9E3779B97F4A7C15)
    return np.random.default_rng(derived & 0x7FFFFFFFFFFFFFFF)