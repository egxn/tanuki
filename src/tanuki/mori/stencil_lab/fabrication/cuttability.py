"""cuttability.py
─────────────────
Can this stencil be cut **without losing information**?

A stencil only holds together if every piece of *material* (the parts that
stay) is robustly connected to the sheet frame.  Two ways information is lost:

1. **Islands** — material fully enclosed by cut-out falls out, so the region it
   represented is gone.
2. **Weak necks** — material connected to the frame only through a sliver
   thinner than the tool's minimum feature; it tears off at cut time, which
   *also* loses that material (and merges the holes it separated).

This module answers the question topologically, via **morphological
reconstruction**:

* erode the material by ``r = min_feature/2`` → the "robust core" (anything
  thinner than the minimum feature disappears);
* keep core components that touch the frame → the *anchors*;
* geodesically dilate the anchors back inside the material → the **safe**
  material (everything reachable through channels ≥ the minimum feature).

Whatever material is *not* safe is **at risk**: it would detach or tear.  Zero
at-risk material (and no sub-kerf holes) ⇒ the design cuts losslessly as-is.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from .islands import _MAT_STRUCT, _border_labels
from .mask import StencilMask


@dataclass(slots=True)
class AtRiskRegion:
    """A piece of material that would be lost when cut."""

    id: int
    area: int                          # pixels
    centroid: tuple[float, float]      # (x, y)
    bbox: tuple[int, int, int, int]    # (x0, y0, x1, y1)
    kind: str                          # "isolated" | "weak-neck"
    bridgeable: bool                   # can a bridge to safe material rescue it?
    anchor_distance: float             # px to the nearest safe material


@dataclass(slots=True)
class CuttabilityReport:
    """Verdict on whether a :class:`StencilMask` cuts without losing information."""

    min_feature_px: float
    sheet_px: int
    material_px: int
    anchored_px: int
    at_risk_px: int
    regions: list[AtRiskRegion] = field(default_factory=list)
    subkerf_hole_count: int = 0
    subkerf_hole_px: int = 0
    n_material_components: int = 0

    # ── derived verdicts ──────────────────────────────────────────────────
    @property
    def at_risk_fraction(self) -> float:
        """Share of *material* that would detach or tear (0 = perfect)."""
        return self.at_risk_px / self.material_px if self.material_px else 0.0

    @property
    def score(self) -> float:
        """Fraction of material that survives the cut (1.0 = nothing lost)."""
        if self.material_px == 0:
            return 0.0
        return self.anchored_px / self.material_px

    @property
    def single_piece(self) -> bool:
        """True when the material is one connected component (frame + design)."""
        return self.n_material_components == 1

    @property
    def needs_bridges(self) -> int:
        """At-risk regions a bridge could rescue (one bridge each)."""
        return sum(1 for r in self.regions if r.bridgeable)

    @property
    def cuttable(self) -> bool:
        """True ⇒ cut as-is, no information lost."""
        return (
            self.material_px > 0
            and self.at_risk_px == 0
            and self.subkerf_hole_count == 0
        )

    def summary(self) -> str:
        verdict = ("CUTTABLE — no information lost" if self.cuttable
                   else "NOT directly cuttable")
        lines = [
            f"  verdict: {verdict}",
            f"  material anchored to frame: {self.anchored_px}/{self.material_px} px "
            f"({100 * self.score:.1f}%)",
            f"  material components: {self.n_material_components}"
            f"{' (single piece)' if self.single_piece else ''}",
        ]
        if self.at_risk_px:
            iso = sum(1 for r in self.regions if r.kind == "isolated")
            weak = len(self.regions) - iso
            lines.append(
                f"  at-risk material: {self.at_risk_px} px "
                f"({100 * self.at_risk_fraction:.1f}%) in {len(self.regions)} region(s) "
                f"— {iso} isolated, {weak} weak-neck"
            )
            lines.append(
                f"    rescuable by bridges: {self.needs_bridges}/{len(self.regions)}"
            )
        if self.subkerf_hole_count:
            lines.append(
                f"  sub-kerf holes (won't cut cleanly): {self.subkerf_hole_count} "
                f"({self.subkerf_hole_px} px)"
            )
        return "\n".join(lines)

    def __str__(self) -> str:
        return "Cuttability analysis\n" + self.summary()


# ─── core algorithm ────────────────────────────────────────────────────────────

def safe_material(mask: StencilMask, *, min_feature_px: float = 2.0) -> np.ndarray:
    """Boolean mask of material robustly connected to the frame.

    Material reachable from the sheet edge only through channels narrower than
    ``min_feature_px`` is excluded — it would tear away.
    """
    from scipy import ndimage

    material = mask.material
    if not material.any():
        return np.zeros_like(material)
    r = max(1, int(round(min_feature_px / 2.0)))
    # border_value=1 → the sheet edge counts as solid material (the frame anchor)
    core = ndimage.binary_erosion(material, structure=_MAT_STRUCT,
                                  iterations=r, border_value=1)
    labels, n = ndimage.label(core, structure=_MAT_STRUCT)
    if n == 0:
        return np.zeros_like(material)
    anchored = np.isin(labels, list(_border_labels(labels)))
    # Opening: dilate the anchored core back by the *same* radius (not geodesic,
    # so it will not cross a neck the erosion already severed) and clip to
    # material. Equivalent to keeping only material that survives an opening
    # rooted at the frame — i.e. reachable through channels ≥ the min feature.
    restored = ndimage.binary_dilation(anchored, structure=_MAT_STRUCT, iterations=r)
    return restored & material


def at_risk_material(mask: StencilMask, *, min_feature_px: float = 2.0) -> np.ndarray:
    """Boolean mask of material that would detach or tear when cut."""
    return mask.material & ~safe_material(mask, min_feature_px=min_feature_px)


def _subkerf_holes(cut: np.ndarray, min_feature_px: float) -> tuple[int, int]:
    from scipy import ndimage

    if not cut.any():
        return 0, 0
    labels, n = ndimage.label(cut, structure=_MAT_STRUCT)
    dist = ndimage.distance_transform_edt(cut)
    # per-component peak distance (inscribed radius) — vectorised, no per-label scan
    peaks = ndimage.maximum(dist, labels, index=range(1, n + 1))
    sizes = ndimage.sum_labels(np.ones_like(labels), labels, index=range(1, n + 1))
    peaks = np.atleast_1d(peaks)
    sizes = np.atleast_1d(sizes)
    small = (2.0 * peaks) < min_feature_px               # inscribed Ø < kerf
    return int(small.sum()), int(sizes[small].sum())


def analyze_cuttability(mask: StencilMask, *,
                        min_feature_px: float = 2.0) -> CuttabilityReport:
    """Evaluate whether ``mask`` can be cut without losing information.

    Returns a :class:`CuttabilityReport`: how much material is anchored vs
    at-risk, every at-risk region classified (isolated island vs weak neck) and
    whether a bridge could rescue it, plus any sub-kerf holes that won't cut.
    """
    from scipy import ndimage

    material = mask.material
    sheet_px = int(material.size)
    material_px = int(material.sum())

    safe = safe_material(mask, min_feature_px=min_feature_px)
    anchored_px = int(safe.sum())
    risk = material & ~safe
    at_risk_px = int(risk.sum())

    mlabels, mn = ndimage.label(material, structure=_MAT_STRUCT)
    mborder = _border_labels(mlabels) if mn else set()
    dist_to_safe = (ndimage.distance_transform_edt(~safe)
                    if safe.any() else None)

    regions: list[AtRiskRegion] = []
    rlabels, rn = ndimage.label(risk, structure=_MAT_STRUCT)
    slices = ndimage.find_objects(rlabels)              # per-region bbox
    for lab in range(1, rn + 1):
        sl = slices[lab - 1]
        if sl is None:
            continue
        y0, x0 = sl[0].start, sl[1].start
        sub = rlabels[sl] == lab
        ly, lx = np.nonzero(sub)
        # the material component this risk piece sits in
        mlab = int(mlabels[sl][ly[0], lx[0]])
        kind = "isolated" if mlab not in mborder else "weak-neck"
        if dist_to_safe is not None:
            d = float(dist_to_safe[sl][sub].min())
            bridgeable = np.isfinite(d)
        else:
            d, bridgeable = float("inf"), False
        regions.append(AtRiskRegion(
            id=lab, area=int(lx.size),
            centroid=(float(lx.mean() + x0), float(ly.mean() + y0)),
            bbox=(int(lx.min() + x0), int(ly.min() + y0),
                  int(lx.max() + x0), int(ly.max() + y0)),
            kind=kind, bridgeable=bridgeable, anchor_distance=d,
        ))

    sub_count, sub_px = _subkerf_holes(mask.cut, min_feature_px)
    return CuttabilityReport(
        min_feature_px=min_feature_px, sheet_px=sheet_px, material_px=material_px,
        anchored_px=anchored_px, at_risk_px=at_risk_px, regions=regions,
        subkerf_hole_count=sub_count, subkerf_hole_px=sub_px,
        n_material_components=mn,
    )
