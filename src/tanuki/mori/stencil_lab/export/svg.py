"""svg.py
────────
SVG serialisation for a :class:`~stencil_lab.geometry.Stencil`.

Each layer becomes an SVG ``<g>`` group (named after the channel, filled with
the channel's preview colour) so layers can be toggled / sent to a cutter
independently.  The image-space coordinate system (top-left origin, y-down)
maps 1:1 onto SVG's, so no flipping is needed.
"""

from __future__ import annotations

from pathlib import Path

from ..geometry import Dot, Layer, Polyline, Stencil


def _fmt(n: float) -> str:
    """Compact float formatting (trim trailing zeros)."""
    return f"{n:.3f}".rstrip("0").rstrip(".")


def _rgb(color: tuple[int, int, int]) -> str:
    return f"rgb({color[0]},{color[1]},{color[2]})"


def _dot_svg(d: Dot, fill: str) -> str:
    return f'    <circle cx="{_fmt(d.x)}" cy="{_fmt(d.y)}" r="{_fmt(d.r)}" fill="{fill}"/>'


def _subpath(points) -> str:
    head = f"M {_fmt(points[0][0])},{_fmt(points[0][1])}"
    rest = " ".join(f"L {_fmt(x)},{_fmt(y)}" for x, y in points[1:])
    return f"{head} {rest} Z"


def _polyline_svg(p: Polyline, color: str) -> str:
    if p.fill and p.holes:
        # outer + hole subpaths, even-odd rule punches the holes out
        d = " ".join([_subpath(p.points)] + [_subpath(h) for h in p.holes])
        return f'    <path d="{d}" fill="{color}" fill-rule="evenodd" stroke="none"/>'
    pts = " ".join(f"{_fmt(x)},{_fmt(y)}" for x, y in p.points)
    tag = "polygon" if p.closed else "polyline"
    if p.fill:
        style = f'fill="{color}" stroke="none"'
    else:
        style = (
            f'fill="none" stroke="{color}" stroke-width="{_fmt(p.width)}" '
            'stroke-linecap="round" stroke-linejoin="round"'
        )
    return f'    <{tag} points="{pts}" {style}/>'


def _layer_svg(layer: Layer) -> str:
    color = _rgb(layer.color)
    body = []
    for prim in layer.primitives:
        if isinstance(prim, Dot):
            body.append(_dot_svg(prim, color))
        else:
            body.append(_polyline_svg(prim, color))
    inner = "\n".join(body)
    return f'  <g id="{layer.name}" inkscape:label="{layer.name}">\n{inner}\n  </g>'


def to_svg(stencil: Stencil, *, background: str | None = None) -> str:
    """Render a stencil to an SVG document string."""
    w, h = _fmt(stencil.width), _fmt(stencil.height)
    parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape" '
        f'width="{w}{stencil.units}" height="{h}{stencil.units}" '
        f'viewBox="0 0 {w} {h}">',
    ]
    if background:
        parts.append(
            f'  <rect x="0" y="0" width="{w}" height="{h}" fill="{background}"/>'
        )
    for layer in stencil.layers:
        parts.append(_layer_svg(layer))
    parts.append("</svg>")
    return "\n".join(parts)


def write_svg(stencil: Stencil, path: str | Path, *, background: str | None = None) -> Path:
    """Write a stencil to ``path`` as SVG, returning the path."""
    path = Path(path)
    path.write_text(to_svg(stencil, background=background), encoding="utf-8")
    return path
