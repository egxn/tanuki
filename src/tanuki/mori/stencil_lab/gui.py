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
from .fabrication import StencilMask
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
            invert: bool = False, max_side: int = 480) -> JSONResponse:
    """Fast un-optimised vector preview + cuttability verdict."""
    path = _lookup(id)
    st = _stencil(path, method=method, pattern=pattern, cell=cell,
                  contrast=contrast, gamma=gamma, invert=invert,
                  max_side=min(max_side, 700), optimize=False, registration="none")
    rep = analyze_cuttability(StencilMask.from_stencil(st), min_feature_px=2.0)
    return JSONResponse({
        "svg": to_svg(st, background="white"),
        "layers": [{"name": l.name, "color": list(l.color), "count": len(l)}
                   for l in st.layers],
        "primitives": st.primitive_count,
        "cuttable": rep.cuttable,
        "score": round(rep.score, 3),
        "at_risk": round(rep.at_risk_fraction, 3),
        "regions": len(rep.regions),
    })


@app.post("/api/export")
def export(id: str = Form(...), method: str = Form("grayscale"),
           pattern: str = Form("dots"), cell: float = Form(6.0),
           contrast: float = Form(1.0), gamma: float = Form(1.0),
           invert: bool = Form(False), max_side: int = Form(1000),
           fmt: str = Form("svg"), optimize: bool = Form(True),
           registration: str = Form("none"), width_mm: float = Form(0.0),
           paper: str = Form("none")):
    """Heavy, on-demand render → downloadable file (or .zip of sheets).

    Runs in FastAPI's threadpool (sync def), so the event loop stays responsive.
    """
    if fmt not in EXPORT_FORMATS:
        raise HTTPException(400, f"bad format {fmt!r}")
    path = _lookup(id)
    st = _stencil(path, method=method, pattern=pattern, cell=cell,
                  contrast=contrast, gamma=gamma, invert=invert,
                  max_side=max_side, optimize=optimize, registration=registration)
    if width_mm and width_mm > 0:
        st = fit_to_physical(st, width_mm=width_mm)

    out = _STORE / f"export_{uuid4().hex[:8]}"
    writer = {"svg": write_svg, "png": write_png, "dxf": write_dxf,
              "pdf": write_pdf, "stl": write_stl, "blender": write_blender_script}[fmt]
    suffix = {"svg": ".svg", "png": ".png", "dxf": ".dxf",
              "pdf": ".pdf", "stl": ".stl", "blender": ".py"}[fmt]

    if paper and paper != "none":
        if not (width_mm and width_mm > 0):                # need a physical size
            from .sizing import printable_area
            bw, _ = printable_area(paper)
            st = fit_to_physical(st, width_mm=bw)
        tiles = tile_to_paper(st, paper)
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
