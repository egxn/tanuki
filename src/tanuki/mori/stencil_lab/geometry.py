"""geometry.py
────────────
Backend-neutral vector geometry for the Stencil Lab.

The whole stencil pipeline (image → separation → pattern → optimization →
export) speaks a single, tiny vocabulary of 2-D primitives that any backend
(SVG, DXF, the Tanuki Blender DSL, …) can consume.  Nothing here knows about
PIL, numpy, or Blender — it is pure data.

Coordinate system
─────────────────
* Origin at the top-left corner, ``x`` grows right, ``y`` grows down.
  This matches image pixel space, so a pattern can be authored directly in the
  pixel coordinates of the source image and only the exporters need to worry
  about flipping for formats that use a bottom-left origin.
* Units are abstract.  ``Stencil.width`` / ``height`` carry an optional
  ``units`` label ("mm", "px", …) so exporters can annotate output.

Primitives
──────────
  ``Dot``      — filled circle (halftone dot, drill mark).
  ``Polyline`` — open or closed chain of points; ``width`` gives stroke weight,
                 ``fill`` marks it as a solid region (a polygon).
  ``Layer``    — a named collection of primitives sharing one ink colour.
  ``Stencil``  — an ordered stack of layers + the canvas dimensions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Sequence

Point = tuple[float, float]


# ─── Primitives ────────────────────────────────────────────────────────────────

@dataclass(slots=True)
class Dot:
    """A filled circle of radius ``r`` centred at ``(x, y)``."""

    x: float
    y: float
    r: float

    def bbox(self) -> tuple[float, float, float, float]:
        return (self.x - self.r, self.y - self.r, self.x + self.r, self.y + self.r)


@dataclass(slots=True)
class Polyline:
    """A chain of points.

    ``closed``  — join the last point back to the first.
    ``width``   — stroke weight (ignored when ``fill`` is True).
    ``fill``    — render as a solid filled polygon rather than a stroked path.
    ``holes``   — inner rings cut out of a filled polygon (even-odd fill); each
                  is its own closed list of points. Only meaningful when
                  ``fill`` is True. Empty for ordinary polylines.
    """

    points: list[Point]
    closed: bool = False
    width: float = 1.0
    fill: bool = False
    holes: list[list[Point]] = field(default_factory=list)

    def bbox(self) -> tuple[float, float, float, float]:
        xs = [p[0] for p in self.points]
        ys = [p[1] for p in self.points]
        return (min(xs), min(ys), max(xs), max(ys))


Primitive = Dot | Polyline


# ─── Layer & Stencil ─────────────────────────────────────────────────────────

@dataclass(slots=True)
class Layer:
    """A named set of primitives sharing one ink colour.

    ``color`` is an ``(r, g, b)`` triple in the 0–255 range, used by exporters
    for preview/fill.  ``name`` typically matches a separation channel
    ("cyan", "key", "red", …).
    """

    name: str
    primitives: list[Primitive] = field(default_factory=list)
    color: tuple[int, int, int] = (0, 0, 0)

    def add(self, prim: Primitive | Iterable[Primitive]) -> None:
        if isinstance(prim, (Dot, Polyline)):
            self.primitives.append(prim)
        else:
            self.primitives.extend(prim)

    def __len__(self) -> int:
        return len(self.primitives)


@dataclass(slots=True)
class Stencil:
    """An ordered stack of layers over a fixed canvas.

    Layers are drawn in list order (index 0 first / bottom).  For CMYK work the
    conventional order is C, M, Y, K so the key plate prints last/on top.
    """

    width: float
    height: float
    layers: list[Layer] = field(default_factory=list)
    units: str = "px"

    def layer(self, name: str, color: tuple[int, int, int] = (0, 0, 0)) -> Layer:
        """Get an existing layer by name or create and append a new one."""
        for layer in self.layers:
            if layer.name == name:
                return layer
        layer = Layer(name=name, color=color)
        self.layers.append(layer)
        return layer

    @property
    def primitive_count(self) -> int:
        return sum(len(layer) for layer in self.layers)


# ─── Helpers ──────────────────────────────────────────────────────────────────

def polygon(points: Sequence[Point], width: float = 1.0,
            holes: Sequence[Sequence[Point]] | None = None) -> Polyline:
    """Convenience constructor for a closed, filled polygon (optionally holed)."""
    return Polyline(
        points=list(points), closed=True, width=width, fill=True,
        holes=[list(h) for h in holes] if holes else [],
    )
