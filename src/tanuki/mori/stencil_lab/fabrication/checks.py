"""checks.py
────────────
Fabrication checks for a :class:`StencilMask`.

Mirrors the :mod:`halo_maps` validator convention: each check returns a list of
problem strings, and :func:`fabrication_checks` aggregates them into a
``dict[str, list[str]]`` where an **empty list means the check passed**::

    results = fabrication_checks(mask, min_feature_px=2.0)
    passed  = [k for k, v in results.items() if not v]
    failed  = {k: v for k, v in results.items() if v}
"""

from __future__ import annotations

import numpy as np

from .features import min_hole_diameter, thin_material
from .islands import detect_islands
from .mask import StencilMask


def check_islands(mask: StencilMask) -> list[str]:
    """Enclosed material islands fall out unless bridged."""
    islands = detect_islands(mask)
    if not islands:
        return []
    return [
        f"island #{isl.id} (area {isl.area}px) at "
        f"({isl.centroid[0]:.0f}, {isl.centroid[1]:.0f}) is unbridged"
        for isl in islands
    ]


def check_min_feature(mask: StencilMask, *, min_feature_px: float) -> list[str]:
    """Material slivers thinner than ``min_feature_px`` will tear."""
    thin = thin_material(mask, min_width=min_feature_px)
    count = int(thin.sum())
    if count == 0:
        return []
    frac = 100.0 * count / thin.size
    return [f"{count}px ({frac:.2f}%) of material is thinner than {min_feature_px}px"]


def check_min_hole(mask: StencilMask, *, min_feature_px: float) -> list[str]:
    """Holes smaller than the tool kerf won't cut cleanly."""
    if not mask.cut.any():
        return []
    d = min_hole_diameter(mask)
    if d >= min_feature_px:
        return []
    return [f"smallest hole diameter {d:.1f}px is below {min_feature_px}px"]


def check_has_material(mask: StencilMask) -> list[str]:
    """A sheet that is all-cut or all-material is not a usable stencil."""
    frac = float(mask.cut.mean())
    if frac >= 0.999:
        return ["sheet is entirely cut away (no material left)"]
    if frac <= 0.001:
        return ["sheet has no cut-outs (nothing to print)"]
    return []


def fabrication_checks(mask: StencilMask, *, min_feature_px: float = 2.0) -> dict[str, list[str]]:
    """Run all fabrication checks; empty list per key means it passed."""
    return {
        "has_material": check_has_material(mask),
        "islands": check_islands(mask),
        "min_feature": check_min_feature(mask, min_feature_px=min_feature_px),
        "min_hole": check_min_hole(mask, min_feature_px=min_feature_px),
    }


def summarize(results: dict[str, list[str]]) -> str:
    """Human-readable one-block summary of a checks dict."""
    lines = []
    for name, problems in results.items():
        if not problems:
            lines.append(f"  ✓ {name}")
        else:
            lines.append(f"  ✗ {name}: {len(problems)} issue(s)")
            lines.extend(f"      - {p}" for p in problems[:5])
            if len(problems) > 5:
                lines.append(f"      … and {len(problems) - 5} more")
    return "\n".join(lines)
