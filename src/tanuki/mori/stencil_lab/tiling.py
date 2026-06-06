"""tiling.py
───────────
Panelise a stencil into tiles that fit a cutting plotter's bed.

A design larger than the plotter bed must be split into a grid of tiles, each
cut separately and reassembled.  :func:`tile_stencil` does that: it clips the
geometry to each tile rectangle, optionally with **overlap** (a shared margin so
adjacent tiles glue together) and **crop marks** (corner ticks for alignment),
and translates each tile to its own ``(0, 0)`` origin so it drops straight onto
the plotter.

Clipping is exact:

* dots are kept when their centre lies in the tile (overhang ≤ radius — set
  ``overlap`` ≥ the largest dot to avoid any loss);
* open / stroked polylines are clipped with Liang–Barsky (split where they
  leave and re-enter the tile);
* filled polygons (and their holes) are clipped with Sutherland–Hodgman.
"""

from __future__ import annotations

from dataclasses import dataclass

from .geometry import Dot, Layer, Point, Polyline, Stencil, polygon

Rect = tuple[float, float, float, float]  # (xmin, ymin, xmax, ymax)


@dataclass(slots=True)
class Tile:
    """One panel of a tiled stencil, translated to its own origin."""

    row: int
    col: int
    rect: Rect            # source rectangle in the original canvas
    stencil: Stencil      # clipped geometry, origin at (0, 0)

    @property
    def name(self) -> str:
        return f"r{self.row}c{self.col}"


# ─── grid ─────────────────────────────────────────────────────────────────────

def _spans(total: float, bed: float, overlap: float,
           full: bool = False) -> list[tuple[float, float]]:
    """1-D tile spans covering ``[0, total]`` in ``bed``-sized steps.

    With ``full`` every span is exactly ``bed`` long (uniform sheets — the last
    one runs past ``total`` into blank space); otherwise the last span is
    clamped to ``total`` (tight, variable-size tiles).
    """
    if bed <= 0:
        raise ValueError("bed size must be > 0")
    if overlap >= bed:
        raise ValueError("overlap must be smaller than the bed size")
    if bed >= total:
        return [(0.0, bed if full else total)]
    step = bed - overlap
    spans: list[tuple[float, float]] = []
    start = 0.0
    while start < total:
        end = start + bed if full else min(start + bed, total)
        spans.append((start, end))
        if start + bed >= total:
            break
        start += step
    return spans


def tile_grid(width: float, height: float, bed_w: float, bed_h: float,
              *, overlap: float = 0.0, full: bool = False) -> list[list[Rect]]:
    """Compute the rectangle grid (rows of columns) for the given bed.

    ``full=True`` makes every tile a full ``bed``-sized sheet (uniform pages).
    """
    xs = _spans(width, bed_w, overlap, full)
    ys = _spans(height, bed_h, overlap, full)
    return [[(x0, y0, x1, y1) for x0, x1 in xs] for y0, y1 in ys]


# ─── clipping ─────────────────────────────────────────────────────────────────

def _clip_segment(a: Point, b: Point, rect: Rect):
    """Liang–Barsky clip of segment a→b to ``rect``; ``None`` if fully outside."""
    xmin, ymin, xmax, ymax = rect
    x0, y0 = a
    x1, y1 = b
    dx, dy = x1 - x0, y1 - y0
    p = (-dx, dx, -dy, dy)
    q = (x0 - xmin, xmax - x0, y0 - ymin, ymax - y0)
    u0, u1 = 0.0, 1.0
    for pi, qi in zip(p, q):
        if pi == 0:
            if qi < 0:
                return None
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
    return ((x0 + u0 * dx, y0 + u0 * dy), (x0 + u1 * dx, y0 + u1 * dy))


