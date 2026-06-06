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

# Each adapter accepts (and ignores) ``**params`` so callers can pass
# generator-specific knobs (e.g. ``line_screen``'s ``max_duty`` / ``wave_*``)
# through the uniform interface; only the generators that understand them
# forward the extras.
PATTERNS: dict[str, PatternFn] = {
    "dots": lambda p, *, cell, angle, **kw: halftone_dots(p, cell=cell, angle=angle),
    "lines": lambda p, *, cell, angle, **kw: halftone_lines(p, spacing=cell, angle=angle),
    "circular": lambda p, *, cell, angle, **kw: halftone_circular(p, spacing=cell),
    "crosshatch": lambda p, *, cell, angle, **kw: crosshatch(p, spacing=cell),
    "sine": lambda p, *, cell, angle, **kw: sine_wave(p, spacing=cell),
    "zigzag": lambda p, *, cell, angle, **kw: zigzag(p, spacing=cell),
    "spiral": lambda p, *, cell, angle, **kw: spiral(p, spacing=cell),
    "radial": lambda p, *, cell, angle, **kw: radial(p, spacing=cell),
    "hexagons": lambda p, *, cell, angle, **kw: hexagons(p, cell=cell),
    "honeycomb": lambda p, *, cell, angle, **kw: honeycomb(p, cell=cell),
    "topographic": lambda p, *, cell, angle, **kw: topographic(p, cell=cell),
    "stipple": lambda p, *, cell, angle, **kw: stipple(p, cell=cell),
    "voronoi": lambda p, *, cell, angle, **kw: voronoi(p, spacing=cell),
    "splotches": lambda p, *, cell, angle, **kw: splotches(p, cell=cell),
    "threshold_lines": lambda p, *, cell, angle, **kw: threshold_lines(p, period=cell, angle=angle),
    "line_screen": lambda p, *, cell, angle, **kw: line_screen(p, period=cell, angle=angle, **kw),
}

PATTERN_NAMES = tuple(PATTERNS)

# ─── grouping by usefulness for cut stencils ────────────────────────────────
# These fill an *area* modulated by coverage, so they read as a proper stencil
# and optimise cleanly — the recommended starting points.
PRIMARY_PATTERNS = ("dots", "hexagons", "line_screen", "splotches")
# Threshold ∩ carrier: cuts only inside the dark regions, leaving the gaps as a
# connected material lattice → self-bridging (always cuttable). See README.
CARRIER_PATTERNS = ("threshold_lines",)
# Stroke / cell / contour screens. On their own they leave fragile thin webs;
# they shine when used as *carriers* (threshold ∩ pattern) — see PATTERN_GROUPS.
EXPERIMENTAL_PATTERNS = tuple(
    n for n in PATTERN_NAMES if n not in PRIMARY_PATTERNS + CARRIER_PATTERNS
)
PATTERN_GROUPS = (
    ("Recommended", PRIMARY_PATTERNS),
    ("Self-bridging (threshold carrier)", CARRIER_PATTERNS),
    ("Experimental — better as carriers", EXPERIMENTAL_PATTERNS),
)


def generate(plane: np.ndarray, pattern: str, *, cell: float = 8.0,
             angle: float = 0.0, **params) -> list[Primitive]:
    """Run a registered pattern by name via the uniform interface.

    Extra ``**params`` are forwarded to the underlying generator (e.g.
    ``max_duty`` / ``wave_amplitude`` / ``wave_length`` for ``line_screen``);
    generators that don't take them simply ignore the extras.
    """
    try:
        fn = PATTERNS[pattern]
    except KeyError:
        raise ValueError(
            f"unknown pattern {pattern!r}; choose from {', '.join(PATTERN_NAMES)}"
        ) from None
    return fn(plane, cell=cell, angle=angle, **params)


__all__ = [
    "PATTERNS",
    "PATTERN_NAMES",
    "PRIMARY_PATTERNS",
    "CARRIER_PATTERNS",
    "EXPERIMENTAL_PATTERNS",
    "PATTERN_GROUPS",
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
