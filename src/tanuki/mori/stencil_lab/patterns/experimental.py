"""experimental.py
──────────────────
Non-traditional pattern generators — the "visual languages" the project is
really about: render an image as waves, cells, contours or stippling instead of
plain dots.

* :func:`sine_wave`   — rows of sine waves; amplitude tracks coverage.
* :func:`zigzag`      — triangle-wave variant of the above.
* :func:`spiral`      — one Archimedean spiral, stroke width tracks coverage.
* :func:`radial`      — rays from a centre, width tracks coverage.
* :func:`hexagons`    — hex-grid halftone; cell size ∝ coverage (filled).
* :func:`honeycomb`   — hex outlines wherever coverage clears a threshold.
* :func:`topographic` — iso-coverage contour lines (marching squares).
* :func:`stipple`     — random dots with density ∝ coverage (organic/noise).
* :func:`voronoi`     — Voronoi cell web; cell density ∝ coverage.
* :func:`splotches`   — irregular ink blobs sized by coverage (shadow/spray, B&W).
* :func:`threshold_lines` — threshold cut broken by a line carrier so it always
  self-bridges (one part cut, one part held).
* :func:`line_screen` — continuous amplitude-modulated line ribbons; the
  street-art "line stencil" portrait look (thin in highlights, merging in
  shadows).

All take a coverage plane ``(H, W)`` in [0, 1] and return primitives in image
pixel coordinates.
"""

from __future__ import annotations

import math

import numpy as np

from ..geometry import Dot, Polyline, polygon
from .sampling import runs_to_polylines, sample, sample_cell


def _require_2d(plane: np.ndarray, who: str) -> None:
    if plane.ndim != 2:
        raise ValueError(f"{who} expects a 2-D coverage plane")


# ─── Waves ──────────────────────────────────────────────────────────────────

def sine_wave(
    plane: np.ndarray,
    *,
    spacing: float = 10.0,
    wavelength: float | None = None,
    amplitude: float | None = None,
    step: float = 2.0,
    width: float = 1.0,
) -> list[Polyline]:
    """Horizontal rows of sine waves whose amplitude follows local coverage."""
    _require_2d(plane, "sine_wave")
    h, w = plane.shape
    wavelength = (spacing * 2.0) if wavelength is None else wavelength
    amplitude = (spacing * 0.5) if amplitude is None else amplitude
    out: list[Polyline] = []
    y = spacing
    while y < h:
        pts = []
        x = 0.0
        while x < w:
            cov = sample(plane, x, y)
            yy = y + amplitude * cov * math.sin(2 * math.pi * x / wavelength)
            pts.append((x, yy))
            x += step
        if len(pts) >= 2:
            out.append(Polyline(points=pts, width=width))
        y += spacing
    return out


def zigzag(
    plane: np.ndarray,
    *,
    spacing: float = 10.0,
    wavelength: float | None = None,
    amplitude: float | None = None,
    step: float = 2.0,
    width: float = 1.0,
) -> list[Polyline]:
    """Like :func:`sine_wave` but with a triangle wave."""
    _require_2d(plane, "zigzag")
    h, w = plane.shape
    wavelength = (spacing * 2.0) if wavelength is None else wavelength
    amplitude = (spacing * 0.5) if amplitude is None else amplitude

    def tri(t: float) -> float:  # triangle wave in [-1, 1], period 1
        return 2.0 * abs(2.0 * (t - math.floor(t + 0.5))) - 1.0

    out: list[Polyline] = []
    y = spacing
    while y < h:
        pts = []
        x = 0.0
        while x < w:
            cov = sample(plane, x, y)
            yy = y + amplitude * cov * tri(x / wavelength)
            pts.append((x, yy))
            x += step
        if len(pts) >= 2:
            out.append(Polyline(points=pts, width=width))
        y += spacing
    return out


# ─── Spiral & radial ───────────────────────────────────────────────────────

