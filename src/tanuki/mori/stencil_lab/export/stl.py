"""stl.py
─────────
STL export — extrude the filled stencil shapes into solids and triangulate.

Only **filled** primitives become solids: dots (as polygon discs) and filled
polygons.  Each is triangulated by ear-clipping, duplicated at ``z = 0`` and
``z = thickness``, and walled around the boundary, yielding a closed solid
suitable for 3-D printing a physical stencil plate.

Coordinates flip y against the canvas height and scale by ``scale`` (units per
pixel); extrusion grows along +Z.
"""

from __future__ import annotations

from pathlib import Path

import math

from ..geometry import Dot, Polyline, Stencil

Pt2 = tuple[float, float]
Pt3 = tuple[float, float, float]


# ─── polygon helpers ──────────────────────────────────────────────────────────

def _signed_area(poly: list[Pt2]) -> float:
    s = 0.0
    n = len(poly)
    for i in range(n):
        x0, y0 = poly[i]
        x1, y1 = poly[(i + 1) % n]
        s += x0 * y1 - x1 * y0
    return s * 0.5


def _cross(a: Pt2, b: Pt2, c: Pt2) -> float:
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def _point_in_tri(p: Pt2, a: Pt2, b: Pt2, c: Pt2) -> bool:
    d1 = _cross(p, a, b)
    d2 = _cross(p, b, c)
    d3 = _cross(p, c, a)
    has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0)
    has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0)
    return not (has_neg and has_pos)


def _dedupe(poly: list[Pt2]) -> list[Pt2]:
    if len(poly) >= 2 and poly[0] == poly[-1]:
        poly = poly[:-1]
    return poly


def triangulate(poly: list[Pt2]) -> list[tuple[Pt2, Pt2, Pt2]]:
    """Ear-clipping triangulation of a simple polygon → CCW triangles."""
    poly = _dedupe(list(poly))
    n = len(poly)
    if n < 3:
        return []
    idx = list(range(n))
    if _signed_area(poly) < 0:          # ensure CCW
        idx.reverse()
    tris: list[tuple[Pt2, Pt2, Pt2]] = []
    guard = 0
    while len(idx) > 3 and guard < 100000:
        guard += 1
        m = len(idx)
        ear = False
        for k in range(m):
            i0, i1, i2 = idx[(k - 1) % m], idx[k], idx[(k + 1) % m]
            a, b, c = poly[i0], poly[i1], poly[i2]
            if _cross(a, b, c) <= 0:    # reflex / collinear → not an ear
                continue
            if any(
                poly[idx[j]] not in (a, b, c)        # ignore coincident bridge verts
                and _point_in_tri(poly[idx[j]], a, b, c)
                for j in range(m) if idx[j] not in (i0, i1, i2)
            ):
                continue
            tris.append((a, b, c))
            del idx[k]
            ear = True
            break
        if not ear:                     # degenerate; bail out gracefully
            break
    if len(idx) == 3:
        tris.append((poly[idx[0]], poly[idx[1]], poly[idx[2]]))
    return tris


# ─── extrusion → triangles ──────────────────────────────────────────────────

def _facet(n: Pt3, a: Pt3, b: Pt3, c: Pt3) -> str:
    return (
        f"  facet normal {n[0]:.6e} {n[1]:.6e} {n[2]:.6e}\n"
        f"    outer loop\n"
        f"      vertex {a[0]:.6e} {a[1]:.6e} {a[2]:.6e}\n"
        f"      vertex {b[0]:.6e} {b[1]:.6e} {b[2]:.6e}\n"
        f"      vertex {c[0]:.6e} {c[1]:.6e} {c[2]:.6e}\n"
        f"    endloop\n  endfacet\n"
    )


