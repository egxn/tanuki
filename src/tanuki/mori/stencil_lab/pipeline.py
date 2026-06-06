"""pipeline.py
─────────────
High-level glue tying the stages into one call.

:func:`halftone_stencil` is the "happy path": image path → multi-layer
:class:`~stencil_lab.geometry.Stencil`, with conventional per-channel screen
angles to avoid moiré, and — since the point of a stencil is to be *cut* —
**optimised for cutting by default** (see :func:`optimize_for_cutting`).
"""

from __future__ import annotations

from pathlib import Path

import numpy as np

from .geometry import Dot, Polyline, Stencil
from .image_io import load_image, resize
from .patterns import PRIMARY_PATTERNS, generate
from .separation import Separation

# Classic CMYK screen angles; falls back to evenly-spread angles for other
# separations so multi-layer screens never share an angle.
_CMYK_ANGLES = {"cyan": 15.0, "magenta": 75.0, "yellow": 0.0, "key": 45.0}


def _angle_for(name: str, index: int, total: int) -> float:
    if name in _CMYK_ANGLES:
        return _CMYK_ANGLES[name]
    return (index * 30.0) % 90.0 if total > 1 else 45.0


def build_stencil(
    sep: Separation,
    size: tuple[int, int],
    *,
    pattern: str = "dots",
    cell: float = 8.0,
    units: str = "px",
    angle: float | None = None,
    params: dict | None = None,
) -> Stencil:
    """Render every channel of a :class:`Separation` into a layered stencil.

    ``size`` is ``(width, height)`` in pixels (matching the coverage planes).
    ``pattern`` selects a generator from :data:`patterns.PATTERNS` (``dots``,
    ``lines``, ``circular``, ``crosshatch``, ``sine``, ``spiral``, ``hexagons``,
    ``topographic``, ``stipple``, …).

    By default each channel gets a conventional per-channel screen *angle*
    (15° / 75° / 0° / 45° for CMYK) to avoid moiré.  Pass ``angle`` to force a
    single angle on every layer instead (e.g. ``angle=0`` for the horizontal
    street-art ``line_screen`` look).  ``params`` are extra generator knobs
    forwarded through :func:`patterns.generate` (e.g. ``max_duty`` / ``wave_*``
    for ``line_screen``).
    """
    w, h = size
    params = params or {}
    stencil = Stencil(width=float(w), height=float(h), units=units)
    total = len(sep)
    for i, ch in enumerate(sep):
        a = angle if angle is not None else _angle_for(ch.name, i, total)
        prims = generate(ch.plane, pattern, cell=cell, angle=a, **params)
        layer = stencil.layer(ch.name, color=ch.color)
        layer.add(prims)
    return stencil


def carrier_mask(plane: np.ndarray, carrier: str, *, threshold: float = 0.5,
                 duty: float = 0.5, cell: float = 8.0, angle: float = 0.0,
                 params: dict | None = None) -> np.ndarray:
    """Boolean cut mask = ``threshold ∩ carrier-texture``.

    The carrier pattern is rendered at a *fixed* density (``duty``, the uniform
    coverage it is drawn at) so it always leaves gaps — a connected material
    lattice. Intersecting with the dark regions (``coverage ≥ threshold``) cuts
    only inside the image, and the carrier's gaps + the highlights stay as
    material bridges. This is the generalisation of :func:`threshold_lines` to
    any pattern (``lines``, ``honeycomb``, ``voronoi``, …).
    """
    from .fabrication.mask import _rasterize

    h, w = plane.shape
    texture = generate(np.full((h, w), float(duty)), carrier, cell=cell,
                       angle=angle, **(params or {}))
    return (plane >= threshold) & _rasterize(texture, (w, h))


