"""png.py
─────────
Raster preview export — render a :class:`Stencil` to a PNG with PIL.

Layers are drawn in order in their preview colours; useful for proofing the
composited result before cutting/printing.  Anti-aliasing is approximated by
rendering at ``supersample``× and downscaling.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

from ..geometry import Dot, Polyline, Stencil


def render_png(
    stencil: Stencil,
    *,
    background: tuple[int, int, int] = (255, 255, 255),
    supersample: int = 2,
) -> Image.Image:
    """Render a stencil to a PIL ``Image`` (composited preview)."""
    ss = max(1, int(supersample))
    w = max(1, int(round(stencil.width * ss)))
    h = max(1, int(round(stencil.height * ss)))
    img = Image.new("RGB", (w, h), background)
    draw = ImageDraw.Draw(img)
    for layer in stencil.layers:
        color = tuple(layer.color)
        for prim in layer.primitives:
            if isinstance(prim, Dot):
                r = prim.r * ss
                draw.ellipse(
                    [prim.x * ss - r, prim.y * ss - r, prim.x * ss + r, prim.y * ss + r],
                    fill=color,
                )
            elif isinstance(prim, Polyline):
                pts = [(x * ss, y * ss) for x, y in prim.points]
                if prim.fill and len(pts) >= 3:
                    if prim.holes:
                        # build a mask (outer filled, holes cleared) and paste through it
                        mask = Image.new("L", (w, h), 0)
                        md = ImageDraw.Draw(mask)
                        md.polygon(pts, fill=255)
                        for hole in prim.holes:
                            md.polygon([(x * ss, y * ss) for x, y in hole], fill=0)
                        img.paste(Image.new("RGB", (w, h), color), (0, 0), mask)
                    else:
                        draw.polygon(pts, fill=color)
                elif len(pts) >= 2:
                    draw.line(pts, fill=color, width=max(1, int(round(prim.width * ss))))
    if ss != 1:
        img = img.resize(
            (max(1, int(round(stencil.width))), max(1, int(round(stencil.height)))),
            Image.LANCZOS,
        )
    return img


def write_png(
    stencil: Stencil,
    path: str | Path,
    *,
    background: tuple[int, int, int] = (255, 255, 255),
    supersample: int = 2,
) -> Path:
    """Render a stencil and write it to ``path`` as PNG."""
    path = Path(path)
    render_png(stencil, background=background, supersample=supersample).save(path)
    return path