def _eliminate_holes(outer: list[Pt2], holes: list[list[Pt2]]) -> list[Pt2]:
    """Splice each hole into the outer ring via a zero-width bridge (earcut style).

    Each hole is connected to the outer boundary at their mutually closest pair
    of vertices, producing one simple polygon ear-clipping can triangulate.
    """
    poly = list(outer)
    for hole in holes:
        best = None
        for i, p in enumerate(poly):
            for j, q in enumerate(hole):
                d = (p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2
                if best is None or d < best[0]:
                    best = (d, i, j)
        _, i, j = best
        bridge = hole[j:] + hole[:j + 1]            # walk the hole, back to start
        poly = poly[:i + 1] + bridge + [poly[i]] + poly[i + 1:]
    return poly


def _walls(ring: list[Pt2], z0: float, z1: float) -> list[tuple[Pt3, Pt3, Pt3]]:
    tris = []
    n = len(ring)
    for i in range(n):
        x0, y0 = ring[i]
        x1, y1 = ring[(i + 1) % n]
        bl, br = (x0, y0, z0), (x1, y1, z0)
        tl, tr = (x0, y0, z1), (x1, y1, z1)
        tris.append((bl, br, tr))
        tris.append((bl, tr, tl))
    return tris


def _extrude_polygon(outer: list[Pt2], holes: list[list[Pt2]],
                     thickness: float) -> list[tuple[Pt3, Pt3, Pt3]]:
    """Closed solid: top + bottom caps (minus holes) + outer & hole walls."""
    outer = _dedupe(list(outer))
    if len(outer) < 3:
        return []
    if _signed_area(outer) < 0:                     # outer CCW (top normal +Z)
        outer = outer[::-1]
    # holes wound opposite to the outer ring so caps and walls stay consistent
    holes = [_dedupe(list(h)) for h in holes if len(_dedupe(list(h))) >= 3]
    holes = [h if _signed_area(h) < 0 else h[::-1] for h in holes]

    bridged = _eliminate_holes(outer, holes) if holes else outer
    caps = triangulate(bridged)
    z0, z1 = 0.0, thickness
    tris: list[tuple[Pt3, Pt3, Pt3]] = []
    for a, b, c in caps:                            # top cap (+Z)
        tris.append(((a[0], a[1], z1), (b[0], b[1], z1), (c[0], c[1], z1)))
    for a, b, c in caps:                            # bottom cap (−Z, reversed)
        tris.append(((a[0], a[1], z0), (c[0], c[1], z0), (b[0], b[1], z0)))
    for ring in [outer, *holes]:                    # outer + cavity walls
        tris += _walls(ring, z0, z1)
    return tris


def _normal(a: Pt3, b: Pt3, c: Pt3) -> Pt3:
    ux, uy, uz = b[0] - a[0], b[1] - a[1], b[2] - a[2]
    vx, vy, vz = c[0] - a[0], c[1] - a[1], c[2] - a[2]
    nx, ny, nz = uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx
    length = math.sqrt(nx * nx + ny * ny + nz * nz)
    if length == 0:
        return (0.0, 0.0, 0.0)
    return (nx / length, ny / length, nz / length)


def _filled_polys(stencil: Stencil, dot_resolution: int
                  ) -> list[tuple[list[Pt2], list[list[Pt2]]]]:
    """Return ``(outer, holes)`` for every filled shape, y flipped to STL space."""
    h = stencil.height
    out: list[tuple[list[Pt2], list[list[Pt2]]]] = []
    for layer in stencil.layers:
        for prim in layer.primitives:
            if isinstance(prim, Dot):
                out.append(([
                    (prim.x + prim.r * math.cos(2 * math.pi * i / dot_resolution),
                     h - (prim.y + prim.r * math.sin(2 * math.pi * i / dot_resolution)))
                    for i in range(dot_resolution)
                ], []))
            elif isinstance(prim, Polyline) and prim.fill and len(prim.points) >= 3:
                outer = [(x, h - y) for x, y in prim.points]
                holes = [[(x, h - y) for x, y in hole] for hole in prim.holes]
                out.append((outer, holes))
    return out


def to_stl(
    stencil: Stencil,
    *,
    thickness: float = 1.0,
    scale: float = 1.0,
    dot_resolution: int = 24,
    name: str = "stencil",
) -> str:
    """Render filled stencil shapes to an ASCII STL solid string."""
    shapes = _filled_polys(stencil, dot_resolution)
    lines = [f"solid {name}\n"]
    for outer, holes in shapes:
        s_outer = [(x * scale, y * scale) for x, y in outer]
        s_holes = [[(x * scale, y * scale) for x, y in h] for h in holes]
        for a, b, c in _extrude_polygon(s_outer, s_holes, thickness):
            n = _normal(a, b, c)
            lines.append(_facet(n, a, b, c))
    lines.append(f"endsolid {name}\n")
    return "".join(lines)


def write_stl(
    stencil: Stencil,
    path: str | Path,
    *,
    thickness: float = 1.0,
    scale: float = 1.0,
    dot_resolution: int = 24,
) -> Path:
    """Write a stencil to ``path`` as ASCII STL, returning the path."""
    path = Path(path)
    src = to_stl(stencil, thickness=thickness, scale=scale,
                 dot_resolution=dot_resolution, name=path.stem)
    path.write_text(src, encoding="utf-8")
    return path
