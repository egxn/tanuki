"""dxf.py
─────────
DXF export — AutoCAD R12 ASCII, the lingua franca of laser / vinyl cutters.

Each stencil layer becomes a DXF layer; dots become ``CIRCLE`` entities and
polylines become ``POLYLINE`` / ``VERTEX`` sequences.  R12 ASCII is the most
widely accepted dialect and is trivial to emit by hand.

DXF uses a bottom-left origin (y-up), so image y is flipped against the canvas
height.
"""

from __future__ import annotations

from pathlib import Path

from ..geometry import Dot, Polyline, Stencil


def _pair(code: int, value) -> str:
    return f"{code}\n{value}"


def _circle(layer: str, cx: float, cy: float, r: float) -> list[str]:
    return [
        _pair(0, "CIRCLE"), _pair(8, layer),
        _pair(10, f"{cx:.4f}"), _pair(20, f"{cy:.4f}"), _pair(30, "0.0"),
        _pair(40, f"{r:.4f}"),
    ]


def _polyline(layer: str, pts: list[tuple[float, float]], closed: bool) -> list[str]:
    out = [
        _pair(0, "POLYLINE"), _pair(8, layer),
        _pair(66, 1),                      # vertices-follow flag
        _pair(70, 1 if closed else 0),     # 1 = closed polyline
    ]
    for x, y in pts:
        out += [
            _pair(0, "VERTEX"), _pair(8, layer),
            _pair(10, f"{x:.4f}"), _pair(20, f"{y:.4f}"), _pair(30, "0.0"),
        ]
    out += [_pair(0, "SEQEND"), _pair(8, layer)]
    return out


def to_dxf(stencil: Stencil) -> str:
    """Render a stencil to a DXF R12 ASCII document string."""
    h = stencil.height
    body: list[str] = [_pair(0, "SECTION"), _pair(2, "ENTITIES")]
    for layer in stencil.layers:
        name = layer.name
        for prim in layer.primitives:
            if isinstance(prim, Dot):
                body += _circle(name, prim.x, h - prim.y, prim.r)
            elif isinstance(prim, Polyline):
                pts = [(x, h - y) for x, y in prim.points]
                if len(pts) >= 2:
                    body += _polyline(name, pts, prim.closed)
                # holes become their own closed polylines (nested for the cutter)
                for hole in prim.holes:
                    hpts = [(x, h - y) for x, y in hole]
                    if len(hpts) >= 2:
                        body += _polyline(name, hpts, True)
    body += [_pair(0, "ENDSEC"), _pair(0, "EOF")]
    return "\n".join(body) + "\n"


def write_dxf(stencil: Stencil, path: str | Path) -> Path:
    """Write a stencil to ``path`` as DXF, returning the path."""
    path = Path(path)
    path.write_text(to_dxf(stencil), encoding="utf-8")
    return path
