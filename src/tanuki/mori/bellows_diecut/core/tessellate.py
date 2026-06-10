"""Tessellation — repeat a unit cell into a print-bed-sized fold pattern.

Each pattern's unit cell is stretched to its tile ``X × Y`` (mm) and replicated
on an ``n × m`` grid per the README "Tile Specifications — 35mm Bellows"
("Adjusted for 170×170 bed" table).  The fold depth follows the README:

    Z = tile_Y / 2 − fabric_thickness − press_tolerance
      = tile_Y / 2 − 0.8

The result is one big :class:`FoldPattern` that ``core.foldcore`` turns into the
folded male/female dies.
"""

from __future__ import annotations

from ..parameters import BellowsParams
from .geometry import FoldPattern, FoldType
from .. import patterns

#: Print-bed and fabric constants (README "Base Parameters").
PRINT_BED = 170.0        # mm (square)
FABRIC_THICKNESS = 0.5   # mm
PRESS_TOLERANCE = 0.3    # mm

#: Per-pattern tile size (mm), grid, and how the cells repeat:
#: - ``square``: plain grid (Resch, Waterbomb);
#: - ``brick``:  alternate rows shifted ½ tile (Miura, Yoshimura — a row's tile
#:   corners land on the next row's tile centres);
#: - ``pitch_x``: horizontal pitch as a fraction of the tile (Kresling's V notch
#:   interlocks with its neighbour, reducing the effective width — 260/300).
TILE_SPECS: dict[str, dict] = {
    "yoshimura": {"tile": (16.0, 14.0), "grid": (8, 12), "tiling": "brick"},
    "miura":     {"tile": (16.0, 17.0), "grid": (8, 10), "tiling": "brick"},
    "waterbomb": {"tile": (16.0, 15.0), "grid": (8, 11), "tiling": "square"},
    "kresling":  {"tile": (18.0, 12.0), "grid": (7, 14), "tiling": "square",
                  "pitch_x": 260.0 / 300.0},
    "resch":     {"tile": (20.0, 10.0), "grid": (6, 17), "tiling": "square"},
}


def tile_depth(tile_y: float) -> float:
    """Fold-ridge depth Z (mm) for a tile of pitch *tile_y* (mm)."""
    return tile_y / 2.0 - FABRIC_THICKNESS - PRESS_TOLERANCE


def tessellate(
    name: str,
    tile: tuple[float, float] | None = None,
    grid: tuple[int, int] | None = None,
) -> FoldPattern:
    """Build the tessellated :class:`FoldPattern` for *name*.

    The unit cell is normalised to a unit square and repeated on the grid, each
    copy scaled to ``tile_X × tile_Y`` (mm) and placed per the pattern's tiling
    rule (square / brick / V-interlock) so the fold lines of adjacent tiles meet.
    """
    spec = TILE_SPECS[name]
    tx, ty = tile or spec["tile"]
    n, m = grid or spec["grid"]
    tiling = spec.get("tiling", "square")
    pitch_x = spec.get("pitch_x", 1.0) * tx       # horizontal step between columns

    cell = patterns.generate(name, BellowsParams(cell_scale=1.0))
    cw = max(cell.width, 1e-9)
    ch = max(cell.height, 1e-9)

    def row_shift(j: int) -> float:
        return (j % 2) * 0.5 * pitch_x if tiling == "brick" else 0.0

    folds: list[tuple[tuple, tuple, FoldType]] = []
    for j in range(m):
        oy = j * ty
        ox0 = row_shift(j)
        for i in range(n):
            ox = ox0 + i * pitch_x
            for kind, lines in ((FoldType.MOUNTAIN, cell.mountains),
                                (FoldType.VALLEY, cell.valleys)):
                for fl in lines:
                    a = (ox + fl.p0[0] / cw * tx, oy + fl.p0[1] / ch * ty)
                    b = (ox + fl.p1[0] / cw * tx, oy + fl.p1[1] / ch * ty)
                    folds.append((a, b, kind))

    xs = [p[0] for a, b, _ in folds for p in (a, b)]
    ys = [p[1] for a, b, _ in folds for p in (a, b)]
    pat = FoldPattern(name=f"{name}_tile",
                      width=max(xs) - min(xs), height=max(ys) - min(ys),
                      seam=False)
    for a, b, kind in folds:
        pat.add_fold(a, b, kind)
    pat.add_outline()
    return pat


def tessellated_size(name: str) -> tuple[float, float]:
    """Total ``(width, height)`` (mm) covered by the tessellation."""
    x0, y0, x1, y1 = tessellate(name).bounds()
    return x1 - x0, y1 - y0


def tile_params(name: str, base_thickness: float = 3.0) -> BellowsParams:
    """``BellowsParams`` for the tessellated die — fold depth + fabric gap from
    the README spec."""
    _tx, ty = TILE_SPECS[name]["tile"]
    return BellowsParams(
        material_thickness=FABRIC_THICKNESS,
        ridge_height=tile_depth(ty),
        base_thickness=base_thickness,
    )


__all__ = [
    "TILE_SPECS", "PRINT_BED", "FABRIC_THICKNESS", "PRESS_TOLERANCE",
    "tile_depth", "tessellated_size", "tessellate", "tile_params",
]
