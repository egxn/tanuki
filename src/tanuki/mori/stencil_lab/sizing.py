"""sizing.py
───────────
Physical size — print a design at a real-world scale, on one sheet or many.

The geometry is vector, so "size" is just a scale factor: :func:`scale_stencil`
multiplies every coordinate so the stencil *measures* in millimetres, and the
exporters then write real dimensions (SVG `mm`, DXF units, PDF points).

Workflow
────────
    st = sl.halftone_stencil("photo.jpg", cell=6)        # pixels
    st = fit_to_physical(st, width_mm=700)               # → 70 cm wide, mm units
    sl.write_svg(st, "poster.svg")                       # prints at 70 cm

Bigger than the printer?  Split it across sheets (A4 … A0, carta, **pliego**):

    tiles = tile_to_paper(st, "A3", margin_mm=10, overlap_mm=10)
    for t in tiles:
        sl.write_pdf(t.stencil, f"sheet_{t.name}.pdf")

Resolution (DPI) is decoupled from size: generate the screen at whatever pixel
``max_side`` / ``cell`` gives the dot pitch you want, *then* scale to physical
size.  :func:`px_for_print` helps pick a pixel size for a target DPI.
"""

from __future__ import annotations

import math

from .geometry import Dot, Polyline, Stencil
from .tiling import Tile, tile_grid, tile_stencil

MM_PER_IN = 25.4

# Paper sizes in millimetres (portrait, width × height).
PAPER: dict[str, tuple[float, float]] = {
    "a0": (841, 1189), "a1": (594, 841), "a2": (420, 594), "a3": (297, 420),
    "a4": (210, 297), "a5": (148, 210), "a6": (105, 148),
    "letter": (215.9, 279.4), "carta": (215.9, 279.4),
    "legal": (215.9, 355.6), "tabloid": (279.4, 431.8), "oficio": (216, 340),
    # Latin-American "pliego" and its fractions
    "pliego": (700, 1000), "medio_pliego": (500, 700), "cuarto_pliego": (350, 500),
    "cricut": (300, 300)
}


# ─── unit helpers ──────────────────────────────────────────────────────────────

def mm_to_px(mm: float, dpi: float) -> float:
    return mm * dpi / MM_PER_IN


def px_to_mm(px: float, dpi: float) -> float:
    return px * MM_PER_IN / dpi


def px_for_print(longest_mm: float, dpi: float = 150.0) -> int:
    """Pixel ``max_side`` to screen a design ``longest_mm`` long at ``dpi``."""
    return max(1, int(round(mm_to_px(longest_mm, dpi))))


def paper_size(name: str, *, landscape: bool = False) -> tuple[float, float]:
    """Look up a paper size in mm; ``landscape`` swaps width/height."""
    try:
        w, h = PAPER[name.lower()]
    except KeyError:
        raise ValueError(
            f"unknown paper {name!r}; choose from {', '.join(sorted(PAPER))}"
        ) from None
    return (h, w) if landscape else (w, h)


# ─── scaling ────────────────────────────────────────────────────────────────

def _scale_prim(prim, f: float):
    if isinstance(prim, Dot):
        return Dot(prim.x * f, prim.y * f, prim.r * f)
    return Polyline(
        points=[(x * f, y * f) for x, y in prim.points],
        closed=prim.closed, width=prim.width * f, fill=prim.fill,
        holes=[[(x * f, y * f) for x, y in h] for h in prim.holes],
    )


def scale_stencil(stencil: Stencil, factor: float, *, units: str | None = None) -> Stencil:
    """Return a copy with every coordinate multiplied by ``factor``."""
    out = Stencil(width=stencil.width * factor, height=stencil.height * factor,
                  units=units or stencil.units)
    for layer in stencil.layers:
        out.layer(layer.name, color=layer.color).add(
            _scale_prim(p, factor) for p in layer.primitives
        )
    return out


