# Stencil Lab

Image → stencil pipeline. Turns photographs and illustrations into artistic
halftone layers and fabrication-ready vector patterns.

> The full product vision lives in [`../README.md`](../README.md). This file
> tracks what is **actually implemented**, phase by phase.
>
> 📖 **Usage guide with copy-paste examples: [`docs/usage.md`](docs/usage.md).**
> 🖼️ **Visual tutorial (every option shown on a photo): [`docs/tutorial.md`](docs/tutorial.md).**

## Pipeline

```
Image → Adjustments → Colour Separation → Pattern → Cut-Optimization → Export
```

Everything between load and export is **numpy-native** (float arrays in
`[0, 1]`) and **backend-agnostic** (a tiny `geometry` vocabulary of `Dot` /
`Polyline` / `Layer` / `Stencil`). PIL is only touched at image decode/encode.

Because a stencil exists to be *cut*, the one-shot `halftone_stencil` (and the
CLI) **optimize for cutting by default** — islands that would fall out are
removed or bridged and the output is fabrication-ready cut polygons. Pass
`optimize=False` (CLI `--no-optimize`) for the raw artistic pattern.

## Quickstart

```python
from tanuki.mori import stencil_lab as sl

# One-shot: image → layered CMYK halftone → SVG
stencil = sl.halftone_stencil("photo.jpg", method="cmyk", cell=6)
sl.write_svg(stencil, "photo.svg", background="white")
```

Step by step:

```python
arr = sl.load_image("photo.jpg")
arr = sl.adjustments.contrast(arr, 1.3)
arr = sl.adjustments.gamma(arr, 0.9)

sep = sl.separation.cmyk(arr)          # → cyan / magenta / yellow / key planes
stencil = sl.build_stencil(sep, (arr.shape[1], arr.shape[0]), cell=8)
sl.write_svg(stencil, "out.svg")
```

CLI:

```bash
python -m tanuki.mori.stencil_lab photo.jpg -o photo.svg \
    --method cmyk --cell 6 --scale 1.0 --background white
```

## Modules

| Module           | What it does |
|------------------|--------------|
| `image_io`       | Load/save images as float `[0,1]` numpy arrays; grayscale, coverage, resize |
| `adjustments`    | brightness, contrast, gamma, invert, threshold, posterize, blur, sharpen, edges |
| `separation`     | grayscale, rgb, cmyk, duotone, tritone → ink-coverage planes (`Separation`) |
| `patterns/`      | pattern generators + `PATTERNS` registry — see below |
| `geometry`       | `Dot`, `Polyline`, `Layer`, `Stencil` — backend-neutral 2-D primitives |
| `export/`        | serialise a `Stencil` → SVG / PNG / DXF / PDF / STL / Blender |
| `registration`   | registration marks, alignment guides, `split_to_plates` (multi-layer) |
| `tiling`         | panelise a canvas into plotter-bed tiles (`tile_stencil`) with overlap + crop marks |
| `sizing`         | physical size in mm (`fit_to_physical`, `scale_stencil`) + print on sheets/pliegos (`poster`, `tile_to_paper`) |
| `gui`            | optional FastAPI web GUI — live SVG preview, layer toggles, cuttability verdict, export |
| `fabrication/`   | `StencilMask`, island detection, bridges, min-feature, fabrication checks, `optimize_mask`, **`analyze_cuttability`** |
| `pipeline`       | `build_stencil`, `halftone_stencil` (cut-optimized by default), `optimize_for_cutting` |

Coordinate system: top-left origin, **y grows down** (matches image pixels and
SVG), units abstract.

## Patterns

Selected by name through the `PATTERNS` registry (uniform `(plane, *, cell,
angle)` interface), or called directly. They're grouped by how well they suit
the project's goal — a **cuttable** stencil (see `PATTERN_GROUPS`).

**Recommended** — fill an *area* modulated by coverage, so they read as a proper
stencil and optimise cleanly:

