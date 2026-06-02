"""features.py
──────────────
Minimum-feature-size control and structural reinforcement.

Tiny features are the enemy of fabrication: a hole smaller than the laser kerf
won't cut cleanly, a material sliver thinner than the bit will tear. These
helpers clean and measure such features on a :class:`StencilMask`.

* :func:`remove_small_holes`   — fill cut blobs below an area (speckle removal).
* :func:`remove_small_islands` — drop fragile enclosed material below an area.
* :func:`thin_material`        — mask of material thinner than a width.
* :func:`min_hole_diameter`    — smallest hole diameter present (px).
"""

from __future__ import annotations

import numpy as np

from .islands import _border_labels
from .mask import StencilMask

_S8 = np.ones((3, 3), int)


def remove_small_holes(mask: StencilMask, *, min_area: int) -> tuple[StencilMask, int]:
    """Fill cut components smaller than ``min_area`` px with material.

    Returns ``(new_mask, n_removed)``.
    """
    from scipy import ndimage

    labels, n = ndimage.label(mask.cut, structure=_S8)
    if n == 0:
        return mask.copy(), 0
    areas = ndimage.sum_labels(np.ones_like(labels), labels, index=range(1, n + 1))
    small = {i + 1 for i, a in enumerate(areas) if a < min_area}
    if not small:
        return mask.copy(), 0
    out = mask.copy()
    out.cut[np.isin(labels, list(small))] = False
    return out, len(small)


def remove_small_islands(mask: StencilMask, *, min_area: int) -> tuple[StencilMask, int]:
    """Remove enclosed material islands smaller than ``min_area`` px (→ cut).

    These are too fragile to bridge; cutting them away is cleaner.
    Returns ``(new_mask, n_removed)``.
    """
    from scipy import ndimage

    labels, n = ndimage.label(mask.material, structure=_S8)
    if n == 0:
        return mask.copy(), 0
    safe = _border_labels(labels)
    areas = ndimage.sum_labels(np.ones_like(labels), labels, index=range(1, n + 1))
    small = {
        i + 1 for i, a in enumerate(areas)
        if (i + 1) not in safe and a < min_area
    }
    if not small:
        return mask.copy(), 0
    out = mask.copy()
    out.cut[np.isin(labels, list(small))] = True
    return out, len(small)


def thin_material(mask: StencilMask, *, min_width: float) -> np.ndarray:
    """Boolean mask of material regions thinner than ``min_width`` px.

    Found by eroding the material by ``min_width / 2`` and seeing what survives;
    anything in the original material but not in the eroded-then-dilated set was
    part of a too-thin feature.
    """
    from scipy import ndimage

    r = max(1, int(round(min_width / 2.0)))
    mat = mask.material
    # border_value=1: treat the sheet edge as solid material so the physical
    # outer boundary (and its convex corners) isn't mistaken for a thin feature.
    eroded = ndimage.binary_erosion(mat, iterations=r, border_value=1)
    reopened = ndimage.binary_dilation(eroded, iterations=r)
    return mat & ~reopened


def min_hole_diameter(mask: StencilMask) -> float:
    """Diameter (px) of the smallest cut feature, via its max inscribed circle."""
    from scipy import ndimage

    if not mask.cut.any():
        return 0.0
    labels, n = ndimage.label(mask.cut, structure=_S8)
    dist = ndimage.distance_transform_edt(mask.cut)
    # Per-component peak distance ≈ inscribed radius.
    peaks = ndimage.maximum(dist, labels, index=range(1, n + 1))
    return float(2.0 * np.min(peaks))
