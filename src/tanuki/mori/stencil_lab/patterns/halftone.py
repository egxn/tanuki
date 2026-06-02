"""halftone.py
─────────────
Traditional halftone screens.

* :func:`halftone_dots`     — amplitude-modulated dot screen (area ∝ coverage).
* :func:`halftone_lines`    — variable-width parallel lines.
* :func:`halftone_circular` — concentric rings of variable-width arcs.
* :func:`crosshatch`        — layered line sets that build up with darkness.

Screen angles matter for colour work: rotating each CMYK plate to a different
angle (15° / 75° / 0° / 45°) avoids moiré.  All generators take a coverage
plane ``(H, W)`` in [0, 1] and return primitives in image pixel coordinates.
"""

from __future__ import annotations

import math

import numpy as np

from ..geometry import Dot, Polyline
from .sampling import runs_to_polylines, sample, sample_cell


def halftone_dots(
    plane: np.ndarray,
    *,
    cell: float = 8.0,
    angle: float = 0.0,
    scale: float = 1.0,
    min_coverage: float = 0.02,
) -> list[Dot]:
    """Dot screen: each grid cell becomes a dot with area ∝ local coverage.

    ``scale`` 1.0 → dots just touch at full coverage; ~1.41 → fully solid.
    """
    if plane.ndim != 2:
        raise ValueError("halftone_dots expects a 2-D coverage plane")
    if cell <= 0:
        raise ValueError("cell must be > 0")

    h, w = plane.shape
    max_radius = (cell / 2.0) * scale
    theta = math.radians(angle)
    cos_t, sin_t = math.cos(theta), math.sin(theta)
    cx0, cy0 = w / 2.0, h / 2.0
    diag = math.hypot(w, h)
    n = int(math.ceil(diag / cell / 2.0)) + 1

    dots: list[Dot] = []
    for j in range(-n, n + 1):
        for i in range(-n, n + 1):
            u, v = i * cell, j * cell
            x = cx0 + u * cos_t - v * sin_t
            y = cy0 + u * sin_t + v * cos_t
            if not (0 <= x < w and 0 <= y < h):
                continue
            cov = sample_cell(plane, x, y, cell)
            if cov < min_coverage:
                continue
            r = max_radius * math.sqrt(min(cov, 1.0))
            if r > 0:
                dots.append(Dot(x=x, y=y, r=r))
    return dots


def halftone_lines(
    plane: np.ndarray,
    *,
    spacing: float = 8.0,
    angle: float = 45.0,
    step: float = 2.0,
    min_coverage: float = 0.05,
    max_width: float | None = None,
) -> list[Polyline]:
    """Parallel lines whose stroke width tracks local coverage."""
    if plane.ndim != 2:
        raise ValueError("halftone_lines expects a 2-D coverage plane")
    h, w = plane.shape
    max_width = spacing if max_width is None else max_width
    theta = math.radians(angle)
    d = (math.cos(theta), math.sin(theta))       # along the line
    nrm = (-math.sin(theta), math.cos(theta))    # across lines
    cx0, cy0 = w / 2.0, h / 2.0
    half = math.hypot(w, h) / 2.0
    n_lines = int(math.ceil(half / spacing)) + 1
    n_steps = int(math.ceil((2 * half) / step)) + 1

    out: list[Polyline] = []
    for k in range(-n_lines, n_lines + 1):
        s = k * spacing
        ox, oy = cx0 + s * nrm[0], cy0 + s * nrm[1]
        pts, covs = [], []
        for m in range(n_steps + 1):
            t = -half + m * step
            x, y = ox + t * d[0], oy + t * d[1]
            if 0 <= x < w and 0 <= y < h:
                pts.append((x, y))
                covs.append(sample(plane, x, y))
        out.extend(runs_to_polylines(pts, covs, max_width=max_width,
                                     min_coverage=min_coverage))
    return out


def halftone_circular(
    plane: np.ndarray,
    *,
    spacing: float = 8.0,
    center: tuple[float, float] | None = None,
    step_deg: float = 4.0,
    min_coverage: float = 0.05,
    max_width: float | None = None,
) -> list[Polyline]:
    """Concentric rings of variable-width arcs centred on the image (or ``center``)."""
    if plane.ndim != 2:
        raise ValueError("halftone_circular expects a 2-D coverage plane")
    h, w = plane.shape
    max_width = spacing if max_width is None else max_width
    cx, cy = center if center else (w / 2.0, h / 2.0)
    max_r = math.hypot(max(cx, w - cx), max(cy, h - cy))
    n_rings = int(math.ceil(max_r / spacing))

    out: list[Polyline] = []
    for ring in range(1, n_rings + 1):
        r = ring * spacing
        n_ang = max(8, int(math.ceil(360.0 / step_deg)))
        pts, covs = [], []
        for a in range(n_ang + 1):
            ang = math.radians(a * 360.0 / n_ang)
            x, y = cx + r * math.cos(ang), cy + r * math.sin(ang)
            if 0 <= x < w and 0 <= y < h:
                pts.append((x, y))
                covs.append(sample(plane, x, y))
            else:
                pts.append(None)  # marks a break; flushed below
                covs.append(-1.0)
        # split on out-of-bounds breaks, then emit runs per contiguous segment
        seg_pts, seg_covs = [], []
        for p, c in zip(pts, covs):
            if p is None:
                out.extend(runs_to_polylines(seg_pts, seg_covs, max_width=max_width,
                                             min_coverage=min_coverage))
                seg_pts, seg_covs = [], []
            else:
                seg_pts.append(p)
                seg_covs.append(c)
        out.extend(runs_to_polylines(seg_pts, seg_covs, max_width=max_width,
                                     min_coverage=min_coverage))
    return out


# Crosshatch build-up: (coverage threshold, line angle) per pass, light → dark.
_CROSSHATCH_PASSES = ((0.15, 45.0), (0.35, -45.0), (0.55, 0.0), (0.75, 90.0))


def crosshatch(
    plane: np.ndarray,
    *,
    spacing: float = 6.0,
    step: float = 2.0,
    line_width: float | None = None,
    passes: tuple[tuple[float, float], ...] = _CROSSHATCH_PASSES,
) -> list[Polyline]:
    """Layered hatching: each darker pass adds a new set of fixed-width lines.

    Light areas get a single direction; progressively darker areas accumulate
    additional angled line sets, the way an engraver builds up tone.
    """
    if plane.ndim != 2:
        raise ValueError("crosshatch expects a 2-D coverage plane")
    width = (spacing * 0.18) if line_width is None else line_width
    out: list[Polyline] = []
    for threshold, angle in passes:
        # A line is drawn where coverage clears this pass's threshold.
        lines = halftone_lines(plane, spacing=spacing, angle=angle, step=step,
                               min_coverage=threshold, max_width=width * 2)
        # Normalise to fixed thin width (coverage already gated by threshold).
        for ln in lines:
            ln.width = width
        out.extend(lines)
    return out
