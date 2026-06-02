"""gui.py
─────────
A small FastAPI web GUI for the Stencil Lab.

Run::

    pip install fastapi uvicorn python-multipart
    python -m tanuki.mori.stencil_lab.gui          # → http://127.0.0.1:8000

Design (matches the proposal):

* **Live preview is vector + fast.** ``/api/preview`` runs the *un-optimised*
  pipeline at a small resolution and returns **inline SVG** whose layers are
  ``<g id="channel">`` groups — so toggling a colour plate is pure CSS in the
  browser, no re-render.
* **Cuttability** is reported live (``analyze_cuttability``).
* **Export is the heavy, on-demand step.** ``/api/export`` runs the
  cut-optimised pipeline (and physical sizing / paper tiling) in FastAPI's
  threadpool, returning a file (or a ``.zip`` of sheets) to download.

Everything reuses the library functions; this module is only glue. The page
markup lives next door in ``gui_index.html`` (the option lists are injected at
load time via :func:`_load_page`).
"""

from __future__ import annotations

import io
import zipfile
from pathlib import Path
from tempfile import mkdtemp
from uuid import uuid4

from . import (
    add_registration_marks,
    analyze_cuttability,
    build_stencil,
    fit_to_physical,
    optimize_for_cutting,
    tile_to_paper,
    to_svg,
    write_blender_script,
    write_dxf,
    write_pdf,
    write_png,
    write_stl,
    write_svg,
)
from . import separation as sep
from .fabrication import StencilMask, island_mask
from .image_io import load_image, resize, to_grayscale
from . import adjustments as adj
from .patterns import PATTERN_NAMES
from .sizing import PAPER

try:
    from fastapi import FastAPI, Form, HTTPException, UploadFile
    from fastapi.responses import HTMLResponse, JSONResponse, Response, FileResponse
except ModuleNotFoundError as exc:  # pragma: no cover - import guard
    raise SystemExit(
        "The GUI needs FastAPI:\n    pip install fastapi uvicorn python-multipart"
    ) from exc

METHODS = ["grayscale", "cmyk", "rgb", "duotone", "tritone"]
EXPORT_FORMATS = ["svg", "png", "dxf", "pdf", "stl", "blender"]
_STORE = Path(mkdtemp(prefix="stencil_gui_"))           # uploaded images live here
_UPLOADS: dict[str, Path] = {}


# ─── core: build a stencil from request params ──────────────────────────────

def _prep(path: Path, *, method: str, contrast: float, gamma: float,
          invert: bool, max_side: int):
    """Load → adjust → separate. Returns (Separation, (w, h))."""
    arr = resize(load_image(path), max_side=max_side)
    # tone adjustments on a grayscale or colour array
    if contrast != 1.0:
        arr = adj.contrast(arr, contrast)
    if gamma != 1.0:
        arr = adj.gamma(arr, gamma)
    if invert:
        arr = adj.invert(arr)
    if method in ("rgb", "cmyk") and arr.ndim == 2:
        import numpy as np
        arr = np.repeat(arr[..., None], 3, axis=-1)
    fn = getattr(sep, method)
    h, w = arr.shape[:2]
    return fn(arr), (w, h)


def _stencil(path, *, method, pattern, cell, contrast, gamma, invert,
             max_side, optimize, registration):
    separation, size = _prep(path, method=method, contrast=contrast, gamma=gamma,
                             invert=invert, max_side=max_side)
    st = build_stencil(separation, size, pattern=pattern, cell=cell)
    if optimize:
        st = optimize_for_cutting(st)
    if registration and registration != "none":
        add_registration_marks(st, kind=registration)
    return st


# ─── app ────────────────────────────────────────────────────────────────────

app = FastAPI(title="Stencil Lab")


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    return _PAGE


@app.post("/api/upload")
async def upload(file: UploadFile) -> JSONResponse:
    data = await file.read()
    uid = uuid4().hex[:12]
    path = _STORE / f"{uid}_{Path(file.filename or 'img').name}"
    path.write_bytes(data)
    _UPLOADS[uid] = path
    arr = load_image(path)
    h, w = arr.shape[:2]
    return JSONResponse({"id": uid, "width": w, "height": h})


