"""sampling.py
─────────────
Shared helpers for pattern generators.

Patterns walk paths across a coverage plane, sample local ink coverage, and
emit vector primitives.  This module centralises the bits every generator needs:

* :func:`sample`        — bilinear coverage lookup at float coordinates.
* :func:`sample_cell`   — mean coverage over a square block.
* :func:`runs_to_polylines` — split a sampled path into stroked segments whose
                          width tracks coverage (the core of every line-based
                          screen: lines, circular, spiral, radial, …).
"""

from __future__ import annotations

import numpy as np

from ..geometry import Point, Polyline


def sample(plane: np.ndarray, x: float, y: float) -> float:
    """Bilinearly sample coverage at float ``(x, y)`` (clamped to bounds)."""
    h, w = plane.shape
    x = min(max(x, 0.0), w - 1.0)
    y = min(max(y, 0.0), h - 1.0)
    x0, y0 = int(x), int(y)
    x1, y1 = min(x0 + 1, w - 1), min(y0 + 1, h - 1)
    fx, fy = x - x0, y - y0
    top = plane[y0, x0] * (1 - fx) + plane[y0, x1] * fx
    bot = plane[y1, x0] * (1 - fx) + plane[y1, x1] * fx
    return float(top * (1 - fy) + bot * fy)


def sample_cell(plane: np.ndarray, cx: float, cy: float, cell: float) -> float:
    """Mean coverage over the ``cell``-sized block centred on (cx, cy)."""
    h, w = plane.shape
    half = cell / 2.0
    x0 = max(0, int(round(cx - half)))
    x1 = min(w, int(round(cx + half)))
    y0 = max(0, int(round(cy - half)))
    y1 = min(h, int(round(cy + half)))
    if x1 <= x0 or y1 <= y0:
        return 0.0
    return float(plane[y0:y1, x0:x1].mean())


def runs_to_polylines(
    points: list[Point],
    covs: list[float],
    *,
    max_width: float,
    min_coverage: float,
    closed: bool = False,
) -> list[Polyline]:
    """Split a sampled path into stroked runs.

    Consecutive points whose coverage is ``>= min_coverage`` form one run; the
    run is emitted as a :class:`Polyline` whose ``width`` is the mean coverage
    of the run scaled by ``max_width``.  Gaps (highlights) leave the path empty.
    """
    out: list[Polyline] = []
    run: list[Point] = []
    run_cov: list[float] = []

    def flush() -> None:
        if len(run) >= 2:
            width = (sum(run_cov) / len(run_cov)) * max_width
            if width > 0:
                out.append(Polyline(points=list(run), closed=closed, width=width))

    for p, c in zip(points, covs):
        if c >= min_coverage:
            run.append(p)
            run_cov.append(c)
        else:
            flush()
            run.clear()
            run_cov.clear()
    flush()
    return out
