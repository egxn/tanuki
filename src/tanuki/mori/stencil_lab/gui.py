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
import math
import zipfile
from pathlib import Path
from tempfile import mkdtemp
from uuid import uuid4

from . import (
    add_registration_marks,
    apply_frame,
    split_to_plates,
    analyze_cuttability,
    build_stencil,
    carrier_stencil,
    cut_ready,
    fit_to_physical,
    optimize_for_cutting,
    support_grid,
    paper_size,
    sheets_needed,
    Stencil,
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
from .patterns import PATTERN_GROUPS, PATTERN_NAMES
from .pipeline import _MESH_PATTERNS, _angle_for, mesh_opening_shapes
from .geometry import Dot, Polyline
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
UNITS_MM = {"mm": 1.0, "cm": 10.0, "m": 1000.0}         # → millimetres
# Reproduce the street-art line-screen recipes from docs/tutorial.md §3 — the
# front-end Presets dropdown maps each to these field values.
PRESETS = {
    "line_ref3":   {"label": "Line screen — ref 3", "method": "grayscale",
                    "pattern": "line_screen", "cell": 6, "angle": "0",
                    "contrast": 1.25, "max_duty": 0.95},
    "duotone_ref2": {"label": "Duotone lines — refs 2 & 4", "method": "duotone",
                     "pattern": "line_screen", "cell": 6, "angle": "0",
                     "contrast": 1.0, "max_duty": 0.95},
    "cmyk_lines":  {"label": "CMYK lines", "method": "cmyk",
                    "pattern": "line_screen", "cell": 6, "angle": "auto",
                    "contrast": 1.0, "max_duty": 1.0},
    "wavy_ref5":   {"label": "Wavy lines — ref 5", "method": "grayscale",
                    "pattern": "line_screen", "cell": 7, "angle": "0",
                    "contrast": 1.25, "max_duty": 0.95,
                    "wave_amplitude": 4, "wave_length": 46},
}
_STORE = Path(mkdtemp(prefix="stencil_gui_"))           # uploaded images live here
_UPLOADS: dict[str, Path] = {}


# ─── request → pattern knobs / physical size ────────────────────────────────

def _angle_params(pattern: str, angle: str, max_duty: float,
                  wave_amplitude: float, wave_length: float):
    """Parse the GUI's angle/line-screen fields → ``(angle_override, params)``.

    ``angle`` is ``"auto"`` (per-channel screen angles, the moiré-avoiding
    default) or a number that forces one angle on every layer. The extra
    ``max_duty`` / ``wave_*`` knobs only apply to ``line_screen``.
    """
    a = None if str(angle).strip().lower() in ("", "auto", "none") else float(angle)
    params: dict = {}
    if pattern == "line_screen":
        params["max_duty"] = max_duty
        if wave_amplitude and wave_amplitude > 0:
            params["wave_amplitude"] = wave_amplitude
            if wave_length and wave_length > 0:
                params["wave_length"] = wave_length
    return a, params


def _phys_dims(w: int, h: int, *, wall_mm: float = 0.0, wall_dim: str = "width",
               out_size: str = "none", paper: str = "none",
               landscape: bool = False) -> tuple[float, float] | None:
    """Target physical ``(width_mm, height_mm)`` for a ``w×h`` px design.

    Precedence: an explicit **wall** dimension wins, else fit within a standard
    **output** paper, else (when splitting) size to one **split** sheet. Returns
    ``None`` when the design has no physical size yet (pure pixels).
    """
    aspect = w / h
    if wall_mm and wall_mm > 0:
        if wall_dim == "height":
            return (wall_mm * aspect, wall_mm)
        return (wall_mm, wall_mm / aspect)
    for name in (out_size, paper):
        if name and name != "none":
            ow, oh = paper_size(name, landscape=landscape)
            f = min(ow / w, oh / h)
            return (w * f, h * f)
    return None


# ─── island analysis (rasterisation-faithful) ──────────────────────────────

def _island_factor(cell: float, w: int, h: int) -> int:
    """Supersample factor so the island raster resolves the inter-shape webs.

    A coarse screen (few pixels per cell) seals the sub-pixel material webs
    between near-tangent shapes when rasterised at native size, faking enclosed
    "islands". A 2–3× raster recovers the webs and removes those false positives.
    Capped so the analysis raster stays bounded.
    """
    f = max(1, min(3, math.ceil(15.0 / max(cell, 1.0))))
    while f > 1 and max(w, h) * f > 2200:
        f -= 1
    return f


def _layer_islands(layer, w: int, h: int, *, factor: int, min_island_area: int):
    """Topologically-enclosed material at a faithful raster → real fall-out.

    Returns ``(count, overlay_mask_native, has_border_material)``. Islands are
    enclosed material components (what actually falls out), counted on a
    ``factor``× raster so sub-pixel webs don't fake them; the overlay is reduced
    back to the native ``(w, h)`` for display.
    """
    import numpy as np
    from scipy import ndimage

    m = StencilMask.from_layer(layer, (w, h), supersample=factor)
    im = island_mask(m, min_feature_px=1.0, min_island_area=min_island_area * factor * factor)
    _, n = ndimage.label(im, structure=np.ones((3, 3), int))
    overlay = im.reshape(h, factor, w, factor).any(axis=(1, 3)) if factor > 1 else im
    mat = m.material
    has_border = bool(mat[0].any() or mat[-1].any() or mat[:, 0].any() or mat[:, -1].any())
    return n, overlay, has_border


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
             max_side, optimize, registration, carrier=False,
             threshold=0.5, duty=0.5, angle=None, params=None, strategy="legacy",
             support=False, support_width=0.0):
    separation, size = _prep(path, method=method, contrast=contrast, gamma=gamma,
                             invert=invert, max_side=max_side)
    if carrier:
        st = carrier_stencil(separation, size, carrier=pattern, threshold=threshold,
                             duty=duty, cell=cell, optimize=optimize,
                             angle=angle, params=params)
    else:
        st = build_stencil(separation, size, pattern=pattern, cell=cell,
                           angle=angle, params=params)
        if support:
            st = support_grid(st, separation, pattern=pattern, cell=cell,
                              angle=angle, params=params,
                              width=support_width or None)
        if optimize:
            st = cut_ready(st, pattern, strategy=strategy)
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
            min_feature_mm: float = 0.5,
            carrier: bool = False, threshold: float = 0.5, duty: float = 0.5,
            optimize: bool = False, angle: str = "auto", max_duty: float = 1.0,
            wave_amplitude: float = 0.0, wave_length: float = 0.0,
            wall_mm: float = 0.0, wall_dim: str = "width",
            group_blobs: bool = False, support: bool = False,
            support_width: float = 0.0, debug: bool = False) -> JSONResponse:
    """Vector preview (**WYSIWYG with export** when ``optimize``) + per-plate verdict.

    With ``optimize`` the preview shows the *cut-optimised* geometry the export
    produces (bridged / merged) — no surprises. Without it, the raw artistic
    pattern is shown and the per-plate cuttability verdict highlights the
    **islands** (pieces that fall out) vs **thin material**. The minimum feature
    is a real tool size in **mm**, converted to pixels at the chosen ``out_size``
    print scale, so "thin material" depends on how big you actually print.
    """
    path = _lookup(id)
    cap = 480 if optimize else 700               # keep the optimised path snappy
    a, params = _angle_params(pattern, angle, max_duty, wave_amplitude, wave_length)
    st = _stencil(path, method=method, pattern=pattern, cell=cell,
                  contrast=contrast, gamma=gamma, invert=invert,
                  max_side=min(max_side, cap), optimize=optimize, registration="none",
                  carrier=carrier, threshold=threshold, duty=duty,
                  angle=a, params=params, support=support, support_width=support_width,
                  strategy="grouped" if group_blobs else "legacy")
    w, h = int(round(st.width)), int(round(st.height))

    # minimum feature → pixels at the chosen print scale (else treat mm as px)
    dims = _phys_dims(w, h, wall_mm=wall_mm, wall_dim=wall_dim,
                      out_size=out_size, landscape=landscape)
    if dims:
        mm_per_px = dims[0] / w                        # physical scale
        min_feature_px = min_feature_mm / mm_per_px
        size_note = (f"{dims[0]:.0f}×{dims[1]:.0f}mm" if not wall_mm else
                     f"wall {dims[0]:.0f}×{dims[1]:.0f}mm")
        scale_note = f"@ {size_note}, {min_feature_mm}mm tool"
    else:
        min_feature_px = max(min_feature_mm, 1.0)     # mm read as px when unsized
        scale_note = f"@ {min_feature_px:.0f}px (set an output size for real mm)"

    mia = max(round(min_feature_px ** 2), round(cell ** 2))   # ignore speckle
    factor = _island_factor(cell, w, h)          # raster-faithful island count
    do_thin = min_feature_px >= 2.0              # weak-neck erosion only meaningful when sized
    layers, total_islands, unbridgeable, max_thin = [], 0, 0, 0.0
    island_layers: dict[str, "np.ndarray"] = {}
    for layer in st.layers:
        n_isl, overlay, has_border = _layer_islands(
            layer, w, h, factor=factor, min_island_area=mia)
        thin = 0.0
        if do_thin:                              # fragility (weak necks) at the print scale
            rep = analyze_cuttability(StencilMask.from_layer(layer, (w, h)),
                                      min_feature_px=min_feature_px, min_island_area=mia)
            thin = rep.thin_px / rep.material_px if rep.material_px else 0.0
        # an enclosed island can be bridged unless the plate has no frame-anchored body
        stuck = n_isl if not has_border else 0
        total_islands += n_isl
        unbridgeable += stuck
        max_thin = max(max_thin, thin)
        layers.append({"name": layer.name, "color": list(layer.color),
                       "count": len(layer), "islands": n_isl,
                       "thin": round(thin, 3), "bridgeable": n_isl > 0 and has_border})
        if overlay.any():
            island_layers[layer.name] = overlay
    # green = nothing falls out; amber = islands but all bridgeable on export; red = real loss
    status = "loss" if unbridgeable > 0 else ("bridge" if total_islands else "clean")

    svg = to_svg(st, background="white")
    if island_layers:
        # one overlay group per plate, hidden until its layer's islands checkbox
        overlay = "".join(f'<g id="isl__{name}" class="islands" style="display:none">'
                          f'{_islands_overlay(im)}</g>'
                          for name, im in island_layers.items())
        svg = svg.replace("</svg>", overlay + "</svg>")
    if debug and not carrier and pattern in _MESH_PATTERNS:
        # show the support mesh: crisp vector outlines of the cut openings
        mesh = _mesh_debug_svg(st, pattern, cell, a, support_width, w, h)
        if mesh:
            svg = svg.replace("</svg>", mesh + "</svg>")
    return JSONResponse({
        "svg": svg,
        "layers": layers,
        "primitives": st.primitive_count,
        "status": status,
        "islands": total_islands,
        "thin": round(max_thin, 3),
        "scale_note": scale_note,
    })