def _lookup(uid: str) -> Path:
    path = _UPLOADS.get(uid)
    if not path or not path.exists():
        raise HTTPException(404, "unknown image id — upload again")
    return path


@app.get("/api/preview")
def preview(id: str, method: str = "grayscale", pattern: str = "dots",
            cell: float = 6.0, contrast: float = 1.0, gamma: float = 1.0,
            invert: bool = False, max_side: int = 480,
            out_size: str = "none", landscape: bool = False,
            min_feature_mm: float = 0.5, show_islands: bool = False) -> JSONResponse:
    """Fast un-optimised vector preview + **per-plate** cuttability verdict.

    Each layer is a separate plate (cut on its own sheet), so cuttability is
    analysed per layer — not on the union of all inks. The minimum feature is a
    real tool size in **mm**: when an ``out_size`` (paper) is chosen it is
    converted to pixels at that print scale, so "thin material" depends on how
    big you actually print. Speckle below the cell size is ignored, and islands
    (real fall-out) are reported apart from thin material.
    """
    from .sizing import paper_size

    path = _lookup(id)
    st = _stencil(path, method=method, pattern=pattern, cell=cell,
                  contrast=contrast, gamma=gamma, invert=invert,
                  max_side=min(max_side, 700), optimize=False, registration="none")
    w, h = int(round(st.width)), int(round(st.height))

    # minimum feature → pixels at the chosen print scale (else treat mm as px)
    if out_size and out_size != "none":
        ow, oh = paper_size(out_size, landscape=landscape)
        mm_per_px = min(ow / w, oh / h)               # fit-within scale
        min_feature_px = min_feature_mm / mm_per_px
        scale_note = f"@ {out_size}{'↔' if landscape else ''}, {min_feature_mm}mm tool"
    else:
        min_feature_px = max(min_feature_mm, 1.0)     # mm read as px when unsized
        scale_note = f"@ {min_feature_px:.0f}px (set an output size for real mm)"

    import numpy as np
    mia = max(round(min_feature_px ** 2), round(cell ** 2))   # ignore speckle
    layers, total_islands, unbridgeable, max_thin = [], 0, 0, 0.0
    islands_union = np.zeros((h, w), bool) if show_islands else None
    for layer in st.layers:
        m = StencilMask.from_layer(layer, (w, h))
        rep = analyze_cuttability(m, min_feature_px=min_feature_px, min_island_area=mia)
        thin = rep.thin_px / rep.material_px if rep.material_px else 0.0
        stuck = sum(1 for r in rep.regions      # islands with nowhere to bridge to
                    if r.kind == "isolated" and not r.bridgeable)
        total_islands += rep.island_count
        unbridgeable += stuck
        max_thin = max(max_thin, thin)
        layers.append({"name": layer.name, "color": list(layer.color),
                       "count": len(layer), "islands": rep.island_count,
                       "thin": round(thin, 3), "bridgeable": rep.needs_bridges})
        if islands_union is not None:
            islands_union |= island_mask(m, min_feature_px=min_feature_px,
                                         min_island_area=mia)
    # green = nothing falls out; amber = islands but all bridgeable on export; red = real loss
    status = "loss" if unbridgeable > 0 else ("bridge" if total_islands else "clean")

    svg = to_svg(st, background="white")
    if islands_union is not None and islands_union.any():
        svg = svg.replace("</svg>", _islands_overlay(islands_union) + "</svg>")
    return JSONResponse({
        "svg": svg,
        "layers": layers,
        "primitives": st.primitive_count,
        "status": status,
        "islands": total_islands,
        "thin": round(max_thin, 3),
        "scale_note": scale_note,
    })