def spiral(
    plane: np.ndarray,
    *,
    spacing: float = 8.0,
    center: tuple[float, float] | None = None,
    step_deg: float = 6.0,
    min_coverage: float = 0.05,
    max_width: float | None = None,
) -> list[Polyline]:
    """A single Archimedean spiral whose stroke width tracks coverage."""
    _require_2d(plane, "spiral")
    h, w = plane.shape
    cx, cy = center if center else (w / 2.0, h / 2.0)
    max_width = spacing if max_width is None else max_width
    b = spacing / (2 * math.pi)                      # radius gain per radian
    max_r = math.hypot(max(cx, w - cx), max(cy, h - cy))
    theta = 0.0
    dtheta = math.radians(step_deg)
    pts, covs = [], []
    while b * theta <= max_r:
        r = b * theta
        x, y = cx + r * math.cos(theta), cy + r * math.sin(theta)
        if 0 <= x < w and 0 <= y < h:
            pts.append((x, y))
            covs.append(sample(plane, x, y))
        else:
            pts.append(None)
            covs.append(-1.0)
        theta += dtheta
    # split on out-of-bounds, emit coverage-weighted runs
    out: list[Polyline] = []
    seg_p, seg_c = [], []
    for p, c in zip(pts, covs):
        if p is None:
            out.extend(runs_to_polylines(seg_p, seg_c, max_width=max_width,
                                         min_coverage=min_coverage))
            seg_p, seg_c = [], []
        else:
            seg_p.append(p)
            seg_c.append(c)
    out.extend(runs_to_polylines(seg_p, seg_c, max_width=max_width,
                                 min_coverage=min_coverage))
    return out


def radial(
    plane: np.ndarray,
    *,
    spacing: float = 8.0,
    center: tuple[float, float] | None = None,
    step: float = 2.0,
    min_coverage: float = 0.05,
    max_width: float | None = None,
) -> list[Polyline]:
    """Rays emanating from a centre, stroke width tracking coverage."""
    _require_2d(plane, "radial")
    h, w = plane.shape
    cx, cy = center if center else (w / 2.0, h / 2.0)
    max_width = spacing if max_width is None else max_width
    max_r = math.hypot(max(cx, w - cx), max(cy, h - cy))
    mid_r = max_r / 2.0
    n_rays = max(8, int(math.ceil(2 * math.pi * mid_r / spacing)))
    out: list[Polyline] = []
    for k in range(n_rays):
        ang = 2 * math.pi * k / n_rays
        dx, dy = math.cos(ang), math.sin(ang)
        pts, covs = [], []
        r = 0.0
        while r <= max_r:
            x, y = cx + r * dx, cy + r * dy
            if 0 <= x < w and 0 <= y < h:
                pts.append((x, y))
                covs.append(sample(plane, x, y))
            r += step
        out.extend(runs_to_polylines(pts, covs, max_width=max_width,
                                     min_coverage=min_coverage))
    return out


# ─── Hex cells ────────────────────────────────────────────────────────────────

def _hex_centers(w: float, h: float, R: float):
    """Flat-top hex grid centres covering the canvas."""
    col_step = 1.5 * R
    row_step = math.sqrt(3.0) * R
    col = 0
    x = 0.0
    while x <= w + R:
        offset = (row_step / 2.0) if (col % 2) else 0.0
        y = offset
        while y <= h + R:
            yield (x, y)
            y += row_step
        x += col_step
        col += 1


def _hex_polygon(cx: float, cy: float, R: float) -> list[tuple[float, float]]:
    return [
        (cx + R * math.cos(math.radians(60 * i)),
         cy + R * math.sin(math.radians(60 * i)))
        for i in range(6)
    ]


def hexagons(
    plane: np.ndarray,
    *,
    cell: float = 12.0,
    scale: float = 1.0,
    min_coverage: float = 0.04,
) -> list[Polyline]:
    """Hex-grid halftone: each cell becomes a filled hexagon sized by coverage."""
    _require_2d(plane, "hexagons")
    h, w = plane.shape
    R = cell / 1.5
    out: list[Polyline] = []
    for cx, cy in _hex_centers(w, h, R):
        if not (0 <= cx < w and 0 <= cy < h):
            continue
        cov = sample_cell(plane, cx, cy, cell)
        if cov < min_coverage:
            continue
        r = R * scale * math.sqrt(min(cov, 1.0))
        if r > 0:
            out.append(polygon(_hex_polygon(cx, cy, r)))
    return out


def honeycomb(
    plane: np.ndarray,
    *,
    cell: float = 12.0,
    threshold: float = 0.2,
    width: float = 1.0,
) -> list[Polyline]:
    """Hex outlines drawn wherever coverage clears ``threshold`` (a mesh mask)."""
    _require_2d(plane, "honeycomb")
    h, w = plane.shape
    R = cell / 1.5
    out: list[Polyline] = []
    for cx, cy in _hex_centers(w, h, R):
        if not (0 <= cx < w and 0 <= cy < h):
            continue
        if sample_cell(plane, cx, cy, cell) < threshold:
            continue
        out.append(Polyline(points=_hex_polygon(cx, cy, R), closed=True, width=width))
    return out


# ─── Topographic contours (marching squares) ──────────────────────────────────