def _rgba_overlay(mask, color) -> str:
    """A transparent PNG of ``mask`` tinted ``color`` (RGBA), as an SVG ``<image>``."""
    import base64

    import numpy as np
    from PIL import Image

    h, w = mask.shape
    rgba = np.zeros((h, w, 4), np.uint8)
    rgba[mask] = color
    buf = io.BytesIO()
    Image.fromarray(rgba, "RGBA").save(buf, "PNG")
    b64 = base64.b64encode(buf.getvalue()).decode("ascii")
    return (f'<image x="0" y="0" width="{w}" height="{h}" '
            f'style="image-rendering:pixelated" '
            f'href="data:image/png;base64,{b64}"/>')


def _islands_overlay(mask) -> str:
    """A transparent red PNG of the island pixels, as an SVG ``<image>`` element."""
    return _rgba_overlay(mask, (230, 20, 20, 210))


def _mesh_debug_svg(st, pattern, cell, angle, support_width, w, h) -> str:
    """Crisp **vector** outlines of the support-mesh openings, one group per plate.

    Each opening is drawn as its true shape (a circle for dots, a hexagon for
    hexagons) with no fill, at the plate's screen angle, **stroked in the plate's
    own colour** so the CMYK meshes don't blur together (a lone grayscale plate
    is drawn in blue). The cut below should sit inside each opening, with a
    material wall between neighbours. Each group follows its plate's visibility.
    """
    total = len(st.layers)
    groups: list[str] = []
    for i, layer in enumerate(st.layers):
        la = angle if angle is not None else _angle_for(layer.name, i, total)
        shapes = mesh_opening_shapes(pattern, cell=cell, angle=la,
                                     width=support_width or None, size=(w, h))
        parts: list[str] = []
        for p in shapes or []:
            if isinstance(p, Dot):
                parts.append(f'<circle cx="{p.x:.1f}" cy="{p.y:.1f}" r="{p.r:.1f}"/>')
            elif isinstance(p, Polyline) and len(p.points) >= 3:
                pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in p.points)
                parts.append(f'<polygon points="{pts}"/>')
        if not parts:
            continue
        r, g, b = layer.color
        stroke = "#0af" if total == 1 else f"rgb({r},{g},{b})"
        groups.append(
            f'<g id="mesh__{layer.name}" class="mesh" fill="none" stroke="{stroke}" '
            f'stroke-width="0.7" stroke-opacity="0.95" vector-effect="non-scaling-stroke">'
            + "".join(parts) + "</g>")
    return "".join(groups)


