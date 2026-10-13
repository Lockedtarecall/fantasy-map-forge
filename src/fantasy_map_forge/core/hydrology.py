"""River and lake extraction from an elevation field."""

from __future__ import annotations

import numpy as np
from scipy import ndimage  # *scipy*: `label` on a 2048^2 bool mask is ~40 ms


def fill_depressions(elevation: np.ndarray) -> np.ndarray:
    """Priority-flood fill so every non-boundary cell drains downhill."""
    filled = elevation.astype(np.float32, copy=True)
    height, width = filled.shape
    border = np.zeros_like(filled, dtype=bool)
    border[0, :] = border[-1, :] = border[:, 0] = border[:, -1] = True
    queue = np.argwhere(border)
    visited = border.copy()
    while queue.size:
        y, x = queue[0]
        queue = queue[1:]
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < height and 0 <= nx < width and not visited[ny, nx]:
                filled[ny, nx] = max(filled[ny, nx], filled[y, x])
                visited[ny, nx] = True
                queue = np.vstack([queue, [ny, nx]])
    return filled


def extract_rivers(
    filled: np.ndarray, min_length: int = 24, flow_threshold: float = 0.012
) -> list[list[tuple[int, int]]]:
    """Trace rivers as lists of (y, x) pixel chains.

    Cells with flow accumulation above `flow_threshold` (fraction of map)
    and chains longer than `min_length` cells are kept. Returns a list of
    polylines in pixel space, longest first.
    """
    height, width = filled.shape
    flow = np.ones_like(filled, dtype=np.float32)
    order = np.argsort(filled, axis=None)[::-1]
    ys, xs = np.unravel_index(order, (height, width))
    for y, x in zip(ys, xs):
        best, best_h = None, filled[y, x]
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < height and 0 <= nx < width and filled[ny, nx] < best_h:
                best, best_h = (ny, nx), filled[ny, nx]
        if best is not None:
            flow[best] += flow[y, x]

    mask = flow > flow_threshold * flow.max()
    labels, count = ndimage.label(mask, structure=np.ones((3, 3)))
    rivers: list[list[tuple[int, int]]] = []
    for label_id in range(1, count + 1):
        ys2, xs2 = np.where(labels == label_id)
        if ys2.size >= min_length:
            rivers.append(list(zip(ys2.tolist(), xs2.tolist())))
    rivers.sort(key=len, reverse=True)
    return rivers