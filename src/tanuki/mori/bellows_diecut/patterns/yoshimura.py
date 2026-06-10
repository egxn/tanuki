"""Yoshimura unit cell.

V shape with a downward peak on top, a diamond below.  The two lateral columns
and the central diamond axis are valleys; every diagonal arm is a mountain.
Geometry transcribed from the SVG reference in ``README.md``.
"""

from __future__ import annotations

from ..parameters import BellowsParams
from ..core.geometry import cell_from_edges, FoldPattern

# Diagonal arms — mountain.
_MOUNTAIN = [
    (220, 75, 340, 135), (460, 75, 340, 135),     # top V → downward peak
    (340, 135, 220, 195), (340, 135, 460, 195),    # diamond upper arms
    (220, 195, 340, 255), (460, 195, 340, 255),    # diamond lower arms
]
# Lateral columns + central diamond axis — valley.
_VALLEY = [
    (220, 75, 220, 195), (460, 75, 460, 195),      # lateral columns
    (340, 135, 340, 255),                          # central axis
]


def generate(params: BellowsParams) -> FoldPattern:
    """Build the Yoshimura unit cell scaled by ``params.cell_scale``."""
    params.validate()
    return cell_from_edges("yoshimura", _MOUNTAIN, _VALLEY, params.cell_scale)


__all__ = ["generate"]