@app.post("/api/export")
def export(id: str = Form(...), method: str = Form("grayscale"),
           pattern: str = Form("dots"), cell: float = Form(6.0),
           contrast: float = Form(1.0), gamma: float = Form(1.0),
           invert: bool = Form(False), max_side: int = Form(1000),
           fmt: str = Form("svg"), optimize: bool = Form(True),
           registration: str = Form("none"),
           out_size: str = Form("none"), landscape: bool = Form(False),
           paper: str = Form("none"),
           carrier: bool = Form(False), threshold: float = Form(0.5),
           duty: float = Form(0.5), angle: str = Form("auto"),
           max_duty: float = Form(1.0), wave_amplitude: float = Form(0.0),
           wave_length: float = Form(0.0), wall_mm: float = Form(0.0),
           wall_dim: str = Form("width"), group_blobs: bool = Form(False),
           frame_mm: float = Form(10.0), frame_width_mm: float = Form(0.0),
           support: bool = Form(False), support_width: float = Form(0.0)):
    """Heavy, on-demand render → downloadable file (or .zip of sheets).

    Physical output size is, in order of precedence, an explicit **wall**
    dimension (``wall_mm`` along ``wall_dim``), else a standard **output** paper
    (``out_size``, e.g. ``tabloid``), else one **split** sheet. ``paper`` is the
    sheet to split onto (e.g. ``a4``); ``frame_mm`` draws a per-sheet border
    inset that many mm from the printable edge (0 = off). Runs in a threadpool.
    """
    if fmt not in EXPORT_FORMATS:
        raise HTTPException(400, f"bad format {fmt!r}")
    path = _lookup(id)
    a, params = _angle_params(pattern, angle, max_duty, wave_amplitude, wave_length)
    st = _stencil(path, method=method, pattern=pattern, cell=cell,
                  contrast=contrast, gamma=gamma, invert=invert,
                  max_side=max_side, optimize=optimize, registration=registration,
                  carrier=carrier, threshold=threshold, duty=duty,
                  angle=a, params=params, support=support, support_width=support_width,
                  strategy="grouped" if group_blobs else "legacy")

    # physical output size (wall ▸ output paper ▸ split sheet), keeping aspect
    dims = _phys_dims(int(round(st.width)), int(round(st.height)), wall_mm=wall_mm,
                      wall_dim=wall_dim, out_size=out_size, paper=paper,
                      landscape=landscape)
    if dims:
        st = fit_to_physical(st, width_mm=dims[0])

    out = _STORE / f"export_{uuid4().hex[:8]}"
    writer = {"svg": write_svg, "png": write_png, "dxf": write_dxf,
              "pdf": write_pdf, "stl": write_stl, "blender": write_blender_script}[fmt]
    suffix = {"svg": ".svg", "png": ".png", "dxf": ".dxf",
              "pdf": ".pdf", "stl": ".stl", "blender": ".py"}[fmt]

    if paper and paper != "none":
        # one set of sheets *per plate* — each colour is cut on its own sheet
        plates = (split_to_plates(st, with_marks=False) if len(st.layers) > 1
                  else [st])
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
            for plate in plates:
                name = plate.layers[0].name if plate.layers else "plate"
                for t in tile_to_paper(plate, paper, landscape=landscape,
                                       frame_mm=frame_mm, frame_width_mm=frame_width_mm):
                    p = out.with_name(f"{out.name}_{name}_{t.name}{suffix}")
                    writer(t.stencil, p)
                    zf.write(p, arcname=f"{name}_{t.name}{suffix}")
        return Response(buf.getvalue(), media_type="application/zip",
                        headers={"Content-Disposition":
                                 f'attachment; filename="stencil_{paper}_plates.zip"'})

    # single-file export → frame the whole sheet and clip artwork out of the margin
    if frame_mm > 0:
        st = apply_frame(st, inset=frame_mm, width=frame_width_mm)
    p = out.with_suffix(suffix)
    writer(st, p)
    media = {"svg": "image/svg+xml", "png": "image/png", "pdf": "application/pdf"}
    return FileResponse(p, media_type=media.get(fmt, "application/octet-stream"),
                        filename=f"stencil{suffix}")