# case bitmask (v0=tl,v1=tr,v2=br,v3=bl) → edge pairs to connect.
# edges: 0=top(0-1) 1=right(1-2) 2=bottom(2-3) 3=left(3-0)
_MS_SEGMENTS = {
    1: [(3, 0)], 2: [(0, 1)], 3: [(3, 1)], 4: [(1, 2)],
    5: [(3, 0), (1, 2)], 6: [(0, 2)], 7: [(3, 2)], 8: [(2, 3)],
    9: [(2, 0)], 10: [(0, 1), (2, 3)], 11: [(2, 1)], 12: [(3, 1)],
    13: [(0, 1)], 14: [(0, 3)],
}
_MS_EDGE_CORNERS = {0: (0, 1), 1: (1, 2), 2: (2, 3), 3: (3, 0)}


def topographic(
    plane: np.ndarray,
    *,
    cell: float = 6.0,
    levels: tuple[float, ...] = (0.25, 0.5, 0.75),
    width: float = 1.0,
) -> list[Polyline]:
    """Iso-coverage contour lines via marching squares on a ``cell`` grid."""
    _require_2d(plane, "topographic")
    h, w = plane.shape
    out: list[Polyline] = []
    for level in levels:
        y = 0.0
        while y + cell < h:
            x = 0.0
            while x + cell < w:
                pos = [(x, y), (x + cell, y), (x + cell, y + cell), (x, y + cell)]
                vals = [sample(plane, px, py) for px, py in pos]
                case = sum((1 << i) for i in range(4) if vals[i] >= level)
                for ea, eb in _MS_SEGMENTS.get(case, ()):
                    p1 = _ms_edge_point(pos, vals, ea, level)
                    p2 = _ms_edge_point(pos, vals, eb, level)
                    out.append(Polyline(points=[p1, p2], width=width))
                x += cell
            y += cell
    return out


def _ms_edge_point(pos, vals, edge, level):
    a, b = _MS_EDGE_CORNERS[edge]
    va, vb = vals[a], vals[b]
    t = 0.5 if abs(vb - va) < 1e-9 else (level - va) / (vb - va)
    t = min(max(t, 0.0), 1.0)
    return (pos[a][0] + t * (pos[b][0] - pos[a][0]),
            pos[a][1] + t * (pos[b][1] - pos[a][1]))


# ─── Stipple (organic / noise) ─────────────────────────────────────────────────

def stipple(
    plane: np.ndarray,
    *,
    cell: float = 6.0,
    radius: float | None = None,
    jitter: float = 0.8,
    seed: int = 0,
) -> list[Dot]:
    """Random dots with placement probability ∝ coverage (stippling / noise)."""
    _require_2d(plane, "stipple")
    h, w = plane.shape
    radius = (cell * 0.22) if radius is None else radius
    rng = np.random.default_rng(seed)
    out: list[Dot] = []
    gy = cell / 2.0
    while gy < h:
        gx = cell / 2.0
        while gx < w:
            jx = gx + (rng.random() - 0.5) * cell * jitter
            jy = gy + (rng.random() - 0.5) * cell * jitter
            if 0 <= jx < w and 0 <= jy < h:
                if rng.random() < sample(plane, jx, jy):
                    out.append(Dot(x=jx, y=jy, r=radius))
            gx += cell
        gy += cell
    return out


# ─── Voronoi ──────────────────────────────────────────────────────────────────

def _weighted_seeds(plane: np.ndarray, *, cell: float, base: float,
                    jitter: float, seed: int) -> np.ndarray:
    """Jittered grid seeds kept with probability max(base, coverage).

    The ``base`` floor guarantees light areas still get enough points to
    tessellate; dark areas accumulate more, so cells shrink with coverage.
    """
    h, w = plane.shape
    rng = np.random.default_rng(seed)
    pts: list[tuple[float, float]] = []
    gy = cell / 2.0
    while gy < h:
        gx = cell / 2.0
        while gx < w:
            jx = gx + (rng.random() - 0.5) * cell * jitter
            jy = gy + (rng.random() - 0.5) * cell * jitter
            if 0 <= jx < w and 0 <= jy < h:
                if rng.random() < max(base, sample(plane, jx, jy)):
                    pts.append((jx, jy))
            gx += cell
        gy += cell
    return np.asarray(pts, dtype=float)


