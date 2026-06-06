"""mask.py
─────────
The :class:`StencilMask` — the canonical representation for Phase 3.

A stencil is a physical sheet with material removed where ink should pass.  We
model that sheet as a boolean raster:

    cut[y, x] == True   →  material removed (a hole / the cut-out)
    cut[y, x] == False  →  material kept    (the sheet body)

Everything in :mod:`fabrication` (island detection, bridges, minimum feature
size, fabrication checks) operates on this mask.  PIL rasterises the vector
primitives; the mask can be vectorised back to closed cut polygons via
:func:`mask_to_polylines` so an optimised result re-enters the export pipeline.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from ..geometry import Dot, Layer, Polyline, Stencil, polygon


@dataclass(slots=True)
class StencilMask:
    """Boolean sheet: ``True`` = cut (hole), ``False`` = material."""

    cut: np.ndarray  # bool (H, W)

    # ── construction ──────────────────────────────────────────────────────
    @property
    def shape(self) -> tuple[int, int]:
        return self.cut.shape

    @property
    def material(self) -> np.ndarray:
        return ~self.cut

    def copy(self) -> "StencilMask":
        return StencilMask(self.cut.copy())

    @classmethod
    def from_coverage(cls, plane: np.ndarray, *, threshold: float = 0.5) -> "StencilMask":
        """Cut wherever ink coverage reaches ``threshold`` (dark → hole)."""
        if plane.ndim != 2:
            raise ValueError("from_coverage expects a 2-D coverage plane")
        return cls(plane >= threshold)

    @classmethod
    def from_layer(cls, layer: Layer, size: tuple[int, int],
                   *, supersample: int = 1) -> "StencilMask":
        """Rasterise one layer's primitives into a cut mask (``size`` = (w, h)).

        ``supersample`` > 1 rasterises at that integer multiple of ``size`` (the
        geometry is scaled to match). This resolves the sub-pixel material webs
        between near-tangent shapes — at the native resolution they vanish and
        falsely seal off "islands"; a 2–3× raster recovers them.
        """
        w, h = size
        if supersample and supersample > 1:
            f = int(supersample)
            prims = [_scale_prim(p, f) for p in layer.primitives]
            return cls(_rasterize(prims, (w * f, h * f)))
        return cls(_rasterize(layer.primitives, size))

    @classmethod
    def from_stencil(cls, stencil: Stencil) -> "StencilMask":
        """Union every layer of a stencil into one cut mask."""
        size = (int(round(stencil.width)), int(round(stencil.height)))
        prims = [p for layer in stencil.layers for p in layer.primitives]
        return cls(_rasterize(prims, size))

    # ── previews / export ─────────────────────────────────────────────────
    def to_preview_array(self) -> np.ndarray:
        """Float image: material dark (0.12), holes white (1.0)."""
        out = np.full(self.cut.shape, 0.12, dtype=np.float64)
        out[self.cut] = 1.0
        return out

    def save_preview(self, path: str | Path) -> Path:
        path = Path(path)
        img = Image.fromarray((self.to_preview_array() * 255 + 0.5).astype(np.uint8))
        img.save(path)
        return path

    def to_stencil(self, *, color: tuple[int, int, int] = (0, 0, 0),
                   name: str = "cut", units: str = "px",
                   simplify: float = 1.0) -> Stencil:
        """Vectorise the cut regions into a single-layer :class:`Stencil`."""
        h, w = self.cut.shape
        st = Stencil(width=float(w), height=float(h), units=units)
        layer = st.layer(name, color=color)
        layer.add(mask_to_polylines(self.cut, simplify=simplify))
        return st


# ─── rasterisation (vector → mask) ────────────────────────────────────────────

def _scale_prim(prim, f: float):
    """Scale a primitive's coordinates (and radius/width) by ``f``."""
    if isinstance(prim, Dot):
        return Dot(prim.x * f, prim.y * f, prim.r * f)
    return Polyline(
        points=[(x * f, y * f) for x, y in prim.points],
        closed=prim.closed, width=prim.width * f, fill=prim.fill,
        holes=[[(x * f, y * f) for x, y in h] for h in prim.holes],
    )


def _rasterize(primitives, size: tuple[int, int]) -> np.ndarray:
    w, h = size
    img = Image.new("1", (w, h), 0)
    draw = ImageDraw.Draw(img)
    for prim in primitives:
        if isinstance(prim, Dot):
            draw.ellipse(
                [prim.x - prim.r, prim.y - prim.r, prim.x + prim.r, prim.y + prim.r],
                fill=1,
            )
        elif isinstance(prim, Polyline):
            pts = [(float(x), float(y)) for x, y in prim.points]
            if prim.fill and len(pts) >= 3:
                draw.polygon(pts, fill=1)
                for hole in prim.holes:               # punch holes back out
                    hpts = [(float(x), float(y)) for x, y in hole]
                    if len(hpts) >= 3:
                        draw.polygon(hpts, fill=0)
            elif len(pts) >= 2:
                draw.line(pts, fill=1, width=max(1, int(round(prim.width))))
    return np.asarray(img, dtype=bool)