@app.get("/api/sheets")
def sheets(id: str, paper: str = "none", wall_mm: float = 0.0,
           wall_dim: str = "width", out_size: str = "none",
           landscape: bool = False, margin_mm: float = 10.0,
           overlap_mm: float = 10.0) -> JSONResponse:
    """How a wall-sized design panelises onto sheets — feeds the bottom grid.

    Cheap (no geometry): scales an empty stencil with the uploaded image's
    aspect to the requested physical size, then reports the physical dimensions
    and the ``cols × rows`` sheet grid (matching what :func:`export` produces).
    """
    path = _lookup(id)
    arr = load_image(path)
    h, w = arr.shape[:2]
    dims = _phys_dims(w, h, wall_mm=wall_mm, wall_dim=wall_dim,
                      out_size=out_size, paper=paper, landscape=landscape)
    if not dims:
        return JSONResponse({"sized": False})
    phys = fit_to_physical(Stencil(width=float(w), height=float(h)), width_mm=dims[0])
    cols = rows = 1
    if paper and paper != "none":
        cols, rows = sheets_needed(phys, paper, landscape=landscape,
                                   margin_mm=margin_mm, overlap_mm=overlap_mm)
    return JSONResponse({
        "sized": True,
        "width_mm": round(phys.width, 1), "height_mm": round(phys.height, 1),
        "paper": paper, "landscape": landscape,
        "cols": cols, "rows": rows, "sheets": cols * rows,
    })


def main() -> None:
    import uvicorn
    print("Stencil Lab GUI → http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="warning")


# ─── front-end (loaded from gui_index.html, with the option lists injected) ─────

def _load_page() -> str:
    template = (Path(__file__).with_name("gui_index.html")
                .read_text(encoding="utf-8"))
    groups = [[label, list(names)] for label, names in PATTERN_GROUPS]
    return (template
            .replace("__PATTERN_GROUPS__", repr(groups))
            .replace("__METHODS__", repr(METHODS))
            .replace("__FORMATS__", repr(EXPORT_FORMATS))
            .replace("__PAPERS__", repr(sorted(PAPER)))
            .replace("__PRESETS__", repr(PRESETS))
            .replace("__UNITS__", repr(UNITS_MM)))


_PAGE = _load_page()


if __name__ == "__main__":
    main()
