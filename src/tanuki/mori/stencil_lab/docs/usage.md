# Stencil Lab — Usage Guide

A practical, copy-paste walkthrough of the Stencil Lab pipeline. Every snippet
is runnable as-is (assuming `tanuki` is importable and you have an image to
point at).

```
Image → Adjustments → Colour Separation → Pattern → (Optimization) → Export
```

Contents:

1. [Install & import](#1-install--import)
2. [The data model](#2-the-data-model)
3. [Loading & saving images](#3-loading--saving-images)
4. [Image adjustments](#4-image-adjustments)
5. [Colour separation](#5-colour-separation)
6. [Pattern generation](#6-pattern-generation)
7. [Building & exporting a stencil](#7-building--exporting-a-stencil)
8. [Fabrication & optimization](#8-fabrication--optimization)
9. [The one-shot pipeline](#9-the-one-shot-pipeline)
10. [Command line](#10-command-line)
11. [Recipes](#11-recipes)

---

## 1. Install & import

The Stencil Lab's dependencies live with the lab (the tanuki core DSL needs
none of them):

```bash
cd src/tanuki/mori/stencil_lab
pip install -r requirements.txt          # numpy, scipy, Pillow
# add -r requirements-gui.txt for the web GUI
```

Equivalently from the package root: `pip install -e ".[stencil]"`. On Ubuntu
use a venv (`python3 -m venv .venv && source .venv/bin/activate`) rather than
`--break-system-packages`.

```python
from tanuki.mori import stencil_lab as sl
from tanuki.mori.stencil_lab import adjustments as adj
from tanuki.mori.stencil_lab import separation as sep
```

Everything between loading and exporting works on **float64 numpy arrays in
`[0, 1]`** and a tiny set of **backend-neutral geometry primitives**. PIL is
only used at image decode/encode.

---

## 2. The data model

Two layers of representation:

**Raster** — numpy arrays in `[0, 1]`:

| Shape         | Meaning                                  |
|---------------|------------------------------------------|
| `(H, W)`      | grayscale *tone* (0 = black, 1 = white)  |
| `(H, W, 3)`   | RGB                                      |
| `(H, W, 4)`   | RGBA                                     |

*Coverage* is `1 - tone` (dark = more ink). Patterns consume coverage planes.

**Vector** — from `stencil_lab.geometry`:

```python
from tanuki.mori.stencil_lab.geometry import Dot, Polyline, Layer, Stencil, polygon

Dot(x, y, r)                       # filled circle
Polyline(points, closed=False,     # open path or (closed+fill) polygon
         width=1.0, fill=False,
         holes=[])                 # inner rings punched out (even-odd fill)
polygon([(0,0),(10,0),(5,8)])      # shorthand: closed + filled
polygon(outer, holes=[ring])       # filled polygon with a hole

layer = Layer("key", color=(0, 0, 0))
layer.add(Dot(5, 5, 2))            # accepts one primitive or an iterable

st = Stencil(width=300, height=200, units="mm")
st.layer("cyan", color=(0, 174, 239)).add(...)   # get-or-create by name
st.primitive_count                                # total primitives
```

Coordinate system: **top-left origin, y grows down** (same as image pixels and
SVG). Units are abstract; `Stencil.units` is just a label exporters annotate.

---

## 3. Loading & saving images

```python
arr = sl.load_image("photo.jpg")            # native mode → (H,W,3) here
gray = sl.load_image("photo.jpg", mode="L") # force grayscale → (H,W)

g = sl.to_grayscale(arr)                     # any array → (H,W) tone
cov = sl.coverage(arr)                       # any array → (H,W) ink coverage

small = sl.resize(arr, max_side=1000)        # downscale longest side, keep aspect
sl.save_image(cov, "coverage_preview.png")   # float [0,1] → PNG
```

Supported inputs: `sl.SUPPORTED_FORMATS` → `.jpg .jpeg .png .tif .tiff .bmp`
(PIL handles more; these are the advertised ones).

---

## 4. Image adjustments

All return a **new** array in `[0, 1]`; inputs are never mutated. Pointwise ops
work on any shape; spatial ops (blur/sharpen/edges) run per channel.

```python
adj.brightness(arr, 0.1)     # add a constant (-1..1)
adj.contrast(arr, 1.4)       # scale about mid-grey (1.0 = unchanged)
adj.gamma(arr, 0.8)          # <1 brighter, >1 darker
adj.invert(arr)              # negative (preserves alpha)

adj.threshold(arr, 0.5)      # binarise → only 0.0 / 1.0
adj.posterize(arr, levels=4) # quantise tones into N steps

adj.blur(arr, radius=2)          # separable Gaussian
adj.sharpen(arr, amount=1.0, radius=2)  # unsharp mask
adj.edges(arr)               # Sobel edge magnitude → bright = strong edge
```

Chaining is just function composition:

```python
prepped = adj.gamma(adj.contrast(sl.to_grayscale(arr), 1.3), 0.9)
```

---

## 5. Colour separation

A *separation* splits an image into named **ink-coverage planes** (`1.0` = full
ink), each tagged with a preview colour. Returns a `Separation` (iterable list
of `Channel(name, plane, color)`).

```python
sep.grayscale(arr)   # → ["key"]                          single black plate
sep.rgb(arr)         # → ["red", "green", "blue"]         additive light
sep.cmyk(arr)        # → ["cyan","magenta","yellow","key"] print process
sep.duotone(arr, shadow=(20,20,90), base=(230,80,60))     # riso 2-colour
sep.tritone(arr)     # → ["shadow", "mid", "highlight"]
```

Working with channels:

```python
s = sep.cmyk(arr)
s.names                      # ['cyan', 'magenta', 'yellow', 'key']
s["key"].plane               # the K coverage array (H, W)
s["key"].color               # (35, 31, 32)
for ch in s:
    print(ch.name, float(ch.plane.mean()))
```

`rgb` and `cmyk` need a colour image. The one-shot pipeline auto-promotes
grayscale input to 3 channels for those methods; if calling directly, do it
yourself: `np.repeat(gray[..., None], 3, axis=-1)`.

---

## 6. Pattern generation

A pattern turns one coverage plane into vector primitives in pixel coordinates.
Use the **registry** for a uniform interface, or call a generator directly for
its full parameter set.

```python
from tanuki.mori.stencil_lab.patterns import PATTERNS, PATTERN_NAMES, generate

PATTERN_NAMES
# ('dots', 'lines', 'circular', 'crosshatch', 'sine', 'zigzag', 'spiral',
#  'radial', 'hexagons', 'honeycomb', 'topographic', 'stipple', 'voronoi',
#  'splotches', 'threshold_lines', 'line_screen')

plane = sep.cmyk(arr)["key"].plane
prims = generate(plane, "sine", cell=10, angle=0)   # uniform (plane, *, cell, angle)
prims = PATTERNS["dots"](plane, cell=8, angle=45)    # same thing

# extra generator knobs are forwarded as **params (ignored by patterns that
# don't take them) — e.g. line_screen's max_duty / wave_amplitude / wave_length
prims = generate(plane, "line_screen", cell=6, angle=0,
                 max_duty=0.95, wave_amplitude=4, wave_length=46)
```

| Name          | Output      | Key params (direct call) |
|---------------|-------------|--------------------------|
| `dots`        | `Dot`       | `cell, angle, scale, min_coverage` |
| `lines`       | `Polyline`  | `spacing, angle, step, max_width` |
| `circular`    | `Polyline`  | `spacing, center, step_deg` |
| `crosshatch`  | `Polyline`  | `spacing, step, line_width, passes` |
| `sine`        | `Polyline`  | `spacing, wavelength, amplitude` |
| `zigzag`      | `Polyline`  | `spacing, wavelength, amplitude` |
| `spiral`      | `Polyline`  | `spacing, center, step_deg, max_width` |
| `radial`      | `Polyline`  | `spacing, center, step, max_width` |
| `hexagons`    | `Polyline`  | `cell, scale, min_coverage` |
| `honeycomb`   | `Polyline`  | `cell, threshold, width` |
| `topographic` | `Polyline`  | `cell, levels, width` |
| `stipple`     | `Dot`       | `cell, radius, jitter, seed` |
| `voronoi`     | `Polyline`  | `spacing, base, jitter, width, seed` |
| `splotches`   | `Polyline`  | `cell, scale, irregularity, jitter, vertices, seed` |
| `threshold_lines` | `Polyline` | `threshold, period, duty, angle` |
| `line_screen` | `Polyline`  | `period, angle, step, min_coverage, max_duty, wave_amplitude, wave_length` |

Direct calls give you everything:

```python
from tanuki.mori.stencil_lab import (
    halftone_dots, sine_wave, topographic, splotches, threshold_lines,
)

halftone_dots(plane, cell=8, angle=45, scale=1.0, min_coverage=0.02)
sine_wave(plane, spacing=10, wavelength=24, amplitude=6)
topographic(plane, cell=6, levels=(0.25, 0.5, 0.75))

# shadow blobs (B&W): organic ink that grows with darkness
splotches(plane, cell=10, scale=1.1, irregularity=0.35)

# threshold cut that always self-bridges: only `duty` of each `period` is cut,
# the rest stays as material ribs → cuttable even where it encloses material.
threshold_lines(plane, threshold=0.5, period=8, duty=0.5, angle=0)
```

**Screen angles** matter for colour: rotate each plate to a different angle to
avoid moiré. The pipeline does this automatically (15° / 75° / 0° / 45° for
CMYK); see `pipeline._CMYK_ANGLES`. Angle-agnostic patterns (circular, spiral,
hexagons, …) simply ignore it.

### Carrier mode (threshold ∩ pattern)

The *Experimental* screens (lines, circular, sine, honeycomb, voronoi, …) leave
fragile thin webs when cut directly. Use them as a **carrier** instead: cut only
where the image is dark *and* inside the pattern, leaving the pattern's gaps as a
connected material lattice (the bridges) — a self-bridging stencil. This
generalises `threshold_lines` to any pattern.

```python
# boolean cut mask = threshold ∩ pattern (rendered at fixed `duty` so gaps remain)
cut = sl.carrier_mask(plane, "honeycomb", threshold=0.5, duty=0.5, cell=8)

# a full layered stencil (per channel), optimised + vectorised to cut polygons
st = sl.carrier_stencil(sep.grayscale(arr), (w, h), carrier="honeycomb", threshold=0.5)

# one-shot / CLI
st = sl.halftone_stencil("photo.jpg", pattern="voronoi", carrier=True, threshold=0.5)
#   python -m tanuki.mori.stencil_lab photo.jpg --pattern honeycomb --carrier --threshold 0.5
```

Measured benefit (vs cutting the pattern directly): honeycomb thin material
91 % → 47 %, voronoi 83 % → 45 %, and the result stays cuttable.

---

## 7. Building & exporting a stencil

`build_stencil` renders every channel of a separation into a layered
`Stencil` with the chosen `pattern`, applying conventional per-channel screen
angles. Pass `angle=` to force a single screen angle on every plate instead
(e.g. `angle=0` for the horizontal `line_screen` look), and `params={…}` to
forward generator-specific knobs through to the pattern.

```python
s = sep.cmyk(arr)
h, w = arr.shape[:2]
stencil = sl.build_stencil(s, (w, h), pattern="dots", cell=8, units="px")

# horizontal line-screen with extra knobs forwarded to the generator
ink = sl.build_stencil(sep.grayscale(arr), (w, h), pattern="line_screen",
                       cell=6, angle=0, params={"max_duty": 0.95})

sl.write_svg(stencil, "out.svg", background="white")  # → file
svg_str = sl.to_svg(stencil)                            # → string
```

Each layer becomes an SVG `<g>` group named after the channel and filled with
its preview colour, so layers can be toggled or sent to a cutter independently.

**Blender** — the same stencil can be emitted as a standalone `bpy` script that
builds real curve / solid geometry:

```python
sl.write_blender_script(
    stencil, "stencil.py",
    scale=0.01,     # units (e.g. mm) per source pixel
    extrude=0.5,    # solid half-thickness — 0.0 leaves flat curves
    fill=True,      # cap the curve faces (needed for solids)
)
```

Then build it (one curve object per layer, in its own collection):

```bash
blender --background --python stencil.py
```

> This uses a direct `bpy` emitter, not the Geometry-Nodes DSL: the DSL's
> primitives are parametric (circle, line, star, …) with no arbitrary-polygon
> node, so it can't represent halftone geometry. Coordinates are flipped to
> Blender's y-up and scaled; geometry sits on XY and extrudes along +Z.

**More formats** — all dependency-free:

```python
sl.write_png(stencil, "preview.png")                 # composited colour raster
sl.write_dxf(stencil, "cut.dxf")                      # R12 ASCII, one DXF layer per channel
sl.write_pdf(stencil, "proof.pdf")                    # single-page vector PDF
sl.write_stl(stencil, "plate.stl", thickness=1.5)     # extruded solid (filled shapes only)
```

| Format   | Vector? | Notes |
|----------|---------|-------|
| `svg`    | ✓       | layers as `<g>` groups; cutter-ready |
| `png`    | raster  | `supersample=N` for anti-aliasing |
| `dxf`    | ✓       | per-layer; dots → `CIRCLE`, polylines → `POLYLINE` |
| `pdf`    | ✓       | bézier circles, filled/stroked paths |
| `stl`    | 3-D     | ear-clip triangulation + extrusion of **filled** shapes |
| `blender`| 3-D     | standalone `bpy` script |

### Registration & multi-layer plates

Marks placed identically on every plate so colours line up:

```python
sl.add_registration_marks(stencil, kind="target")    # crosshair | target | corner
```

Explode into one single-layer stencil per channel (each carrying the marks),
ready to cut/print separately:

```python
for plate in sl.split_to_plates(stencil, kind="target"):
    name = plate.layers[0].name
    sl.write_dxf(plate, f"plate_{name}.dxf")
```

### Tiling for the plotter bed

When the design is bigger than the cutter can handle, split it into tiles that
fit the bed. Each tile is clipped, given crop marks, and moved to its own
`(0, 0)` origin:

```python
tiles = sl.tile_stencil(
    stencil, 600, 800,    # plotter bed in px (width × height)
    overlap=20,           # shared margin so seams glue together
    crop_marks=True,      # corner ticks on a "crop" layer for alignment
)
for t in tiles:           # t.row / t.col / t.rect / t.stencil
    sl.write_dxf(t.stencil, f"cut_{t.name}.dxf")   # → cut_r0c0.dxf, …
```

Clipping is exact — strokes are Liang–Barsky clipped, filled polygons (and
their holes) Sutherland–Hodgman clipped, dots kept by centre membership. Set
`overlap` ≥ your largest dot/stroke so nothing is dropped at a seam.
`sl.tile_grid(w, h, bed_w, bed_h, overlap=…)` returns just the rectangle grid.

### Physical size & printing on sheets

`tile_stencil` works in pixels; to print at a real **size**, scale the geometry
to millimetres first. The exporters then emit real dimensions (SVG `mm`, PDF
mm→points, DXF/STL in mm) so output prints 1:1.

```python
big = sl.fit_to_physical(stencil, width_mm=700)   # 70 cm wide, units="mm" (keeps aspect)
big = sl.scale_stencil(stencil, 2.0, units="mm")  # explicit factor
sl.write_svg(big, "poster.svg")                   # 70 cm-wide SVG
```

Split a large design across real sheets — A0–A6, `carta`, `tabloid`, and the
Latin-American `pliego` (70×100 cm) and fractions:

```python
sl.sheets_needed(big, "a4")                        # → (cols, rows)
tiles = sl.tile_to_paper(big, "a3", margin_mm=10, overlap_mm=10)
tiles = sl.tile_to_paper(big, "a3", frame_mm=10)   # clear a 1 cm margin on each sheet
# add frame_width_mm=0.5 to also draw a visible border (a cut path)

# one call: size by physical width or by sheet count, then tile
scaled, tiles = sl.poster(stencil, "a4", width_mm=420)   # ≈ A2 across A4
scaled, tiles = sl.poster(stencil, "pliego", cols=2)     # 2 pliegos wide
for t in tiles:
    sl.write_pdf(t.stencil, f"sheet_{t.name}.pdf")        # each in mm, 1:1

# multi-ink: split per colour plate first, so each ink cuts on its own sheet
for plate in sl.split_to_plates(big, with_marks=False):   # cyan / magenta / …
    name = plate.layers[0].name
    for t in sl.tile_to_paper(plate, "medio_pliego"):
        sl.write_pdf(t.stencil, f"{name}_{t.name}.pdf")   # e.g. cyan_r0c0.pdf
```

Resolution is independent of size — generate the screen in pixels
(`max_side` / `cell` set the dot pitch), then scale to mm. `sl.px_for_print(
longest_mm, dpi)` returns a pixel `max_side` for a target DPI; `sl.paper_size(
name, landscape=…)` and `sl.PAPER` expose the sheet table.

---

## 8. Fabrication & optimization

A printed stencil is a physical sheet with material removed where ink passes.
Phase 3 models that as a **`StencilMask`**: a boolean raster where `True` = cut
(hole) and `False` = material. This is where you catch the things that ruin a
real cut — islands that fall out, slivers that tear, speckle that won't cut.

```python
from tanuki.mori.stencil_lab import fabrication as fab

# build a mask: from a coverage plane (dark → cut) …
mask = fab.StencilMask.from_coverage(cov, threshold=0.5)
# … or by rasterising a generated Stencil's geometry
mask = fab.StencilMask.from_stencil(stencil)
```

**Island detection** — enclosed material (the middle of an "O") that would fall
out:

```python
for isl in fab.detect_islands(mask):
    print(isl.id, isl.area, isl.centroid)
```

**One-shot optimize** — clean speckle, drop fragile fragments, bridge the rest,
re-check:

```python
opt, report = fab.optimize_mask(
    mask,
    min_hole_area=4,      # fill cut blobs smaller than this (px)
    min_island_area=16,   # cut away material islands smaller than this
    bridge_width=2.0,     # width of bridges that tie islands to the body
    min_feature_px=2.0,   # fabrication-check threshold
)
print(report)            # islands before/after, bridges, check summary
report.ready             # True when every check passed
```

**Individual steps**, if you want control:

```python
mask, n = fab.remove_small_holes(mask, min_area=4)
mask, n = fab.remove_small_islands(mask, min_area=16)
mask, n = fab.add_bridges(mask, width=2.0)
thin    = fab.thin_material(mask, min_width=2.0)   # boolean mask of slivers
d       = fab.min_hole_diameter(mask)              # smallest hole (px)
```

**Fabrication checks** — `dict[str, list[str]]`, empty list = passed (same
convention as the halo_maps validators):

```python
results = fab.fabrication_checks(mask, min_feature_px=2.0)
failed  = {k: v for k, v in results.items() if v}
print(fab.summarize(results))
```

**Cuttability analysis** — *can it be cut without losing information?* Erodes
the material by the minimum feature, anchors the cores touching the frame and
reconstructs what is robustly connected; the rest is **at-risk** (islands that
fall out + weak necks that tear):

```python
report = fab.analyze_cuttability(mask, min_feature_px=2.0, min_island_area=None)
report.loses_information  # True ⇒ some island ≥ min feature falls out
report.island_count       # islands (pieces that fall out) — the real loss
report.thin_px            # material in thin/fragile areas (may tear)
report.score              # fraction of material that survives (1.0 = perfect)
for r in report.regions:
    r.kind                # "isolated" (island) | "weak-neck" (thin)
    r.area, r.bridgeable  # px, and whether a bridge can rescue it
print(report.summary())
```

`min_island_area` (default `round(min_feature_px**2)`) drops sub-feature
**speckle** — the flecks trapped between near-touching halftone dots — so the
island count reflects real fall-out, not thousands of negligible specks. The
report cleanly separates **islands** (information loss) from **thin material**
(fragility, which the optimised export bridges away).

For a **multi-ink** design, analyse each plate on its own (it's cut on its own
sheet) rather than the union: `analyze_cuttability(StencilMask.from_layer(layer,
size))`. The raw `safe_material` / `at_risk_material` masks are available if you
want to visualise them. `analyze_cuttability` is read-only — pair it with
`optimize_mask` to *fix* what it reports.

**Back to vectors** — the optimised mask becomes cut polygons for export:

```python
mask.save_preview("sheet.png")          # quick raster preview
cut = opt.to_stencil(name="cut")        # → Stencil of closed cut polygons
sl.write_svg(cut, "cut.svg")            # ready for the cutter
```

> Vectorisation traces each cut blob's outer boundary (Moore-neighbour) **and
> its inner holes** (enclosed material), attached via `Polyline.holes`. An
> annular cut becomes a true ring — every exporter honours the holes (SVG/PDF
> even-odd fill, STL cavity walls, DXF/Blender nested rings, PNG masking).

## 9. The one-shot pipeline

```python
stencil = sl.halftone_stencil(
    "photo.jpg",
    method="cmyk",      # cmyk | rgb | grayscale | duotone | tritone
    pattern="dots",     # any name in PATTERN_NAMES
    cell=6,
    max_side=1000,      # downscale first (None to keep full resolution)
    # optimize=True,    # ← default: make it cuttable (see below)
)
sl.write_svg(stencil, "photo.svg", background="white")
```

**Cut-optimized by default.** A stencil exists to be *cut*, so the one-shot
generation runs [`optimize_for_cutting`](#8-fabrication--optimization) on every
layer — islands that would fall out are removed or bridged and the result comes
back as **closed cut polygons** rather than raw dots/strokes. The verdict can be
confirmed with `analyze_cuttability`.

```python
raw = sl.halftone_stencil("photo.jpg", optimize=False)      # artistic pattern
cut = sl.halftone_stencil("photo.jpg")                       # cut-ready (default)

# tune the optimization through the same call
cut = sl.halftone_stencil("photo.jpg", min_feature_px=2, bridge_width=3,
                          min_hole_area=4, min_island_area=16)

# or optimize a stencil you built yourself
cut = sl.optimize_for_cutting(sl.build_stencil(sep.cmyk(arr), (w, h)))
```

> A fine photographic halftone can't become a perfect single-piece stencil
> (the thin web between dots stays fragile) — optimization removes every
> *isolated* island and bridges the rest; use a coarser `cell`, a connected
> pattern, or bolder art if `analyze_cuttability` still flags too much.

**Grouped cut strategy (opt-in).** Pass `strategy="grouped"` for a
pattern-specific cut prep instead of the default raster bridge/merge. Line
screens (`line_screen` / `lines` / `threshold_lines`) are left **exactly as
drawn** (they already self-bridge), and the shape screens (`dots`, `hexagons`,
`stipple`, `splotches`) have their **touching** shapes merged into one clean cut
mass while isolated shapes stay verbatim — so a dark blob becomes a single
coherent polygon rather than a pile of overlapping circles. The default
(`strategy="legacy"`) is unchanged.

```python
cut = sl.halftone_stencil("photo.jpg", pattern="dots", strategy="grouped")

# or apply it to a stencil you built yourself
masses = sl.merge_touching_shapes(sl.build_stencil(sep.grayscale(arr), (w, h),
                                                   pattern="hexagons"))
cut = sl.cut_grouped(my_stencil, "dots")    # full per-pattern dispatch
```

**Support grid / mesh (opt-in).** `support_grid` confines each layer's cut to a
regular **mesh** — like a metal grid or a die over leather: a single connected
lattice of material with a hole at every pattern cell. The cut is intersected
with the holes (`cut ∩ openings`), so a material **wall** (`width` px) always
survives between neighbouring cells — the plate stays one connected piece and
**nothing falls out**, while the cut inside each hole still follows the pattern
(dot / hex size ∝ coverage). Defined for the regular-lattice `dots` and
`hexagons` screens; other patterns are returned unchanged.

```python
s = sep.grayscale(arr)
st = sl.build_stencil(s, (w, h), pattern="dots", cell=8)
st = sl.support_grid(st, s, pattern="dots", cell=8, width=2)   # mesh wall = 2 px
cut = sl.cut_ready(st, "dots")
```

On the tanuki dots screen the mesh takes the per-plate islands to **zero** (the
material is one connected body), turning the cuttability verdict green.

---

## 10. Command line

```bash
python -m tanuki.mori.stencil_lab photo.jpg -o photo.svg \
    --method cmyk \
    --pattern dots \
    --cell 6 \
    --max-side 1000 \
    --background white
```

`--pattern` accepts any registry name (`dots`, `lines`, `crosshatch`, `sine`,
`spiral`, `hexagons`, `topographic`, `stipple`, …). Omit `-o` to write next to
the input with the format's default suffix. Prints a summary:

```
Wrote photo.svg (svg) — 4 layer(s), 4006 primitives (300×200 px)
```

Pick any format with `-f / --format` (`svg`, `png`, `dxf`, `pdf`, `stl`,
`blender`) and add registration marks with `--registration`:

```bash
# DXF cut file with target marks
python -m tanuki.mori.stencil_lab photo.jpg -f dxf --registration target

# Blender script with solid extrusion
python -m tanuki.mori.stencil_lab photo.jpg -f blender \
    --method grayscale --pattern hexagons --scale 0.01 --extrude 0.5 --cell 10
# then: blender --background --python photo.py

# 3-D-printable plate
python -m tanuki.mori.stencil_lab photo.jpg -f stl --thickness 1.5 --scale 0.1

# split a large design across a 600×800 plotter bed (writes photo_r#c#.dxf)
python -m tanuki.mori.stencil_lab photo.jpg -f dxf --tile 600x800 --tile-overlap 20
```

### Web GUI

An optional FastAPI GUI wraps the same pipeline with live SVG preview,
toggleable colour plates, a cuttability verdict and background export:

```bash
pip install -r src/tanuki/mori/stencil_lab/requirements-gui.txt   # or: pip install -e ".[gui]"
cd src/tanuki && python -m tanuki.mori.stencil_lab.gui            # → http://127.0.0.1:8000
```

See the [tutorial](tutorial.md#9-web-gui) for a screenshot and [`gui.py`](../gui.py)
for the (small) implementation — `/api/preview` returns inline SVG, `/api/export`
runs the heavy optimised render in a threadpool.

---

## 11. Recipes

**Black-and-white newspaper halftone**

```python
arr = sl.load_image("portrait.jpg", mode="L")
arr = adj.contrast(arr, 1.2)
h, w = arr.shape
stencil = sl.build_stencil(sep.grayscale(arr), (w, h), cell=5)  # single plate → 45° screen
sl.write_svg(stencil, "newspaper.svg", background="white")
```

**Risograph two-colour print**

```python
arr = sl.load_image("art.png")
s = sep.duotone(arr, shadow=(30, 30, 120), base=(255, 90, 60))
stencil = sl.build_stencil(s, (arr.shape[1], arr.shape[0]), cell=7)
sl.write_svg(stencil, "riso.svg", background="white")
```

**Line-art from edges (Phase 1 raster preview)**

```python
arr = sl.to_grayscale(sl.load_image("building.jpg"))
edge = adj.edges(adj.blur(arr, 1))          # de-noise, then Sobel
sl.save_image(adj.invert(edge), "lineart.png")
```

**High-contrast posterized stencil**

```python
arr = sl.to_grayscale(sl.load_image("logo.png"))
arr = adj.posterize(adj.contrast(arr, 1.6), levels=3)
stencil = sl.build_stencil(sep.grayscale(arr), (arr.shape[1], arr.shape[0]), cell=4)
sl.write_svg(stencil, "poster.svg")
```

---

See [`../README.md`](../README.md) for the module map and phase roadmap.