def _clip_polyline(points: list[Point], rect: Rect) -> list[list[Point]]:
    """Clip an open polyline to ``rect`` → list of contiguous sub-polylines."""
    runs: list[list[Point]] = []
    cur: list[Point] = []
    for a, b in zip(points, points[1:]):
        seg = _clip_segment(a, b, rect)
        if seg is None:
            if len(cur) >= 2:
                runs.append(cur)
            cur = []
            continue
        p, q = seg
        if not cur:
            cur = [p, q]
        elif cur[-1] == p:
            cur.append(q)
        else:
            if len(cur) >= 2:
                runs.append(cur)
            cur = [p, q]
    if len(cur) >= 2:
        runs.append(cur)
    return runs


def _clip_polygon(poly: list[Point], rect: Rect) -> list[Point]:
    """Sutherland–Hodgman clip of a polygon to the rectangle ``rect``."""
    xmin, ymin, xmax, ymax = rect

    def _edge(pts, inside, inter):
        if not pts:
            return []
        out: list[Point] = []
        prev = pts[-1]
        pin = inside(prev)
        for cur in pts:
            cin = inside(cur)
            if cin:
                if not pin:
                    out.append(inter(prev, cur))
                out.append(cur)
            elif pin:
                out.append(inter(prev, cur))
            prev, pin = cur, cin
        return out

    def ix(a, b, xv):
        t = (xv - a[0]) / (b[0] - a[0])
        return (xv, a[1] + t * (b[1] - a[1]))

    def iy(a, b, yv):
        t = (yv - a[1]) / (b[1] - a[1])
        return (a[0] + t * (b[0] - a[0]), yv)

    pts = list(poly)
    pts = _edge(pts, lambda p: p[0] >= xmin, lambda a, b: ix(a, b, xmin))
    pts = _edge(pts, lambda p: p[0] <= xmax, lambda a, b: ix(a, b, xmax))
    pts = _edge(pts, lambda p: p[1] >= ymin, lambda a, b: iy(a, b, ymin))
    pts = _edge(pts, lambda p: p[1] <= ymax, lambda a, b: iy(a, b, ymax))
    return pts


def clip_to_rect(prim, rect: Rect) -> list:
    """Clip a single primitive to ``rect`` → list of clipped primitives."""
    xmin, ymin, xmax, ymax = rect
    if isinstance(prim, Dot):
        if xmin <= prim.x <= xmax and ymin <= prim.y <= ymax:
            return [Dot(prim.x, prim.y, prim.r)]
        return []
    if isinstance(prim, Polyline):
        if prim.fill and len(prim.points) >= 3:
            outer = _clip_polygon(prim.points, rect)
            if len(outer) < 3:
                return []
            holes = []
            for hole in prim.holes:
                clipped = _clip_polygon(hole, rect)
                if len(clipped) >= 3:
                    holes.append(clipped)
            return [polygon(outer, width=prim.width, holes=holes)]
        return [
            Polyline(run, closed=False, width=prim.width)
            for run in _clip_polyline(prim.points, rect)
        ]
    return []


# ─── translation ──────────────────────────────────────────────────────────────

def _translate(prim, dx: float, dy: float):
    if isinstance(prim, Dot):
        return Dot(prim.x + dx, prim.y + dy, prim.r)
    return Polyline(
        points=[(x + dx, y + dy) for x, y in prim.points],
        closed=prim.closed, width=prim.width, fill=prim.fill,
        holes=[[(x + dx, y + dy) for x, y in h] for h in prim.holes],
    )


def _crop_marks(w: float, h: float, *, size: float, width: float) -> list[Polyline]:
    """L-shaped corner ticks for tile alignment (in tile-local coordinates)."""
    s = size
    return [
        Polyline([(0, s), (0, 0), (s, 0)], width=width),
        Polyline([(w - s, 0), (w, 0), (w, s)], width=width),
        Polyline([(0, h - s), (0, h), (s, h)], width=width),
        Polyline([(w, h - s), (w, h), (w - s, h)], width=width),
    ]


def sheet_frame(w: float, h: float, *, inset: float, width: float = 0.5) -> Polyline | None:
    """A rectangular border outline inset ``inset`` from a ``w×h`` sheet's edges.

    Returns ``None`` when the inset leaves no room (so callers can skip it).
    """
    if inset <= 0 or w - 2 * inset <= 0 or h - 2 * inset <= 0:
        return None
    x0, y0, x1, y1 = inset, inset, w - inset, h - inset
    return Polyline([(x0, y0), (x1, y0), (x1, y1), (x0, y1)],
                    closed=True, width=width)