def _clip_segment(x0, y0, x1, y1, w, h):
    """Liang–Barsky clip of a segment to the rect [0, w] × [0, h]."""
    dx, dy = x1 - x0, y1 - y0
    p = (-dx, dx, -dy, dy)
    q = (x0, w - x0, y0, h - y0)
    u0, u1 = 0.0, 1.0
    for pi, qi in zip(p, q):
        if pi == 0:
            if qi < 0:
                return None             # parallel and outside
        else:
            t = qi / pi
            if pi < 0:
                if t > u1:
                    return None
                u0 = max(u0, t)
            else:
                if t < u0:
                    return None
                u1 = min(u1, t)
    # clamp away floating-point epsilon so endpoints land exactly in bounds
    return (
        min(max(x0 + u0 * dx, 0.0), w), min(max(y0 + u0 * dy, 0.0), h),
        min(max(x0 + u1 * dx, 0.0), w), min(max(y0 + u1 * dy, 0.0), h),
    )


def voronoi(
    plane: np.ndarray,
    *,
    spacing: float = 12.0,
    base: float = 0.15,
    jitter: float = 0.9,
    width: float = 1.0,
    seed: int = 0,
) -> list[Polyline]:
    """Voronoi cell web; seed density tracks coverage (denser where darker).

    Seeds are scattered on a jittered grid (one candidate per ``spacing`` cell,
    kept with probability ``max(base, coverage)``); the Voronoi ridges between
    them are emitted as stroked edges clipped to the image.
    """
    _require_2d(plane, "voronoi")
    from scipy.spatial import Voronoi, QhullError

    h, w = plane.shape
    pts = _weighted_seeds(plane, cell=spacing, base=base, jitter=jitter, seed=seed)
    if len(pts) < 4:
        return []
    try:
        vor = Voronoi(pts)
    except QhullError:
        return []

    out: list[Polyline] = []
    verts = vor.vertices
    for a, b in vor.ridge_vertices:
        if a < 0 or b < 0:              # skip ridges that run to infinity
            continue
        clipped = _clip_segment(verts[a][0], verts[a][1],
                                verts[b][0], verts[b][1], w, h)
        if clipped is None:
            continue
        cx0, cy0, cx1, cy1 = clipped
        out.append(Polyline([(cx0, cy0), (cx1, cy1)], width=width))
    return out


# ─── Splotches (dynamic-size ink blobs → shadows, B&W) ──────────────────────────

def splotches(
    plane: np.ndarray,
    *,
    cell: float = 10.0,
    scale: float = 1.1,
    irregularity: float = 0.35,
    jitter: float = 0.3,
    vertices: int = 11,
    min_coverage: float = 0.05,
    seed: int = 0,
) -> list[Polyline]:
    """Irregular ink blobs whose size tracks coverage — a hand-stippled shadow.

    Each grid cell with enough ink becomes an organic blob (a noisy polygon)
    grown by ``sqrt(coverage)``; darker areas grow bigger, overlapping blobs to
    pool into solid shadow.  Intended for a single (grayscale) channel.

    ``irregularity`` roughens the blob outline, ``jitter`` wobbles its centre,
    ``scale`` > 1 lets dark cells merge into solid shapes.
    """
    _require_2d(plane, "splotches")
    if cell <= 0:
        raise ValueError("cell must be > 0")
    h, w = plane.shape
    rng = np.random.default_rng(seed)
    base = cell / 2.0
    out: list[Polyline] = []
    gy = cell / 2.0
    while gy < h:
        gx = cell / 2.0
        while gx < w:
            cov = sample_cell(plane, gx, gy, cell)
            if cov >= min_coverage:
                cx = gx + (rng.random() - 0.5) * cell * jitter
                cy = gy + (rng.random() - 0.5) * cell * jitter
                r = base * scale * math.sqrt(min(cov, 1.0))
                pts = []
                for k in range(vertices):
                    ang = 2 * math.pi * (k + 0.5 * (rng.random() - 0.5)) / vertices
                    rr = r * (1.0 + irregularity * (rng.random() * 2.0 - 1.0))
                    pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
                out.append(polygon(pts))
            gx += cell
        gy += cell
    return out


# ─── Threshold + line carrier (self-bridging stencil) ───────────────────────────