def _islands_overlay(mask) -> str:
    """A transparent red PNG of the island pixels, as an SVG ``<image>`` element."""
    import base64

    import numpy as np
    from PIL import Image

    h, w = mask.shape
    rgba = np.zeros((h, w, 4), np.uint8)
    rgba[mask] = (230, 20, 20, 210)
    buf = io.BytesIO()
    Image.fromarray(rgba, "RGBA").save(buf, "PNG")
    b64 = base64.b64encode(buf.getvalue()).decode("ascii")
    return (f'<image x="0" y="0" width="{w}" height="{h}" '
            f'style="image-rendering:pixelated" '
            f'href="data:image/png;base64,{b64}"/>')


@app.post("/api/export")
def export(id: str = Form(...), method: str = Form("grayscale"),
           pattern: str = Form("dots"), cell: float = Form(6.0),
           contrast: float = Form(1.0), gamma: float = Form(1.0),
           invert: bool = Form(False), max_side: int = Form(1000),
           fmt: str = Form("svg"), optimize: bool = Form(True),
           registration: str = Form("none"),
           out_size: str = Form("none"), landscape: bool = Form(False),
           paper: str = Form("none")):
    """Heavy, on-demand render → downloadable file (or .zip of sheets).

    ``out_size`` sets the **physical output size** to a paper (e.g. ``tabloid``)
    in the chosen ``landscape`` orientation; ``paper`` is the **sheet to split
    onto** (e.g. ``a4``). Runs in FastAPI's threadpool so the loop stays free.
    """
    from .sizing import paper_size

    if fmt not in EXPORT_FORMATS:
        raise HTTPException(400, f"bad format {fmt!r}")
    path = _lookup(id)
    st = _stencil(path, method=method, pattern=pattern, cell=cell,
                  contrast=contrast, gamma=gamma, invert=invert,
                  max_side=max_side, optimize=optimize, registration=registration)

    # physical output size: fit within the chosen paper, keeping aspect
    if out_size and out_size != "none":
        ow, oh = paper_size(out_size, landscape=landscape)
        st = fit_to_physical(st, width_mm=ow, height_mm=oh)
    elif paper and paper != "none":
        # no explicit output size but splitting → size to one sheet
        ow, oh = paper_size(paper, landscape=landscape)
        st = fit_to_physical(st, width_mm=ow, height_mm=oh)

    out = _STORE / f"export_{uuid4().hex[:8]}"
    writer = {"svg": write_svg, "png": write_png, "dxf": write_dxf,
              "pdf": write_pdf, "stl": write_stl, "blender": write_blender_script}[fmt]
    suffix = {"svg": ".svg", "png": ".png", "dxf": ".dxf",
              "pdf": ".pdf", "stl": ".stl", "blender": ".py"}[fmt]

    if paper and paper != "none":
        tiles = tile_to_paper(st, paper, landscape=landscape)
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
            for t in tiles:
                p = out.with_name(f"{out.name}_{t.name}{suffix}")
                writer(t.stencil, p)
                zf.write(p, arcname=f"sheet_{t.name}{suffix}")
        return Response(buf.getvalue(), media_type="application/zip",
                        headers={"Content-Disposition":
                                 f'attachment; filename="stencil_{paper}_sheets.zip"'})

    p = out.with_suffix(suffix)
    writer(st, p)
    media = {"svg": "image/svg+xml", "png": "image/png", "pdf": "application/pdf"}
    return FileResponse(p, media_type=media.get(fmt, "application/octet-stream"),
                        filename=f"stencil{suffix}")


def main() -> None:
    import uvicorn
    print("Stencil Lab GUI → http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="warning")


# ─── front-end (loaded from gui_index.html, with the option lists injected) ─────

def _load_page() -> str:
    template = (Path(__file__).with_name("gui_index.html")
                .read_text(encoding="utf-8"))
    return (template
            .replace("__PATTERNS__", repr(list(PATTERN_NAMES)))
            .replace("__METHODS__", repr(METHODS))
            .replace("__FORMATS__", repr(EXPORT_FORMATS))
            .replace("__PAPERS__", repr(sorted(PAPER))))


_PAGE = _load_page()


if __name__ == "__main__":
    main()