def apply_frame(stencil: Stencil, *, inset: float, width: float = 0.0,
                clip: bool = True) -> Stencil:
    """Clear an ``inset`` margin around the artwork — optionally drawing a border.

    With ``clip`` (default) every layer except ``crop`` is clipped to the inset
    rectangle, so **no artwork is left in the margin** (otherwise a cutter would
    still cut the halftone that bled into it). A visible border outline is added
    on a ``frame`` layer **only when ``width`` > 0** — by default the margin is
    just cleared and *no extra cut path* is drawn (the cutter has no frame to
    cut). If the inset leaves no room the stencil is returned unchanged.
    """
    if inset <= 0 or stencil.width - 2 * inset <= 0 or stencil.height - 2 * inset <= 0:
        return stencil
    rect = (inset, inset, stencil.width - inset, stencil.height - inset)
    out = Stencil(width=stencil.width, height=stencil.height, units=stencil.units)
    for layer in stencil.layers:
        nl = out.layer(layer.name, color=layer.color)
        if clip and layer.name not in ("crop", "frame"):
            for prim in layer.primitives:
                nl.add(clip_to_rect(prim, rect))
        else:
            nl.add(list(layer.primitives))
    if width > 0:                               # opt-in visible border (it IS a cut path)
        box = sheet_frame(stencil.width, stencil.height, inset=inset, width=width)
        if box is not None:
            out.layer("frame", color=(0, 0, 0)).add(box)
    return out


# ─── main API ──────────────────────────────────────────────────────────────────

def tile_stencil(
    stencil: Stencil,
    bed_width: float,
    bed_height: float,
    *,
    overlap: float = 0.0,
    crop_marks: bool = True,
    crop_size: float = 8.0,
    crop_width: float = 1.0,
    frame: float = 0.0,
    frame_width: float = 0.0,
    full: bool = False,
    skip_empty: bool = False,
) -> list[Tile]:
    """Split ``stencil`` into tiles no larger than ``bed_width`` × ``bed_height``.

    Each returned :class:`Tile` carries a clipped, origin-aligned stencil ready
    to send to a plotter.  ``overlap`` adds a shared margin between neighbours
    (use ≥ your largest dot/stroke so nothing is lost at seams); ``crop_marks``
    stamps corner ticks on a ``crop`` layer for re-alignment.

    ``frame`` > 0 clears that much margin around each tile (clipping artwork out
    of it); a visible border outline is added only when ``frame_width`` > 0.

    ``full=True`` makes every tile a full ``bed``-sized page (uniform sheets,
    the edges run into blank space) instead of clamping edge tiles to the design.
    ``skip_empty=True`` drops tiles whose ink layers are empty (blank sheets).
    """
    grid = tile_grid(stencil.width, stencil.height, bed_width, bed_height,
                     overlap=overlap, full=full)
    tiles: list[Tile] = []
    for r, row in enumerate(grid):
        for c, rect in enumerate(row):
            x0, y0, x1, y1 = rect
            tw, th = x1 - x0, y1 - y0
            tile_st = Stencil(width=tw, height=th, units=stencil.units)
            empty = True
            for layer in stencil.layers:
                new_layer = tile_st.layer(layer.name, color=layer.color)
                for prim in layer.primitives:
                    for clipped in clip_to_rect(prim, rect):
                        new_layer.add(_translate(clipped, -x0, -y0))
                        empty = False
            if skip_empty and empty:
                continue                       # blank sheet — nothing to cut here
            if crop_marks:
                tile_st.layer("crop", color=(0, 0, 0)).add(
                    _crop_marks(tw, th, size=crop_size, width=crop_width)
                )
            if frame > 0:                       # frame + clip artwork out of the margin
                tile_st = apply_frame(tile_st, inset=frame, width=frame_width)
            tiles.append(Tile(row=r, col=c, rect=rect, stencil=tile_st))
    return tiles