| Name          | What it draws |
|---------------|---------------|
| `dots`        | AM dot screen, area ∝ coverage |
| `hexagons`    | hex-grid halftone, cell size ∝ coverage |
| `line_screen` | continuous amplitude-modulated line ribbons (street-art look; supports `wave`) |
| `splotches`   | irregular ink blobs sized by coverage (shadows, B&W) |

**Self-bridging (threshold carrier)** — cut only inside the dark regions,
leaving the gaps as a connected material lattice ⇒ always cuttable:

| Name              | What it draws |
|-------------------|---------------|
| `threshold_lines` | threshold ∩ a line carrier (`duty` controls cut vs held) |

**Experimental** — stroke / cell / contour screens. On their own they leave
fragile thin webs or enclosed cells; they're most useful as **carriers**
(threshold ∩ pattern), which roughly halves the fragile material — see below.

| Name | | Name | |
|------|--|------|--|
| `lines` | parallel lines, width ∝ coverage | `radial` | rays from a centre |
| `circular` | concentric variable-width arcs | `honeycomb` | hex outlines |
| `crosshatch` | layered line sets | `topographic` | iso-coverage contours |
| `sine` | rows of sine waves | `stipple` | random dots, density ∝ coverage |
| `zigzag` | triangle-wave variant | `voronoi` | Voronoi cell web |
| `spiral` | one Archimedean spiral | | |

### Patterns as threshold carriers

Any pattern can be used as a **carrier**: instead of cutting the pattern's own
strokes, threshold the image and cut only the intersection with the carrier
texture (rendered at a fixed `duty` so it always leaves gaps) — the carrier's
gaps + the highlights stay as a connected material lattice (the bridges).

```python
sl.carrier_stencil(sep.grayscale(arr), (w, h), carrier="honeycomb", threshold=0.5)
sl.halftone_stencil("photo.jpg", pattern="voronoi", carrier=True)   # one-shot
# CLI:  … --pattern honeycomb --carrier --threshold 0.5
```

This is the recommended way to use the *Experimental* screens: used directly
their thin strokes get erased by optimisation (near-empty), but as carriers they
produce substantial, **self-bridging** geometry — `carrier_mask` /
`carrier_stencil` generalise `threshold_lines` to any pattern.

## Roadmap

- [x] **Phase 1 — Image pipeline.** I/O, adjustments, separation
  (RGB/CMYK/gray/duotone/tritone), dot halftone with screen angles, geometry
  model, SVG export, CLI.
- [x] **Phase 2 — Patterns.** Traditional line / circular / crosshatch
  halftones + experimental family (sine, zigzag, spiral, radial, hexagons,
  honeycomb, topographic contours, stipple, **voronoi** via `scipy.spatial`),
  unified `PATTERNS` registry wired into the pipeline & CLI.
- [x] **Phase 3 — Stencil optimization.** `StencilMask` (cut/material raster),
  island detection, automatic bridge generation (EDT-based), minimum feature
  size + reinforcement (small-hole/island removal, thin-neck detection),
  fabrication checks, `optimize_mask` orchestrator, and mask → cut-polygon
  vectorisation (Moore boundary tracing **with inner-hole tracing**, so annular
  cuts vectorise as true rings) honoured by every exporter. `cut_ready` picks
  the strategy by pattern: **stable** patterns get `cut_cleanup` (vector — keeps
  the shapes verbatim, only drops sub-feature ones, so the export matches the
  preview), while experimental/raster designs get the bridge/merge optimiser.
