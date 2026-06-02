"""islands.py
─────────────
Island detection and automatic bridge generation.

An **island** is a connected component of *material* that does not touch the
sheet border — it is fully surrounded by cut-out, so on a real stencil it would
simply fall out (think of the middle of an "O" or "A").

A **bridge** is a thin sliver of material left across a cut to tie an island
back to the safe, border-connected body of the sheet.

Material uses 8-connectivity (a diagonal sliver still holds), matching how a
physical sheet behaves.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .mask import StencilMask

_MAT_STRUCT = np.ones((3, 3), int)  # 8-connectivity for material


@dataclass(slots=True)
class Island:
    """A fully-enclosed material component that would fall out unbridged."""

    id: int
    area: int                      # pixel count
    centroid: tuple[float, float]  # (x, y)
    bbox: tuple[int, int, int, int]  # (x0, y0, x1, y1)


def _label_material(mask: StencilMask):
    from scipy import ndimage
    return ndimage.label(mask.material, structure=_MAT_STRUCT)


def _border_labels(labels: np.ndarray) -> set[int]:
    edges = np.concatenate([
        labels[0, :], labels[-1, :], labels[:, 0], labels[:, -1],
    ])
    return set(int(v) for v in np.unique(edges) if v != 0)


def detect_islands(mask: StencilMask) -> list[Island]:
    """Return every enclosed material component (excludes the border body).

    Works inside each component's bounding box (``find_objects``) so the cost is
    O(total pixels), not O(components × image) — vital for dense halftones.
    """
    from scipy import ndimage

    labels, n = _label_material(mask)
    if n == 0:
        return []
    safe = _border_labels(labels)
    slices = ndimage.find_objects(labels)
    islands: list[Island] = []
    for label in range(1, n + 1):
        if label in safe:
            continue
        sl = slices[label - 1]
        if sl is None:
            continue
        y0, x0 = sl[0].start, sl[1].start
        ly, lx = np.nonzero(labels[sl] == label)
        islands.append(Island(
            id=label,
            area=int(lx.size),
            centroid=(float(lx.mean() + x0), float(ly.mean() + y0)),
            bbox=(int(lx.min() + x0), int(ly.min() + y0),
                  int(lx.max() + x0), int(ly.max() + y0)),
        ))
    return islands


def add_bridges(
    mask: StencilMask,
    *,
    width: float = 2.0,
    min_area: int = 1,
) -> tuple[StencilMask, int]:
    """Carve bridges connecting every enclosed island to the safe body.

    For each island, the shortest path to safe material is found via a Euclidean
    distance transform, and a straight band of material ``width`` px wide is laid
    down across the intervening cut.

    Returns ``(new_mask, n_bridges)``.  Islands smaller than ``min_area`` are
    skipped (handle those with minimum-feature removal instead).
    """
    from scipy import ndimage

    labels, n = _label_material(mask)
    if n == 0:
        return mask.copy(), 0
    safe = _border_labels(labels)
    if not safe:  # nothing border-connected to bridge to
        return mask.copy(), 0

    safe_mask = np.isin(labels, list(safe))
    # For every pixel, distance to nearest safe-material pixel + its coordinates.
    dist, (iy, ix) = ndimage.distance_transform_edt(~safe_mask, return_indices=True)

    slices = ndimage.find_objects(labels)
    out = mask.copy()
    bridges = 0
    for label in range(1, n + 1):
        if label in safe:
            continue
        sl = slices[label - 1]
        if sl is None:
            continue
        sub = labels[sl] == label                       # island within its bbox
        if int(sub.sum()) < min_area:
            continue
        # island pixel closest to the safe body (searched only inside the bbox)
        cand = np.where(sub, dist[sl], np.inf)
        ly, lx = np.unravel_index(int(np.argmin(cand)), cand.shape)
        ry, rx = ly + sl[0].start, lx + sl[1].start
        ty, tx = int(iy[ry, rx]), int(ix[ry, rx])       # nearest safe pixel
        _draw_band(out.cut, (rx, ry), (tx, ty), width)
        bridges += 1
    return out, bridges


def _draw_band(cut: np.ndarray, p0: tuple[int, int], p1: tuple[int, int], width: float) -> None:
    """Set a ``width``-px band between p0 and p1 to material (cut = False)."""
    h, w = cut.shape
    x0, y0 = p0
    x1, y1 = p1
    length = max(abs(x1 - x0), abs(y1 - y0), 1)
    r = max(0, int(round(width / 2.0)))
    for i in range(length + 1):
        t = i / length
        cx = int(round(x0 + (x1 - x0) * t))
        cy = int(round(y0 + (y1 - y0) * t))
        y_lo, y_hi = max(0, cy - r), min(h, cy + r + 1)
        x_lo, x_hi = max(0, cx - r), min(w, cx + r + 1)
        cut[y_lo:y_hi, x_lo:x_hi] = False
