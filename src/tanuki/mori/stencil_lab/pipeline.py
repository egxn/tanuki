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

from .geometry import Stencil
from .image_io import load_image, resize
from .patterns import generate
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
) -> Stencil:
    """Render every channel of a :class:`Separation` into a layered stencil.

    ``size`` is ``(width, height)`` in pixels (matching the coverage planes).
    ``pattern`` selects a generator from :data:`patterns.PATTERNS` (``dots``,
    ``lines``, ``circular``, ``crosshatch``, ``sine``, ``spiral``, ``hexagons``,
    ``topographic``, ``stipple``, …); per-channel screen angles are applied for
    the angle-aware patterns.
    """
    w, h = size
    stencil = Stencil(width=float(w), height=float(h), units=units)
    total = len(sep)
    for i, ch in enumerate(sep):
        angle = _angle_for(ch.name, i, total)
        prims = generate(ch.plane, pattern, cell=cell, angle=angle)
        layer = stencil.layer(ch.name, color=ch.color)
        layer.add(prims)
    return stencil


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
    min_feature_px: float = 2.0,
    bridge_width: float = 2.0,
    min_hole_area: int = 4,
    min_island_area: int = 16,
) -> Stencil:
    """One-shot: load an image and produce a patterned, layered stencil.

    ``method`` selects the separation (``cmyk`` / ``rgb`` / ``grayscale`` /
    ``duotone`` / ``tritone``); ``pattern`` selects the screen.

    Because a stencil exists to be cut, the result is **optimised for cutting by
    default** (:func:`optimize_for_cutting`) — pieces that would fall out are
    bridged or removed and the geometry comes back as cut polygons.  Pass
    ``optimize=False`` for the raw artistic pattern instead.
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
    stencil = build_stencil(sep, (w, h), pattern=pattern, cell=cell)
    if optimize:
        stencil = optimize_for_cutting(
            stencil, min_hole_area=min_hole_area, min_island_area=min_island_area,
            bridge_width=bridge_width, min_feature_px=min_feature_px,
        )
    return stencil