def fit_to_physical(stencil: Stencil, *, width_mm: float | None = None,
                    height_mm: float | None = None) -> Stencil:
    """Scale a (pixel) stencil to a physical size in mm, keeping aspect ratio.

    Give ``width_mm`` and/or ``height_mm``; with both, the design is scaled to
    fit *within* the box.  Result has ``units="mm"``.
    """
    if not width_mm and not height_mm:
        raise ValueError("give width_mm and/or height_mm")
    fx = width_mm / stencil.width if width_mm else math.inf
    fy = height_mm / stencil.height if height_mm else math.inf
    return scale_stencil(stencil, min(fx, fy), units="mm")


# ─── paper tiling (poster mode) ─────────────────────────────────────────────

def printable_area(paper: str, *, landscape: bool = False,
                    margin_mm: float = 10.0) -> tuple[float, float]:
    """Usable area of a sheet after subtracting margins (mm)."""
    pw, ph = paper_size(paper, landscape=landscape)
    return (pw - 2 * margin_mm, ph - 2 * margin_mm)


def sheets_needed(stencil: Stencil, paper: str, *, landscape: bool = False,
                  margin_mm: float = 10.0, overlap_mm: float = 10.0) -> tuple[int, int]:
    """How many sheets ``(cols, rows)`` a physical (mm) stencil needs."""
    bw, bh = printable_area(paper, landscape=landscape, margin_mm=margin_mm)
    grid = tile_grid(stencil.width, stencil.height, bw, bh, overlap=overlap_mm)
    return (len(grid[0]) if grid else 0, len(grid))


def tile_to_paper(stencil: Stencil, paper: str = "a4", *, landscape: bool = False,
                  margin_mm: float = 10.0, overlap_mm: float = 10.0,
                  crop_marks: bool = True, full: bool = True,
                  skip_empty: bool = True, frame_mm: float = 0.0,
                  frame_width_mm: float = 0.0) -> list[Tile]:
    """Split a physical (mm) stencil onto sheets of ``paper``.

    Tiles to the sheet's printable area (size − margins), with ``overlap_mm`` of
    shared margin and corner crop marks for re-alignment.  Each tile's stencil
    is in mm, ready to print/cut at 1:1.

    ``frame_mm`` > 0 clears that many millimetres of margin around each sheet
    (clipping artwork out of it, e.g. ``10`` = a 1 cm margin); ``frame_width_mm``
    > 0 also draws a visible border outline (which the cutter *will* cut, so it
    defaults to 0 — just the clear margin).

    By default every sheet is a **full, uniform printable page** (``full``) and
    **blank sheets are dropped** (``skip_empty``) — so you don't get tiny edge
    tiles or empty pages for inks that aren't present in a region.
    """
    bw, bh = printable_area(paper, landscape=landscape, margin_mm=margin_mm)
    return tile_stencil(stencil, bw, bh, overlap=overlap_mm, crop_marks=crop_marks,
                        frame=frame_mm, frame_width=frame_width_mm,
                        full=full, skip_empty=skip_empty)


def poster(stencil: Stencil, paper: str = "a4", *, width_mm: float | None = None,
           cols: int | None = None, landscape: bool = False,
           margin_mm: float = 10.0, overlap_mm: float = 10.0,
           crop_marks: bool = True, frame_mm: float = 0.0) -> tuple[Stencil, list[Tile]]:
    """One call: size a design and split it across ``paper`` sheets.

    Choose the physical width by ``width_mm`` directly, or by ``cols`` (number of
    sheets across); defaults to a single sheet width.  ``frame_mm`` > 0 adds a
    per-sheet border (see :func:`tile_to_paper`).  Returns
    ``(scaled_stencil_mm, tiles)``.
    """
    bw, bh = printable_area(paper, landscape=landscape, margin_mm=margin_mm)
    if width_mm is None:
        n = max(1, cols or 1)
        width_mm = n * bw - (n - 1) * overlap_mm     # n sheets across, minus overlaps
    scaled = fit_to_physical(stencil, width_mm=width_mm)
    tiles = tile_to_paper(scaled, paper, landscape=landscape, margin_mm=margin_mm,
                          overlap_mm=overlap_mm, crop_marks=crop_marks, frame_mm=frame_mm)
    return scaled, tiles