def threshold_lines(
    plane: np.ndarray,
    *,
    threshold: float = 0.5,
    period: float = 8.0,
    duty: float = 0.5,
    angle: float = 0.0,
    step: float = 2.0,
) -> list[Polyline]:
    """Threshold cut broken into strips by a parallel-line carrier.

    Inside the thresholded (dark, coverage ≥ ``threshold``) regions, only stripes
    of width ``period × duty`` are cut; the ``period × (1 − duty)`` gaps between
    them are always left as material, so the sheet self-bridges — one part is
    always cut, the other always held.  Light regions stay fully material.

    Emits filled cut-strip polygons (oriented at ``angle``).
    """
    _require_2d(plane, "threshold_lines")
    h, w = plane.shape
    bar_w = max(0.0, period * duty)
    if bar_w == 0:
        return []
    theta = math.radians(angle)
    d = (math.cos(theta), math.sin(theta))        # along the line
    nrm = (-math.sin(theta), math.cos(theta))     # across lines
    cx0, cy0 = w / 2.0, h / 2.0
    half = math.hypot(w, h) / 2.0
    n_lines = int(math.ceil(half / period)) + 1
    n_steps = int(math.ceil((2 * half) / step)) + 1
    hw = bar_w / 2.0

    out: list[Polyline] = []
    for k in range(-n_lines, n_lines + 1):
        s = k * period
        ox, oy = cx0 + s * nrm[0], cy0 + s * nrm[1]
        runs: list[list] = []
        cur: list = []
        for m in range(n_steps + 1):
            t = -half + m * step
            x, y = ox + t * d[0], oy + t * d[1]
            on = 0 <= x < w and 0 <= y < h and sample(plane, x, y) >= threshold
            if on:
                cur.append((x, y))
            elif cur:
                runs.append(cur)
                cur = []
        if cur:
            runs.append(cur)
        for run in runs:
            p0, p1 = run[0], run[-1]
            out.append(polygon([
                (p0[0] - nrm[0] * hw, p0[1] - nrm[1] * hw),
                (p1[0] - nrm[0] * hw, p1[1] - nrm[1] * hw),
                (p1[0] + nrm[0] * hw, p1[1] + nrm[1] * hw),
                (p0[0] + nrm[0] * hw, p0[1] + nrm[1] * hw),
            ]))
    return out


# ─── Line screen (amplitude-modulated line stencil — the street-art look) ───────

def line_screen(
    plane: np.ndarray,
    *,
    period: float = 6.0,
    angle: float = 0.0,
    step: float = 1.5,
    min_coverage: float = 0.04,
    max_duty: float = 1.0,
    wave_amplitude: float = 0.0,
    wave_length: float | None = None,
) -> list[Polyline]:
    """Continuous parallel lines whose **width** swells with coverage.

    The classic spray-stencil / screenprint portrait: each line is a filled
    ribbon centred on its track, with half-width ``(period/2)·max_duty·coverage``
    — hair-thin in highlights, fattening until neighbours merge into solid
    black in the shadows.  Set ``max_duty`` < 1 to always leave a sliver of
    material between lines (more cuttable); ``angle`` rotates the screen.

    Set ``wave_amplitude`` > 0 to **undulate** the lines: every track is shifted
    perpendicularly by ``wave_amplitude·sin(2π·t / wave_length)`` (all lines in
    phase, so they stay parallel and never collide) — the wavy line-stencil look.

    Emits one filled ribbon polygon per continuous run.
    """
    _require_2d(plane, "line_screen")
    if period <= 0:
        raise ValueError("period must be > 0")
    h, w = plane.shape
    theta = math.radians(angle)
    d = (math.cos(theta), math.sin(theta))        # along the line
    nrm = (-math.sin(theta), math.cos(theta))     # across lines
    cx0, cy0 = w / 2.0, h / 2.0
    half = math.hypot(w, h) / 2.0
    n_lines = int(math.ceil(half / period)) + 1
    n_steps = int(math.ceil((2 * half) / step)) + 1
    max_hw = (period / 2.0) * max_duty
    wl = wave_length if wave_length else period * 6.0
    wk = (2.0 * math.pi / wl) if (wave_amplitude and wl) else 0.0

    def ribbon(run: list) -> None:
        if len(run) < 2:
            return
        top = [(px + nrm[0] * hw, py + nrm[1] * hw) for (px, py), hw in run]
        bot = [(px - nrm[0] * hw, py - nrm[1] * hw)
               for (px, py), hw in reversed(run)]
        out.append(polygon(top + bot))

    out: list[Polyline] = []
    for k in range(-n_lines, n_lines + 1):
        s = k * period
        ox, oy = cx0 + s * nrm[0], cy0 + s * nrm[1]
        run: list = []
        for m in range(n_steps + 1):
            t = -half + m * step
            x, y = ox + t * d[0], oy + t * d[1]
            if wk:                                  # undulate across the track
                disp = wave_amplitude * math.sin(wk * t)
                x, y = x + nrm[0] * disp, y + nrm[1] * disp
            cov = sample(plane, x, y) if (0 <= x < w and 0 <= y < h) else 0.0
            if cov >= min_coverage:
                run.append(((x, y), max_hw * min(cov, 1.0)))
            else:
                ribbon(run)
                run = []
        ribbon(run)
    return out