def carrier_stencil(
    sep: "Separation",
    size: tuple[int, int],
    *,
    carrier: str = "lines",
    threshold: float = 0.5,
    duty: float = 0.5,
    cell: float = 8.0,
    units: str = "px",
    optimize: bool = True,
    min_hole_area: int = 4,
    min_island_area: int = 16,
    bridge_width: float = 2.0,
    min_feature_px: float = 2.0,
    angle: float | None = None,
    params: dict | None = None,
) -> Stencil:
    """Build a layered stencil by cutting ``threshold ∩ carrier`` per channel.

    Each channel's dark regions are cut through the ``carrier`` lattice (so the
    result self-bridges), then optionally optimised, and vectorised to cut
    polygons. Makes the *Experimental* patterns fabrication-useful.
    """
    from .fabrication import StencilMask, mask_to_polylines, optimize_mask

    w, h = size
    out = Stencil(width=float(w), height=float(h), units=units)
    total = len(sep)
    for i, ch in enumerate(sep):
        a = angle if angle is not None else _angle_for(ch.name, i, total)
        cut = carrier_mask(ch.plane, carrier, threshold=threshold, duty=duty,
                           cell=cell, angle=a, params=params)
        mask = StencilMask(cut)
        if optimize:
            mask, _ = optimize_mask(
                mask, min_hole_area=min_hole_area, min_island_area=min_island_area,
                bridge_width=bridge_width, min_feature_px=min_feature_px,
            )
        out.layer(ch.name, color=ch.color).add(mask_to_polylines(mask.cut))
    return out


def cut_cleanup(stencil: Stencil, *, min_feature_px: float = 2.0) -> Stencil:
    """Vector-preserving cut prep — keeps each shape exactly, drops sub-feature.

    The *stable* patterns (dots, hexagons, line_screen, splotches) already emit
    clean, separated filled shapes that cut fine on their own (the sheet stays
    one connected piece around the holes). So instead of rasterising and merging
    them — which fuses touching shapes into incoherent blobs — we keep the
    primitives verbatim and only drop ones smaller than the tool's minimum
    feature (they would not cut cleanly). The output looks like the preview.
    """
    out = Stencil(width=stencil.width, height=stencil.height, units=stencil.units)
    for layer in stencil.layers:
        nl = out.layer(layer.name, color=layer.color)
        for p in layer.primitives:
            if isinstance(p, Dot):
                if 2.0 * p.r >= min_feature_px:
                    nl.add(Dot(p.x, p.y, p.r))
            elif isinstance(p, Polyline):
                if p.fill:
                    x0, y0, x1, y1 = p.bbox()
                    if min(x1 - x0, y1 - y0) >= min_feature_px:
                        nl.add(p)
                elif p.width >= min_feature_px:
                    nl.add(p)
    return out


def cut_ready(stencil: Stencil, pattern: str, *, min_feature_px: float = 2.0,
              min_hole_area: int = 4, min_island_area: int = 16,
              bridge_width: float = 2.0, strategy: str = "legacy") -> Stencil:
    """Make a stencil cut-ready, choosing the strategy by pattern.

    Default (``strategy="legacy"``, unchanged): stable patterns →
    :func:`cut_cleanup` (preserve shapes); everything else →
    :func:`optimize_for_cutting` (raster bridge/merge).

    ``strategy="grouped"`` (opt-in) uses the pattern-specific
    :func:`cut_grouped` instead — line screens are left exactly as drawn and the
    shape screens (dots, hexagons, …) have their *touching* shapes merged into
    clean cut masses while lone shapes stay verbatim.
    """
    if strategy == "grouped":
        return cut_grouped(
            stencil, pattern, min_feature_px=min_feature_px,
            min_hole_area=min_hole_area, min_island_area=min_island_area,
            bridge_width=bridge_width,
        )
    if pattern in PRIMARY_PATTERNS:
        return cut_cleanup(stencil, min_feature_px=min_feature_px)
    return optimize_for_cutting(
        stencil, min_hole_area=min_hole_area, min_island_area=min_island_area,
        bridge_width=bridge_width, min_feature_px=min_feature_px,
    )


# ─── per-pattern "grouped" cut strategy (opt-in) ────────────────────────────
# Tailors the cut prep to the pattern: line screens are left exactly as drawn
# (they already self-bridge), while shape screens have their *touching* shapes
# merged into one clean cut blob — a dark mass becomes a single coherent polygon
# instead of a pile of overlapping circles, while isolated shapes stay verbatim.
_LINE_LIKE = ("line_screen", "lines", "threshold_lines")
_BLOB_LIKE = ("dots", "hexagons", "stipple", "splotches")


