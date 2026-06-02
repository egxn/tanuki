"""registration.py
───────────────────
Registration marks, alignment guides and multi-layer plate handling.

When a design prints/cuts as several plates (one per ink, e.g. C, M, Y, K), the
plates must line up.  Registration marks are identical features placed on
*every* plate so they can be overlaid precisely.

* :func:`registration_marks` — build mark geometry for a canvas.
* :func:`add_registration_marks` — stamp the marks onto every layer in place.
* :func:`split_to_plates` — explode a stencil into one single-layer stencil per
  channel (each carrying the shared marks), ready to export/cut separately.
"""

from __future__ import annotations

import math
from dataclasses import replace

from .geometry import Layer, Polyline, Stencil

_MARK_COLOR = (0, 0, 0)


def _circle(cx: float, cy: float, r: float, width: float, *, res: int = 32) -> Polyline:
    pts = [
        (cx + r * math.cos(2 * math.pi * i / res),
         cy + r * math.sin(2 * math.pi * i / res))
        for i in range(res)
    ]
    return Polyline(points=pts, closed=True, width=width)


def _crosshair(cx: float, cy: float, s: float, width: float) -> list[Polyline]:
    return [
        Polyline([(cx - s, cy), (cx + s, cy)], width=width),
        Polyline([(cx, cy - s), (cx, cy + s)], width=width),
    ]


def _corner_tick(cx: float, cy: float, s: float, width: float,
                 sx: int, sy: int) -> Polyline:
    """L-shaped tick opening toward (sx, sy) ∈ {-1, +1}."""
    return Polyline([(cx + sx * s, cy), (cx, cy), (cx, cy + sy * s)], width=width)


def registration_marks(
    width: float,
    height: float,
    *,
    kind: str = "target",
    margin: float = 12.0,
    size: float = 8.0,
    line_width: float = 1.0,
) -> list[Polyline]:
    """Build registration mark geometry for a ``width`` × ``height`` canvas.

    ``kind`` ∈ ``{"crosshair", "target", "corner"}``.  Marks are placed at the
    four corners, inset by ``margin``.
    """
    corners = [
        (margin, margin, +1, +1),
        (width - margin, margin, -1, +1),
        (margin, height - margin, +1, -1),
        (width - margin, height - margin, -1, -1),
    ]
    marks: list[Polyline] = []
    for cx, cy, sx, sy in corners:
        if kind == "crosshair":
            marks.extend(_crosshair(cx, cy, size, line_width))
        elif kind == "target":
            marks.extend(_crosshair(cx, cy, size, line_width))
            marks.append(_circle(cx, cy, size * 0.6, line_width))
        elif kind == "corner":
            marks.append(_corner_tick(cx, cy, size, line_width, sx, sy))
        else:
            raise ValueError(f"unknown registration kind {kind!r}")
    return marks


def add_registration_marks(
    stencil: Stencil,
    *,
    kind: str = "target",
    margin: float = 12.0,
    size: float = 8.0,
    line_width: float = 1.0,
) -> Stencil:
    """Stamp registration marks onto **every** layer of ``stencil`` (in place).

    Marks go on each plate so the plates can be aligned; returns the stencil.
    """
    marks = registration_marks(
        stencil.width, stencil.height,
        kind=kind, margin=margin, size=size, line_width=line_width,
    )
    if not stencil.layers:
        stencil.layer("registration", color=_MARK_COLOR)
    for layer in stencil.layers:
        # fresh copies per layer so each plate owns its marks
        layer.add(replace(m) for m in marks)
    return stencil


def split_to_plates(
    stencil: Stencil,
    *,
    with_marks: bool = True,
    kind: str = "target",
    margin: float = 12.0,
    size: float = 8.0,
    line_width: float = 1.0,
) -> list[Stencil]:
    """Explode into one single-layer :class:`Stencil` per channel.

    Each plate optionally carries the shared registration marks so it can be
    printed / cut independently and re-aligned.
    """
    marks = (
        registration_marks(stencil.width, stencil.height, kind=kind,
                            margin=margin, size=size, line_width=line_width)
        if with_marks else []
    )
    plates: list[Stencil] = []
    for layer in stencil.layers:
        plate = Stencil(width=stencil.width, height=stencil.height, units=stencil.units)
        new_layer = Layer(name=layer.name, color=layer.color,
                          primitives=list(layer.primitives))
        new_layer.add(replace(m) for m in marks)
        plate.layers.append(new_layer)
        plates.append(plate)
    return plates
