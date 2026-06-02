"""Exporters — serialise a :class:`~stencil_lab.geometry.Stencil` to a format.

* SVG — preview + vector-cutter ready (Phase 1).
* Blender — standalone ``bpy`` script building curves / extruded solids (Phase 4).
* PNG — composited colour raster preview (Phase 5).
* DXF — AutoCAD R12 ASCII, per-layer, for laser / vinyl cutters (Phase 5).
* PDF — single-page vector PDF (Phase 5).
* STL — extruded solid for 3-D printing (Phase 5).
"""

from .svg import to_svg, write_svg
from .blender import to_blender_script, write_blender_script
from .png import render_png, write_png
from .dxf import to_dxf, write_dxf
from .pdf import to_pdf, write_pdf
from .stl import to_stl, write_stl

__all__ = [
    "to_svg", "write_svg",
    "to_blender_script", "write_blender_script",
    "render_png", "write_png",
    "to_dxf", "write_dxf",
    "to_pdf", "write_pdf",
    "to_stl", "write_stl",
]