def _centroid(prim) -> tuple[float, float]:
    if isinstance(prim, Dot):
        return (prim.x, prim.y)
    n = max(1, len(prim.points))
    return (sum(x for x, _ in prim.points) / n,
            sum(y for _, y in prim.points) / n)


def _feature_ok(prim, min_feature_px: float) -> bool:
    """Same minimum-feature test as :func:`cut_cleanup` (keep only cuttable bits)."""
    if isinstance(prim, Dot):
        return 2.0 * prim.r >= min_feature_px
    if prim.fill:
        x0, y0, x1, y1 = prim.bbox()
        return min(x1 - x0, y1 - y0) >= min_feature_px
    return prim.width >= min_feature_px


def _preserve(stencil: Stencil) -> Stencil:
    """A copy that keeps every primitive exactly (used for line screens)."""
    out = Stencil(width=stencil.width, height=stencil.height, units=stencil.units)
    for layer in stencil.layers:
        out.layer(layer.name, color=layer.color).add(list(layer.primitives))
    return out


def merge_touching_shapes(stencil: Stencil, *, min_feature_px: float = 2.0,
                          simplify: float = 1.0) -> Stencil:
    """Merge each layer's *touching* shapes into one cut blob; keep lone shapes.

    Connected groups of overlapping primitives — the dark "masses" where dots /
    hexagons grow into each other — are traced into a single closed polygon
    (with holes), so the cut is one coherent outline rather than many overlapping
    circles. Shapes that touch nothing are kept verbatim (a clean circle /
    hexagon); sub-feature specks are dropped.
    """
    from scipy import ndimage

    from .fabrication.mask import _rasterize, mask_to_polylines

    w, h = int(round(stencil.width)), int(round(stencil.height))
    s8 = np.ones((3, 3), int)
    out = Stencil(width=stencil.width, height=stencil.height, units=stencil.units)
    for layer in stencil.layers:
        prims = list(layer.primitives)
        nl = out.layer(layer.name, color=layer.color)
        if not prims:
            continue
        labels, n = ndimage.label(_rasterize(prims, (w, h)), structure=s8)
        if n == 0:
            continue
        # how many primitives share each connected component (via their centroid)
        counts = np.zeros(n + 1, dtype=np.int64)
        prim_label = np.empty(len(prims), dtype=np.int64)
        for i, p in enumerate(prims):
            cx, cy = _centroid(p)
            ix = min(max(int(round(cx)), 0), w - 1)
            iy = min(max(int(round(cy)), 0), h - 1)
            lab = int(labels[iy, ix])
            prim_label[i] = lab
            if lab:
                counts[lab] += 1
        # a component shared by ≥2 primitives is a merged mass → one traced blob
        blob_mask = counts[labels] > 1
        if blob_mask.any():
            nl.add(mask_to_polylines(blob_mask, simplify=simplify))
        # lone shapes → keep the exact primitive (when it meets the min feature)
        for p, lab in zip(prims, prim_label):
            if counts[lab] <= 1 and _feature_ok(p, min_feature_px):
                nl.add(p)
    return out


def cut_grouped(stencil: Stencil, pattern: str, *, min_feature_px: float = 2.0,
                min_hole_area: int = 4, min_island_area: int = 16,
                bridge_width: float = 2.0, simplify: float = 1.0) -> Stencil:
    """Pattern-specific cut prep (the ``strategy="grouped"`` path of cut_ready).

    * **line screens** (``line_screen`` / ``lines`` / ``threshold_lines``) — left
      exactly as drawn; they already self-bridge, so nothing is merged or moved.
    * **shape screens** (``dots`` / ``hexagons`` / ``stipple`` / ``splotches``) —
      :func:`merge_touching_shapes` groups touching shapes into clean masses and
      keeps lone shapes verbatim.
    * **anything else** — falls back to :func:`optimize_for_cutting`.
    """
    if pattern in _LINE_LIKE:
        return _preserve(stencil)
    if pattern in _BLOB_LIKE:
        return merge_touching_shapes(stencil, min_feature_px=min_feature_px,
                                     simplify=simplify)
    return optimize_for_cutting(
        stencil, min_hole_area=min_hole_area, min_island_area=min_island_area,
        bridge_width=bridge_width, min_feature_px=min_feature_px,
    )


