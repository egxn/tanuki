"""Pattern generators — turn ink-coverage planes into vector geometry.

Every generator takes a coverage plane ``(H, W)`` in [0, 1] and returns a list
of :mod:`stencil_lab.geometry` primitives in image pixel coordinates.

Two ways to use them:

* Call a generator directly with its full parameter set (see each function).
* Use the :data:`PATTERNS` registry for a uniform ``(plane, *, cell, angle)``
  interface — this is what the pipeline / CLI dispatch on.

    >>> from tanuki.mori.stencil_lab.patterns import PATTERNS
    >>> prims = PATTERNS["sine"](plane, cell=10, angle=0)
"""

from __future__ import annotations

from typing import Callable

import numpy as np

from ..geometry import Primitive
from .halftone import crosshatch, halftone_circular, halftone_dots, halftone_lines
from .experimental import (
    hexagons,
    honeycomb,
    line_screen,
    radial,
    sine_wave,
    spiral,
    splotches,
    stipple,
    threshold_lines,
    topographic,
    voronoi,
    zigzag,
)

# Uniform adapter signature: (plane, *, cell, angle) -> list[Primitive].
# Each adapter maps the generic ``cell`` knob onto each generator's natural
# scale parameter and applies ``angle`` only where it is meaningful.
PatternFn = Callable[..., list[Primitive]]

PATTERNS: dict[str, PatternFn] = {
    "dots": lambda p, *, cell, angle: halftone_dots(p, cell=cell, angle=angle),
    "lines": lambda p, *, cell, angle: halftone_lines(p, spacing=cell, angle=angle),
    "circular": lambda p, *, cell, angle: halftone_circular(p, spacing=cell),
    "crosshatch": lambda p, *, cell, angle: crosshatch(p, spacing=cell),
    "sine": lambda p, *, cell, angle: sine_wave(p, spacing=cell),
    "zigzag": lambda p, *, cell, angle: zigzag(p, spacing=cell),
    "spiral": lambda p, *, cell, angle: spiral(p, spacing=cell),
    "radial": lambda p, *, cell, angle: radial(p, spacing=cell),
    "hexagons": lambda p, *, cell, angle: hexagons(p, cell=cell),
    "honeycomb": lambda p, *, cell, angle: honeycomb(p, cell=cell),
    "topographic": lambda p, *, cell, angle: topographic(p, cell=cell),
    "stipple": lambda p, *, cell, angle: stipple(p, cell=cell),
    "voronoi": lambda p, *, cell, angle: voronoi(p, spacing=cell),
    "splotches": lambda p, *, cell, angle: splotches(p, cell=cell),
    "threshold_lines": lambda p, *, cell, angle: threshold_lines(p, period=cell, angle=angle),
    "line_screen": lambda p, *, cell, angle: line_screen(p, period=cell, angle=angle),
}

PATTERN_NAMES = tuple(PATTERNS)


def generate(plane: np.ndarray, pattern: str, *, cell: float = 8.0,
             angle: float = 0.0) -> list[Primitive]:
    """Run a registered pattern by name via the uniform interface."""
    try:
        fn = PATTERNS[pattern]
    except KeyError:
        raise ValueError(
            f"unknown pattern {pattern!r}; choose from {', '.join(PATTERN_NAMES)}"
        ) from None
    return fn(plane, cell=cell, angle=angle)


__all__ = [
    "PATTERNS",
    "PATTERN_NAMES",
    "generate",
    # traditional
    "halftone_dots",
    "halftone_lines",
    "halftone_circular",
    "crosshatch",
    # experimental
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
]