# ─── vectorisation (mask → vector) ────────────────────────────────────────────

# 8-neighbourhood offsets, clockwise from North (row, col).
_MOORE = [(-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1)]


def _trace_component(comp: np.ndarray) -> list[tuple[float, float]]:
    """Moore-neighbour boundary trace of a single 8-connected blob (padded)."""
    fg = np.argwhere(comp)
    if len(fg) == 0:
        return []
    start = (int(fg[0][0]), int(fg[0][1]))  # top-most, then left-most
    H, W = comp.shape

    def is_fg(r: int, c: int) -> bool:
        return 0 <= r < H and 0 <= c < W and comp[r, c]

    # First boundary pixel; we arrived from the west (background to the left).
    boundary = [start]
    cur = start
    back_dir = 6  # index in _MOORE pointing West (0, -1)
    max_steps = int(comp.sum()) * 4 + 8
    for _ in range(max_steps):
        # Search clockwise starting just after the backtrack direction.
        found = None
        for k in range(8):
            d = (back_dir + 1 + k) % 8
            dr, dc = _MOORE[d]
            nr, nc = cur[0] + dr, cur[1] + dc
            if is_fg(nr, nc):
                found = (d, (nr, nc))
                break
        if found is None:
            break  # isolated pixel
        d, nxt = found
        # New backtrack = direction from nxt back to cur (opposite of d).
        back_dir = (d + 4) % 8
        cur = nxt
        if cur == start and len(boundary) > 1:
            break
        boundary.append(cur)
    # convert (row, col) → (x, y)
    return [(float(c), float(r)) for r, c in boundary]


def _simplify_ring(points: list[tuple[float, float]], tol: float) -> list[tuple[float, float]]:
    """Cheap vertex decimation: drop points closer than ``tol`` to the last kept."""
    if tol <= 0 or len(points) < 4:
        return points
    out = [points[0]]
    for p in points[1:]:
        lx, ly = out[-1]
        if (p[0] - lx) ** 2 + (p[1] - ly) ** 2 >= tol * tol:
            out.append(p)
    return out if len(out) >= 3 else points


def _trace_ring(comp: np.ndarray, simplify: float) -> list | None:
    """Trace a single blob and simplify. ``None`` if fewer than 3 points."""
    ring = _trace_component(comp)
    if len(ring) < 3:
        return None
    return _simplify_ring(ring, simplify)


def _margin_slice(sl, shape):
    """Expand a ``find_objects`` slice by 1 px (clamped) → (slice, x0, y0)."""
    h, w = shape
    y0, y1 = max(0, sl[0].start - 1), min(h, sl[0].stop + 1)
    x0, x1 = max(0, sl[1].start - 1), min(w, sl[1].stop + 1)
    return (slice(y0, y1), slice(x0, x1)), x0, y0


def mask_to_polylines(cut: np.ndarray, *, simplify: float = 1.0) -> list[Polyline]:
    """Trace each cut blob into a closed, filled polygon with its inner holes.

    The outer boundary of every 8-connected cut region is traced; any enclosed
    material (a hole in the cut, e.g. the middle of an annular cut) is traced as
    an inner ring and attached via :attr:`Polyline.holes` for even-odd fill.

    Each blob is processed inside its own bounding box (via ``find_objects``), and
    enclosed material is found from **one** global ``binary_fill_holes`` — so the
    expensive hole pass only runs for the few blobs that actually wrap material,
    not for every dot in a halftone.
    """
    from scipy import ndimage

    s8 = np.ones((3, 3), int)
    labels, n = ndimage.label(cut, structure=s8)
    slices = ndimage.find_objects(labels)
    # enclosed material, computed once for the whole sheet (not per blob)
    enclosed = ndimage.binary_fill_holes(cut, structure=s8) & ~cut

    out: list[Polyline] = []
    for label, sl in enumerate(slices, start=1):
        if sl is None:
            continue
        msl, x0, y0 = _margin_slice(sl, cut.shape)
        sub = labels[msl] == label                   # blob in its bbox + margin
        ring = _trace_ring(sub, simplify)
        if ring is None:
            continue
        ring = [(x + x0, y + y0) for x, y in ring]   # → global pixels
        holes: list[list] = []
        # only the blobs that wrap enclosed material pay for hole extraction
        if enclosed[msl].any():
            filled = ndimage.binary_fill_holes(sub, structure=s8)
            hole_mask = filled & ~sub
            if hole_mask.any():
                hlabels, hn = ndimage.label(hole_mask)   # holes: 4-connected dual
                for hl in range(1, hn + 1):
                    hring = _trace_ring(hlabels == hl, simplify)
                    if hring is not None:
                        holes.append([(x + x0, y + y0) for x, y in hring])
        out.append(polygon(ring, holes=holes))
    return out
