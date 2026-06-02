"""pdf.py
─────────
Vector PDF export — a single-page PDF written by hand (no dependencies).

Dots are emitted as Bézier circles, filled polylines as filled paths, stroked
polylines as stroked paths, each in its layer's preview colour.  PDF uses a
bottom-left origin (y-up), so image y is flipped against the page height.

The writer assembles objects while tracking byte offsets so the cross-reference
table is valid.  Everything is ASCII (latin-1), so character counts equal byte
counts.
"""

from __future__ import annotations

from pathlib import Path

from ..geometry import Dot, Polyline, Stencil

MM_PER_IN = 25.4
_KAPPA = 0.5522847498307936  # circle-from-4-béziers magic constant


def _n(v: float) -> str:
    return f"{v:.3f}".rstrip("0").rstrip(".")


def _rgb(color: tuple[int, int, int]) -> str:
    return f"{_n(color[0] / 255)} {_n(color[1] / 255)} {_n(color[2] / 255)}"


def _circle_ops(cx: float, cy: float, r: float) -> str:
    k = _KAPPA * r
    return (
        f"{_n(cx + r)} {_n(cy)} m\n"
        f"{_n(cx + r)} {_n(cy + k)} {_n(cx + k)} {_n(cy + r)} {_n(cx)} {_n(cy + r)} c\n"
        f"{_n(cx - k)} {_n(cy + r)} {_n(cx - r)} {_n(cy + k)} {_n(cx - r)} {_n(cy)} c\n"
        f"{_n(cx - r)} {_n(cy - k)} {_n(cx - k)} {_n(cy - r)} {_n(cx)} {_n(cy - r)} c\n"
        f"{_n(cx + k)} {_n(cy - r)} {_n(cx + r)} {_n(cy - k)} {_n(cx + r)} {_n(cy)} c\n"
        "h\n"
    )


def _content_stream(stencil: Stencil) -> str:
    h = stencil.height
    ops: list[str] = []
    for layer in stencil.layers:
        fill = _rgb(layer.color)
        for prim in layer.primitives:
            if isinstance(prim, Dot):
                ops.append(f"{fill} rg")
                ops.append(_circle_ops(prim.x, h - prim.y, prim.r) + "f")
            elif isinstance(prim, Polyline) and len(prim.points) >= 2:
                def _sub(points):
                    p = [(x, h - y) for x, y in points]
                    s = f"{_n(p[0][0])} {_n(p[0][1])} m\n"
                    s += "".join(f"{_n(x)} {_n(y)} l\n" for x, y in p[1:])
                    return s + "h\n"
                if prim.fill:
                    ops.append(f"{fill} rg")
                    path = _sub(prim.points) + "".join(_sub(hole) for hole in prim.holes)
                    # even-odd fill (f*) so holes are punched out
                    ops.append(path + ("f*" if prim.holes else "f"))
                else:
                    ops.append(f"{fill} RG")
                    ops.append(f"{_n(prim.width)} w")
                    pts = [(x, h - y) for x, y in prim.points]
                    sp = f"{_n(pts[0][0])} {_n(pts[0][1])} m\n"
                    sp += "".join(f"{_n(x)} {_n(y)} l\n" for x, y in pts[1:])
                    ops.append(sp + ("h\nS" if prim.closed else "S"))
    return "\n".join(ops) + "\n"


def to_pdf(stencil: Stencil) -> bytes:
    """Render a stencil to a single-page vector PDF (bytes).

    PDF user space is points (1/72").  When the stencil is in millimetres the
    whole page is scaled by 72/25.4 via a ``cm`` matrix so it prints 1:1.
    """
    # mm → points so physical (mm) stencils print at real size
    u = (72.0 / MM_PER_IN) if stencil.units == "mm" else 1.0
    w, h = stencil.width * u, stencil.height * u
    content = _content_stream(stencil)
    if u != 1.0:
        content = f"{_n(u)} 0 0 {_n(u)} 0 0 cm\n" + content
    objects = [
        "<< /Type /Catalog /Pages 2 0 R >>",
        "<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {_n(w)} {_n(h)}] "
        f"/Contents 4 0 R /Resources << >> >>",
        f"<< /Length {len(content)} >>\nstream\n{content}endstream",
    ]

    buf = "%PDF-1.4\n"
    offsets: list[int] = []
    for i, body in enumerate(objects, start=1):
        offsets.append(len(buf))
        buf += f"{i} 0 obj\n{body}\nendobj\n"

    xref_pos = len(buf)
    n = len(objects)
    buf += f"xref\n0 {n + 1}\n0000000000 65535 f \n"
    for off in offsets:
        buf += f"{off:010d} 00000 n \n"
    buf += (
        f"trailer\n<< /Size {n + 1} /Root 1 0 R >>\n"
        f"startxref\n{xref_pos}\n%%EOF\n"
    )
    return buf.encode("latin-1")


def write_pdf(stencil: Stencil, path: str | Path) -> Path:
    """Write a stencil to ``path`` as a vector PDF, returning the path."""
    path = Path(path)
    path.write_bytes(to_pdf(stencil))
    return path