- [x] **Phase 4 — Blender geometry.** `to_blender_script` / `write_blender_script`
  emit a standalone `bpy` script that builds one curve object per layer (dots →
  polygon circles, polylines → poly splines), with 2-D fill and Z extrusion for
  solid extruded stencils, Y-flip + scale, and per-layer collections/colours.
  Verified by running the output in headless Blender. *(Uses a direct `bpy`
  emitter rather than the Geometry-Nodes DSL: the DSL primitives are parametric
  with no arbitrary-polygon node, so it can't represent halftone geometry.)*
- [x] **Phase 5 — Registration & export.** Registration marks (crosshair /
  target / corner) stamped on every plate, `split_to_plates` for multi-layer
  output, and dependency-free exporters: **PNG** (colour raster), **DXF** (R12
  ASCII, per-layer), **PDF** (hand-written vector), **STL** (ear-clipping
  triangulation + extrusion — verified importing into Blender).
- [x] **Phase 6 — Canvas tiling.** `tile_stencil` panelises a canvas larger than
  the plotter bed into a grid of origin-aligned tiles with configurable
  **overlap** and **crop marks**. Exact clipping: Liang–Barsky (strokes),
  Sutherland–Hodgman (filled polygons + holes), centre-membership (dots).
  Any export format can be written per tile (`--tile WxH` in the CLI).
- [x] **Phase 7 — Cuttability analysis.** `analyze_cuttability` decides whether a
  stencil can be cut **without losing information** via morphological
  reconstruction: erode material by the min feature, anchor frame-touching
  cores, reconstruct the robustly-connected (*safe*) material — the rest is
  *at-risk*, split into **islands** (`island_count` / `island_mask` — pieces
  that fall out = real information loss) and **thin material** (`thin_px` —
  fragility, scale-dependent). Speckle below `min_island_area` is ignored.
  Reports `score`, sub-kerf holes and a verdict; CLI `--analyze` (exit 0/1).
  Analyse plates separately for multi-ink designs (each is cut on its own sheet).
- [x] **Phase 8 — Physical size & sheets.** `fit_to_physical` / `scale_stencil`
  put the design into millimetres (SVG `mm`, PDF mm→points, DXF/STL in mm);
  `poster` / `tile_to_paper` / `sheets_needed` split a large design across real
  paper (A0–A6, carta, tabloid, **pliego** + fractions) with margins, overlap
  and crop marks. CLI `--width-mm`, `--paper`, `--landscape`. Resolution (DPI)
  is decoupled from size — screen in pixels, then scale.
- [x] **Phase 9 — Web GUI (optional).** A small FastAPI app — `gui.py` +
  `gui_index.html`, run with `python -m tanuki.mori.stencil_lab.gui` — with live
  **vector** preview (zoom + spinner), toggleable `<g>` plates, a **show-islands**
  red overlay, a **carrier mode** toggle (+ threshold), a **per-plate, size-aware**
  cuttability verdict (islands vs thin material, scaled by output size +
  min-feature-mm), and a background export with an **output paper size +
  orientation** and optional **split on sheets** (→ `.zip`).

## Dependencies

The tanuki **core DSL needs nothing extra**. The Stencil Lab's dependencies are
self-contained here and only installed when you want the lab:

```bash
cd src/tanuki/mori/stencil_lab
python3 -m venv .venv && source .venv/bin/activate   # recommended on Ubuntu (PEP 668)

pip install -r requirements.txt        # image pipeline: numpy, scipy, Pillow
pip install -r requirements-gui.txt     # + the web GUI: fastapi, uvicorn, python-multipart
```

Equivalently, from the package root: `pip install -e ".[stencil]"` (pipeline) or
`pip install -e ".[gui]"` (pipeline + GUI). On Ubuntu, prefer a venv over
`pip install --break-system-packages …`.

## GUI

```bash
pip install -r src/tanuki/mori/stencil_lab/requirements-gui.txt   # or: pip install -e ".[gui]"
cd src/tanuki                                  # the tanuki package must be importable
python -m tanuki.mori.stencil_lab.gui          # → http://127.0.0.1:8000
```

Upload a photo, tweak separation / pattern / cell / tone with live SVG preview,
toggle colour plates on/off, read the cuttability verdict, then export to any
format (with optional physical width and paper splitting).

## Performance

`optimize_for_cutting` (and the vectoriser) work per-component inside
bounding boxes (`find_objects`) and extract holes from one global
`binary_fill_holes`, so a CMYK halftone optimises in seconds rather than tens of
seconds. The GUI's live preview skips optimisation and runs at low resolution
(~0.3 s); the heavy optimised export runs in FastAPI's threadpool.

## Tests

```bash
cd src/tanuki && python -m pytest tests/test_stencil_lab.py
```