# ─── support grid / mesh (opt-in) ───────────────────────────────────────────
# A regular **mesh** (like a metal grid or a die over leather): a connected
# lattice of *material* — the supports — with the cut confined to the mesh's
# openings. Each pattern cell becomes a hole shrunk by ``wall`` so a material
# wall always survives between neighbours; the cut inside a hole still follows
# the pattern (dot/hex size ∝ coverage). Nothing can detach — the mesh is one
# connected piece. Defined for the regular-lattice screens (dots / hexagons).
_MESH_PATTERNS = ("dots", "hexagons")


def _mesh_wall(cell: float, width: float | None) -> float:
    """Resolve the mesh wall thickness: keep a connected mesh and an open hole."""
    wall = width if (width and width > 0) else max(2.0, cell * 0.25)
    return max(1.5, min(wall, cell * 0.6))


def mesh_opening_shapes(pattern: str, *, cell: float = 8.0, angle: float = 0.0,
                        width: float | None = None,
                        size: tuple[int, int]):
    """The support mesh's cut openings as **vector primitives** (or ``None``).

    Each pattern cell at full coverage, drawn with a reduced ``scale`` so adjacent
    cells stop short of touching (leaving a ``width``-px material wall) — a clean
    lattice of separated circles (dots) / hexagons. Useful to render the mesh as
    crisp outlines for debugging.
    """
    if pattern not in _MESH_PATTERNS:
        return None
    from .patterns import halftone_dots, hexagons as _hexagons

    w, h = size
    full = np.ones((h, w))
    scale = max(0.3, 1.0 - _mesh_wall(cell, width) / max(cell, 1.0))
    if pattern == "hexagons":
        return _hexagons(full, cell=cell, scale=scale, min_coverage=0.0)
    return halftone_dots(full, cell=cell, angle=angle, scale=scale, min_coverage=0.0)


def mesh_openings(pattern: str, *, cell: float = 8.0, angle: float = 0.0,
                  width: float | None = None,
                  size: tuple[int, int]) -> np.ndarray | None:
    """Filled lattice of separated cut openings for the support mesh (dots/hex).

    The rasterised form of :func:`mesh_opening_shapes`: a boolean mask of the
    openings the cut is confined to (the complement is the connected support
    mesh). Returns ``None`` for patterns without a regular lattice.
    """
    shapes = mesh_opening_shapes(pattern, cell=cell, angle=angle, width=width, size=size)
    if shapes is None:
        return None
    from .fabrication.mask import _rasterize

    return _rasterize(shapes, size)


def support_grid(stencil: Stencil, sep: Separation, *, pattern: str,
                 cell: float = 8.0, angle: float | None = None,
                 width: float | None = None, params: dict | None = None,
                 simplify: float = 1.0) -> Stencil:
    """Confine each layer's cut to a regular support **mesh** (returns cut polys).

    Think of a die / metal mesh laid over the design: a connected lattice of
    material with a hole at every pattern cell. The cut is intersected with the
    holes (``cut ∩ openings``), so a material wall ``width`` px wide always
    survives between neighbouring cells — the whole plate stays one connected
    piece and nothing falls out, while the cut inside each hole still follows the
    pattern (dot / hex size ∝ coverage).

    Defined for the regular-lattice screens (``dots`` / ``hexagons``); other
    patterns are returned unchanged. Opt-in; the default pipeline never calls it.
    """
    if pattern not in _MESH_PATTERNS:
        return stencil

    from .fabrication.mask import _rasterize, mask_to_polylines

    w, h = int(round(stencil.width)), int(round(stencil.height))
    layers = list(stencil.layers)
    total = len(sep)
    out = Stencil(width=stencil.width, height=stencil.height, units=stencil.units)
    for i, ch in enumerate(sep):
        a = angle if angle is not None else _angle_for(ch.name, i, total)
        layer = layers[i] if i < len(layers) else None
        cut = _rasterize(layer.primitives, (w, h)) if layer else np.zeros((h, w), bool)
        openings = mesh_openings(pattern, cell=cell, angle=a, width=width, size=(w, h))
        nl = out.layer(ch.name, color=ch.color)
        nl.add(mask_to_polylines(cut & openings, simplify=simplify))
    return out


