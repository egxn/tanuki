"""tanuki.mori.stencil_lab.fabrication — Phase 3 stencil optimisation.

Turns a pattern into a fabrication-ready cut sheet:

    mask = StencilMask.from_stencil(stencil)     # vector → cut/material raster
    opt, report = optimize_mask(mask)            # clean + bridge + check
    print(report)                                # readiness summary
    cut = opt.to_stencil()                       # raster → cut polygons

Building blocks: island detection, automatic bridge generation, minimum feature
size control / reinforcement, and fabrication checks (``dict[str, list[str]]``,
empty list = passed, mirroring the halo_maps validators).
"""

from .mask import StencilMask, mask_to_polylines
from .islands import Island, add_bridges, detect_islands
from .features import (
    min_hole_diameter,
    remove_small_holes,
    remove_small_islands,
    thin_material,
)
from .checks import fabrication_checks, summarize
from .optimize import OptimizeReport, optimize_mask
from .cuttability import (
    AtRiskRegion,
    CuttabilityReport,
    analyze_cuttability,
    at_risk_material,
    island_mask,
    safe_material,
)

__all__ = [
    "StencilMask",
    "mask_to_polylines",
    "Island",
    "detect_islands",
    "add_bridges",
    "remove_small_holes",
    "remove_small_islands",
    "thin_material",
    "min_hole_diameter",
    "fabrication_checks",
    "summarize",
    "optimize_mask",
    "OptimizeReport",
    # cuttability analysis
    "analyze_cuttability",
    "CuttabilityReport",
    "AtRiskRegion",
    "safe_material",
    "at_risk_material",
    "island_mask",
]
