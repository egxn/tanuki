"""tanuki.mori.stencil_lab — image → stencil pipeline.

Experimental toolkit that turns images into artistic stencil layers, halftones
and fabrication-ready vector patterns.  See ``mori/README.md`` for the full
vision; this package is built in phases.

Pipeline
────────
    Image → Adjustments → Colour Separation → Pattern → (Optimization) → Export

    load_image(path)                 # → float [0,1] numpy array
    adjustments.contrast(arr, 1.4)   # tweak tone
    sep = separation.cmyk(arr)       # → ink-coverage planes
    dots = halftone_dots(plane)      # → vector primitives
    stencil = build_stencil(...)     # → layered Stencil
    write_svg(stencil, "out.svg")    # → SVG

Phase 1 (current): image I/O, adjustments, separation (RGB/CMYK/gray/duo/tri),
dot halftone, geometry model, SVG export.
"""

from __future__ import annotations

from . import adjustments, fabrication, separation
from .fabrication import (
    CuttabilityReport,
    OptimizeReport,
    StencilMask,
    analyze_cuttability,
    detect_islands,
    fabrication_checks,
    optimize_mask,
)
from .geometry import Dot, Layer, Polyline, Stencil, polygon
from .image_io import (
    SUPPORTED_FORMATS,
    coverage,
    load_image,
    resize,
    save_image,
    to_grayscale,
)
from .patterns import (
    PATTERN_NAMES,
    PATTERNS,
    crosshatch,
    generate,
    halftone_circular,
    halftone_dots,
    halftone_lines,
    hexagons,
    honeycomb,
    radial,
    sine_wave,
    spiral,
    line_screen,
    splotches,
    stipple,
    threshold_lines,
    topographic,
    voronoi,
    zigzag,
)
from .separation import Channel, Separation
from .export import (
    render_png,
    to_blender_script,
    to_dxf,
    to_pdf,
    to_stl,
    to_svg,
    write_blender_script,
    write_dxf,
    write_pdf,
    write_png,
    write_stl,
    write_svg,
)
from .registration import (
    add_registration_marks,
    registration_marks,
    split_to_plates,
)
from .tiling import Tile, apply_frame, clip_to_rect, sheet_frame, tile_grid, tile_stencil
from .sizing import (
    PAPER,
    fit_to_physical,
    mm_to_px,
    paper_size,
    poster,
    px_for_print,
    px_to_mm,
    scale_stencil,
    sheets_needed,
    tile_to_paper,
)
from .pipeline import (
    build_stencil,
    carrier_mask,
    carrier_stencil,
    cut_cleanup,
    cut_grouped,
    cut_ready,
    halftone_stencil,
    merge_touching_shapes,
    mesh_openings,
    optimize_for_cutting,
    support_grid,
)

__all__ = [
    # submodules
    "adjustments",
    "separation",
    "fabrication",
    # fabrication (Phase 3)
    "StencilMask",
    "detect_islands",
    "fabrication_checks",
    "optimize_mask",
    "OptimizeReport",
    "analyze_cuttability",
    "CuttabilityReport",
    # image I/O
    "load_image",
    "save_image",
    "resize",
    "to_grayscale",
    "coverage",
    "SUPPORTED_FORMATS",
    # separation
    "Separation",
    "Channel",
    # geometry
    "Stencil",
    "Layer",
    "Dot",
    "Polyline",
    "polygon",
    # patterns
    "PATTERNS",
    "PATTERN_NAMES",
    "generate",
    "halftone_dots",
    "halftone_lines",
    "halftone_circular",
    "crosshatch",
    "sine_wave",
    "zigzag",
    "spiral",
    "radial",
    "hexagons",
    "honeycomb",
    "topographic",
    "stipple",
    "voronoi",
    "splotches",
    "threshold_lines",
    "line_screen",
    # export
    "to_svg",
    "write_svg",
    "to_blender_script",
    "write_blender_script",
    "render_png",
    "write_png",
    "to_dxf",
    "write_dxf",
    "to_pdf",
    "write_pdf",
    "to_stl",
    "write_stl",
    # registration / multi-layer
    "registration_marks",
    "add_registration_marks",
    "split_to_plates",
    # tiling / panelisation
    "Tile",
    "tile_stencil",
    "tile_grid",
    "clip_to_rect",
    "sheet_frame",
    "apply_frame",
    # physical sizing / printing on sheets
    "PAPER",
    "paper_size",
    "scale_stencil",
    "fit_to_physical",
    "tile_to_paper",
    "sheets_needed",
    "poster",
    "mm_to_px",
    "px_to_mm",
    "px_for_print",
    # pipeline
    "build_stencil",
    "halftone_stencil",
    "optimize_for_cutting",
    "cut_cleanup",
    "cut_ready",
    "cut_grouped",
    "merge_touching_shapes",
    "support_grid",
    "mesh_openings",
    "carrier_stencil",
    "carrier_mask",
]