def optimize_for_cutting(
    stencil: Stencil,
    *,
    min_hole_area: int = 4,
    min_island_area: int = 16,
    bridge_width: float = 2.0,
    min_feature_px: float = 2.0,
    simplify: float = 1.0,
) -> Stencil:
    """Make every layer fabrication-ready and return cut-polygon geometry.

    Each layer is rasterised to a :class:`StencilMask`, optimised (speckle
    filled, fragile islands removed, the rest bridged to the frame), and
    vectorised back to closed cut polygons (with holes).  This turns an artistic
    pattern into something a plotter can actually cut without pieces falling out.
    """
    from .fabrication import StencilMask, mask_to_polylines, optimize_mask

    size = (int(round(stencil.width)), int(round(stencil.height)))
    out = Stencil(width=stencil.width, height=stencil.height, units=stencil.units)
    for layer in stencil.layers:
        mask = StencilMask.from_layer(layer, size)
        opt, _ = optimize_mask(
            mask, min_hole_area=min_hole_area, min_island_area=min_island_area,
            bridge_width=bridge_width, min_feature_px=min_feature_px,
        )
        out.layer(layer.name, color=layer.color).add(
            mask_to_polylines(opt.cut, simplify=simplify)
        )
    return out


def halftone_stencil(
    image_path: str | Path,
    *,
    method: str = "cmyk",
    pattern: str = "dots",
    cell: float = 8.0,
    max_side: int | None = 1000,
    optimize: bool = True,
    carrier: bool = False,
    threshold: float = 0.5,
    duty: float = 0.5,
    min_feature_px: float = 2.0,
    bridge_width: float = 2.0,
    min_hole_area: int = 4,
    min_island_area: int = 16,
    angle: float | None = None,
    params: dict | None = None,
    strategy: str = "legacy",
) -> Stencil:
    """One-shot: load an image and produce a patterned, layered stencil.

    ``method`` selects the separation (``cmyk`` / ``rgb`` / ``grayscale`` /
    ``duotone`` / ``tritone``); ``pattern`` selects the screen.

    With ``carrier=True`` the ``pattern`` is used as a **threshold carrier**
    (cut = ``threshold ∩ pattern`` at density ``duty``) so the result
    self-bridges — the recommended way to use the *Experimental* screens.

    Because a stencil exists to be cut, the result is **optimised for cutting by
    default** — pieces that would fall out are bridged or removed and the
    geometry comes back as cut polygons.  Pass ``optimize=False`` for the raw
    artistic pattern instead.
    """
    from . import separation as sep_mod

    arr = load_image(image_path)
    if max_side is not None:
        arr = resize(arr, max_side=max_side)

    sep_fn = getattr(sep_mod, method, None)
    if sep_fn is None:
        raise ValueError(
            f"unknown separation method {method!r}; "
            "expected cmyk/rgb/grayscale/duotone/tritone"
        )
    # rgb/cmyk need colour; promote grayscale input to 3-channel so they work.
    if method in ("rgb", "cmyk") and arr.ndim == 2:
        arr = np.repeat(arr[..., None], 3, axis=-1)

    sep = sep_fn(arr)
    h, w = arr.shape[:2]
    if carrier:
        return carrier_stencil(
            sep, (w, h), carrier=pattern, threshold=threshold, duty=duty, cell=cell,
            optimize=optimize, min_hole_area=min_hole_area,
            min_island_area=min_island_area, bridge_width=bridge_width,
            min_feature_px=min_feature_px, angle=angle, params=params,
        )
    stencil = build_stencil(sep, (w, h), pattern=pattern, cell=cell,
                            angle=angle, params=params)
    if optimize:
        stencil = cut_ready(
            stencil, pattern, min_feature_px=min_feature_px,
            min_hole_area=min_hole_area, min_island_area=min_island_area,
            bridge_width=bridge_width, strategy=strategy,
        )
    return stencil
