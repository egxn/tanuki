"""tanuki.mori.bellows_diecut — 3D-printable matched dies for camera bellows.

Generates a male/female die pair that creases an origami fold pattern into
fabric.  Each pattern is one **unit cell** (single tile, no repetition yet —
tessellation comes later).  Following the README "Diecut Strategy", each die is a
flat plate with the fold edges extruded as triangular ridges (mountains, up) and
channels (valleys, down); the female is the negative.  The relief is built with
the **Tanuki Geometry Nodes DSL** (a cube plus boolean cuts) and the STL is baked
in **Blender**.  The ridge height is derived from the spacing between fold edges.

Quick start::

    from tanuki.mori.bellows_diecut import BellowsParams, generate_diecut

    params = BellowsParams(cell_scale=0.25)
    result = generate_diecut("yoshimura", params, "output", bake=True)  # needs Blender
    # result["paths"] → {'obj':…, 'svg':…, 'json':…, 'bpy':…, 'stl_male':…, 'stl_female':…}

Pipeline overview::

    patterns/<name>.generate(params)     →  FoldPattern  (one tile)
    core.diecut.build_graphs(...)        →  {male, female} Tanuki IR graphs
    core.exporter.export_all(..., bake)  →  OBJ/SVG/JSON + DSL script → STL (Blender)
"""

from __future__ import annotations

from pathlib import Path

from .parameters import BellowsParams
from .core.geometry import FoldPattern, FoldLine, FoldType
from .core import diecut, exporter, tessellate
from . import patterns

#: Patterns available as single unit cells (see README "Fold Patterns").
PATTERNS = ("yoshimura", "miura", "waterbomb", "kresling", "resch")


def generate_pattern(name: str, params: BellowsParams) -> FoldPattern:
    """Generate the unit-cell :class:`FoldPattern` for *name*."""
    return patterns.generate(name, params)


def generate_diecut(
    name: str,
    params: BellowsParams,
    output_dir: str | Path | None = None,
    bake: bool = False,
) -> dict:
    """Full pipeline: unit cell → DSL male/female dies → exported files.

    Parameters
    ----------
    name:
        Pattern key — one of :data:`PATTERNS`.
    params:
        A :class:`BellowsParams`.
    output_dir:
        Required for the die meshes: the foldcore OBJs, the flat OBJ/SVG/JSON
        and the self-contained DSL bake script ``<name>_diecut.py`` are written
        there.  When ``None`` only the :class:`FoldPattern` is returned.
    bake:
        If ``True`` (and Blender is on PATH), run the bake script to produce
        ``stl/<name>_{male,female}.stl``.

    Returns
    -------
    dict
        ``{"pattern": FoldPattern, "graphs": {male, female}, "paths": {...}}``.
        ``graphs`` / ``paths`` are empty when *output_dir* is ``None``.
    """
    from pathlib import Path

    pattern = generate_pattern(name, params)
    if output_dir is None:
        return {"pattern": pattern, "graphs": {}, "paths": {}}

    graphs = diecut.build_graphs(pattern, params, Path(output_dir) / "mesh")
    paths = exporter.export_all(
        pattern, params, output_dir, graphs=graphs, bake=bake
    )
    return {"pattern": pattern, "graphs": graphs, "paths": paths}


def generate_tessellation(
    name: str,
    output_dir: str | Path | None = None,
    bake: bool = False,
    tile: tuple[float, float] | None = None,
    grid: tuple[int, int] | None = None,
    base_thickness: float = 3.0,
) -> dict:
    """Tile *name* across the print bed and build the folded male/female dies.

    Uses the README "Tile Specifications" (size ``tile_X × tile_Y`` mm, grid
    ``n × m``, fold depth ``Z = tile_Y/2 − 0.8``) unless *tile* / *grid* override
    them.  See :func:`generate_diecut` for *output_dir* / *bake* semantics.
    """
    pattern = tessellate.tessellate(name, tile=tile, grid=grid)
    params = tessellate.tile_params(name, base_thickness=base_thickness)
    if output_dir is None:
        return {"pattern": pattern, "params": params, "graphs": {}, "paths": {}}

    graphs = diecut.build_graphs(pattern, params, Path(output_dir) / "mesh")
    paths = exporter.export_all(
        pattern, params, output_dir, graphs=graphs, bake=bake
    )
    return {"pattern": pattern, "params": params, "graphs": graphs, "paths": paths}


__all__ = [
    "BellowsParams",
    "FoldPattern", "FoldLine", "FoldType",
    "diecut", "exporter", "patterns", "tessellate",
    "PATTERNS",
    "generate_pattern", "generate_diecut", "generate_tessellation",
]
