"""optimize.py
──────────────
High-level stencil optimisation: clean → reinforce → verify.

:func:`optimize_mask` runs the full Phase 3 pipeline on a :class:`StencilMask`:

1. **Remove small holes** — drop sub-kerf speckle that won't cut.
2. **Remove tiny islands** — cut away material fragments too small to bridge.
3. **Add bridges** — tie every remaining enclosed island back to the body.
4. **Re-check** — return fabrication metrics for the result.

It returns the optimised mask plus an :class:`OptimizeReport` describing what
changed and whether the result is fabrication-ready.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .checks import fabrication_checks, summarize
from .features import remove_small_holes, remove_small_islands
from .islands import add_bridges, detect_islands
from .mask import StencilMask


@dataclass(slots=True)
class OptimizeReport:
    holes_removed: int = 0
    islands_removed: int = 0
    bridges_added: int = 0
    islands_before: int = 0
    islands_after: int = 0
    checks: dict[str, list[str]] = field(default_factory=dict)

    @property
    def ready(self) -> bool:
        """True when every fabrication check passed."""
        return all(not problems for problems in self.checks.values())

    def __str__(self) -> str:
        head = (
            f"Stencil optimisation report\n"
            f"  islands: {self.islands_before} → {self.islands_after}  "
            f"(removed {self.islands_removed}, bridged {self.bridges_added})\n"
            f"  small holes removed: {self.holes_removed}\n"
            f"  fabrication checks:\n"
        )
        return head + summarize(self.checks) + (
            "\n  → READY" if self.ready else "\n  → NEEDS ATTENTION"
        )


def optimize_mask(
    mask: StencilMask,
    *,
    min_hole_area: int = 4,
    min_island_area: int = 16,
    bridge_width: float = 2.0,
    min_feature_px: float = 2.0,
    add_bridges_pass: bool = True,
) -> tuple[StencilMask, OptimizeReport]:
    """Clean, reinforce and verify a stencil mask. See module docstring."""
    report = OptimizeReport()
    report.islands_before = len(detect_islands(mask))

    work, report.holes_removed = remove_small_holes(mask, min_area=min_hole_area)
    work, report.islands_removed = remove_small_islands(work, min_area=min_island_area)

    if add_bridges_pass:
        work, report.bridges_added = add_bridges(
            work, width=bridge_width, min_area=min_island_area,
        )

    report.islands_after = len(detect_islands(work))
    report.checks = fabrication_checks(work, min_feature_px=min_feature_px)
    return work, report
