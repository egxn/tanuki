"""Bellows Diecut — core geometry, foldcore dies, and exporters."""

from .geometry import (
    Point2, Edge, FoldType, FoldLine, FoldPattern,
    cell_from_edges, edge_spacing, relief_dims, merge_collinear,
)
from . import foldcore, tessellate
from .foldcore import build_surface, build_die, fold_amplitude
from .tessellate import TILE_SPECS, tile_depth, tessellated_size
from .diecut import build_graphs
from .exporter import (
    export_bpy_script, bake_and_export_stl, bake_molds,
    export_obj, export_svg, export_json, export_all,
)

__all__ = [
    "Point2", "Edge", "FoldType", "FoldLine", "FoldPattern",
    "cell_from_edges", "edge_spacing", "relief_dims", "merge_collinear",
    "foldcore", "build_surface", "build_die", "fold_amplitude",
    "tessellate", "TILE_SPECS", "tile_depth", "tessellated_size",
    "build_graphs",
    "export_bpy_script", "bake_and_export_stl", "bake_molds",
    "export_obj", "export_svg", "export_json", "export_all",
]
