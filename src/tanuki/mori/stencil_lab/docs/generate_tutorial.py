"""generate_tutorial.py
───────────────────────
Regenerate every image embedded in ``tutorial.md`` from ``tanuki.jpg``.

Run from anywhere::

    python -m tanuki.mori.stencil_lab.docs.generate_tutorial

It writes PNGs into ``docs/tutorial/`` so the tutorial stays in sync with the
code — re-run it whenever a pattern, separation or default changes.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np

from tanuki.mori import stencil_lab as sl
from tanuki.mori.stencil_lab import adjustments as adj
from tanuki.mori.stencil_lab import fabrication as fab
from tanuki.mori.stencil_lab import separation as sep
from tanuki.mori.stencil_lab.patterns import PATTERN_NAMES

HERE = Path(__file__).resolve().parent
SRC = HERE / "tanuki.jpg"
OUT = HERE / "tutorial"
MAX_SIDE = 440          # working resolution for the gallery
CELL = 5.0              # halftone cell for pattern/separation demos


def _stencil(plane_sep, size):
    return sl.build_stencil(plane_sep, size, cell=CELL)


def main() -> None:
    OUT.mkdir(exist_ok=True)

    # ── source ────────────────────────────────────────────────────────────
    rgb = sl.resize(sl.load_image(SRC), max_side=MAX_SIDE)
    h, w = rgb.shape[:2]
    gray = sl.to_grayscale(rgb)
    cov = 1.0 - gray
    sl.save_image(rgb, OUT / "00_source.png")
    sl.save_image(gray, OUT / "01_grayscale.png")
    sl.save_image(cov, OUT / "02_coverage.png")
    print(f"source {w}×{h}")

    # ── adjustments (raster tone demos) ─────────────────────────────────────
    adjustments = {
        "brightness": adj.brightness(gray, 0.25),
        "contrast": adj.contrast(gray, 1.8),
        "gamma": adj.gamma(gray, 0.45),
        "invert": adj.invert(gray),
        "threshold": adj.threshold(gray, 0.5),
        "posterize": adj.posterize(gray, 4),
        "blur": adj.blur(gray, 4),
        "sharpen": adj.sharpen(gray, 1.5, 2),
        "edges": adj.edges(gray),
    }
    for name, arr in adjustments.items():
        sl.save_image(arr, OUT / f"adj_{name}.png")
    print(f"adjustments: {len(adjustments)}")

    # ── separations (halftone result per method) ────────────────────────────
    methods = {
        "grayscale": sep.grayscale(rgb),
        "rgb": sep.rgb(rgb),
        "cmyk": sep.cmyk(rgb),
        "duotone": sep.duotone(rgb),
        "tritone": sep.tritone(rgb),
    }
    for name, s in methods.items():
        st = _stencil(s, (w, h))
        sl.write_png(st, OUT / f"sep_{name}.png")

    # CMYK shown plate by plate — each channel screened on its own, in its ink
    cmyk = methods["cmyk"]
    for ch in cmyk:
        plate = _stencil(sep.Separation([ch]), (w, h))   # keeps the channel's angle
        sl.write_png(plate, OUT / f"sep_cmyk_{ch.name}.png")
    print(f"separations: {len(methods)} (+{len(cmyk)} CMYK plates)")

    # ── patterns (grayscale, one per screen) ────────────────────────────────
    gray_sep = sep.grayscale(rgb)
    for name in PATTERN_NAMES:
        st = sl.build_stencil(gray_sep, (w, h), pattern=name, cell=CELL)
        sl.write_png(st, OUT / f"pat_{name}.png")
    print(f"patterns: {len(PATTERN_NAMES)}")

    # ── street-art line-screen reproductions (inspired by docs/refs) ────────
    plane = 1.0 - adj.contrast(gray, 1.25)             # contrasty coverage
    ls = sl.Stencil(w, h)
    ls.layer("ink", color=(20, 30, 90)).add(
        sl.line_screen(plane, period=6, angle=0, max_duty=0.95))   # horizontal
    sl.write_png(ls, OUT / "ref_line_screen.png", background=(245, 242, 230))

    duo = sep.duotone(rgb, shadow=(20, 30, 90), base=(235, 90, 70))
    dls = sl.Stencil(w, h)
    for ch in duo:                                     # both plates horizontal
        dls.layer(ch.name, color=ch.color).add(
            sl.line_screen(ch.plane, period=6, angle=0, max_duty=0.95))
    sl.write_png(dls, OUT / "ref_duotone_lines.png", background=(250, 248, 240))

    # CMYK line-screen: each plate as lines at its own screen angle (15/75/0/45)
    cmyk_ls = sl.build_stencil(sep.cmyk(rgb), (w, h), pattern="line_screen", cell=6)
    sl.write_png(cmyk_ls, OUT / "ref_cmyk_lines.png", background=(255, 255, 255))

    # wavy line-screen (ref 5): undulating duotone lines
    wav = sl.Stencil(w, h)
    wav.layer("ink", color=(15, 55, 70)).add(
        sl.line_screen(plane, period=7, angle=0, wave_amplitude=4,
                       wave_length=46, max_duty=0.95))
    sl.write_png(wav, OUT / "ref_wave_lines.png", background=(225, 232, 228))
    print("street-art: line_screen, duotone, CMYK, wavy")

    # ── fabrication (mask → optimize) ───────────────────────────────────────
    poster = adj.posterize(adj.contrast(gray, 1.4), 2)
    mask = fab.StencilMask.from_coverage(1.0 - poster, threshold=0.5)
    mask.save_preview(OUT / "fab_mask.png")
    opt, report = fab.optimize_mask(mask, min_hole_area=8, min_island_area=40,
                                    bridge_width=3)
    opt.save_preview(OUT / "fab_optimized.png")
    (OUT / "fab_report.txt").write_text(str(report), encoding="utf-8")
    print(f"fabrication: islands {report.islands_before}→{report.islands_after}, "
          f"bridges {report.bridges_added}")

    # ── cuttability: safe (anchored) vs at-risk (would fall out) ────────────
    dot_st = sl.build_stencil(sep.grayscale(rgb), (w, h), pattern="dots", cell=6)
    cmask = fab.StencilMask.from_stencil(dot_st)
    safe = fab.safe_material(cmask, min_feature_px=2)
    risk = fab.at_risk_material(cmask, min_feature_px=2)
    overlay = np.ones((h, w, 3))                 # white = cut / holes
    overlay[safe] = (0.15, 0.15, 0.15)           # material anchored to frame
    overlay[risk] = (0.85, 0.10, 0.10)           # at-risk → would detach (red)
    sl.save_image(overlay, OUT / "cut_safe_vs_risk.png")
    crep = fab.analyze_cuttability(cmask, min_feature_px=2)
    (OUT / "cut_report.txt").write_text(crep.summary(), encoding="utf-8")
    print(f"cuttability: score {crep.score:.2f}, at-risk "
          f"{100 * crep.at_risk_fraction:.0f}%, {len(crep.regions)} regions")

    # ── registration marks (sparse screen so marks read clearly) ────────────
    reg = sl.build_stencil(sep.grayscale(rgb), (w, h), cell=10.0)
    sl.add_registration_marks(reg, kind="target", margin=16, size=12, line_width=2.0)
    sl.write_png(reg, OUT / "registration_target.png")
    print("registration: target")

    # ── tiling (montage of 2×2 tiles with gaps) ─────────────────────────────
    base = sl.build_stencil(sep.grayscale(rgb), (w, h), cell=CELL)
    bed_w, bed_h = w / 2 + 10, h / 2 + 10        # → 2×2 grid with overlap
    tiles = sl.tile_stencil(base, bed_w, bed_h, overlap=20)
    from PIL import Image
    gap = 12
    cols = max(t.col for t in tiles) + 1
    rows = max(t.row for t in tiles) + 1
    cell_w = max(int(t.stencil.width) for t in tiles)
    cell_h = max(int(t.stencil.height) for t in tiles)
    montage = Image.new("RGB",
                        (cols * cell_w + (cols + 1) * gap,
                         rows * cell_h + (rows + 1) * gap), (210, 210, 210))
    for t in tiles:
        img = sl.render_png(t.stencil, supersample=1)
        x = gap + t.col * (cell_w + gap)
        y = gap + t.row * (cell_h + gap)
        montage.paste(img, (x, y))
    montage.save(OUT / "tiling_montage.png")
    print(f"tiling: {len(tiles)} tiles ({rows}×{cols})")

    # ── physical poster: one photo scaled to ~A2 and split onto A4 sheets ───
    base2 = sl.build_stencil(sep.grayscale(rgb), (w, h), pattern="line_screen", cell=6)
    scaled, ptiles = sl.poster(base2, "a4", width_mm=420, margin_mm=10, overlap_mm=10)
    pcols = max(t.col for t in ptiles) + 1
    prows = max(t.row for t in ptiles) + 1
    pw = max(int(t.stencil.width) for t in ptiles)
    ph = max(int(t.stencil.height) for t in ptiles)
    pm = Image.new("RGB",
                   (pcols * pw + (pcols + 1) * gap, prows * ph + (prows + 1) * gap),
                   (235, 235, 235))
    for t in ptiles:
        img = sl.render_png(t.stencil, supersample=1, background=(255, 255, 255))
        pm.paste(img, (gap + t.col * (pw + gap), gap + t.row * (ph + gap)))
    pm.save(OUT / "poster_sheets.png")
    print(f"poster: {scaled.width:.0f}×{scaled.height:.0f} mm on {len(ptiles)} A4 sheets")

    _gui_screenshot(rgb, w, h)

    print(f"\nDone → {OUT}")


def _gui_screenshot(rgb, w, h) -> None:
    """Screenshot the real FastAPI GUI (needs fastapi + a chromium on PATH)."""
    import shutil
    import subprocess

    chrome = next((b for b in ("chromium", "chromium-browser", "google-chrome",
                               "google-chrome-stable") if shutil.which(b)), None)
    if chrome is None:
        print("gui: skipped (no chromium on PATH)")
        return
    try:
        from tanuki.mori.stencil_lab.gui import _PAGE, _islands_overlay
    except (ImportError, SystemExit):
        print("gui: skipped (FastAPI not installed)")
        return
    import numpy as np

    cell = 6
    st = sl.build_stencil(sep.cmyk(rgb), (w, h), pattern="dots", cell=cell)
    svg = sl.to_svg(st, background="white")
    # per-plate cuttability + island overlay, exactly like /api/preview
    mia = max(4, round(cell ** 2))
    rows, total_islands, max_thin = [], 0, 0.0
    islands = np.zeros((h, w), bool)
    for L in st.layers:
        m = fab.StencilMask.from_layer(L, (w, h))
        r = fab.analyze_cuttability(m, min_feature_px=2, min_island_area=mia)
        thin = r.thin_px / r.material_px if r.material_px else 0.0
        total_islands += r.island_count
        max_thin = max(max_thin, thin)
        islands |= fab.island_mask(m, min_feature_px=2, min_island_area=mia)
        isl = f' · <b>{r.island_count} isl</b>' if r.island_count else ''
        rows.append(
            f'<label><input type=checkbox checked style="width:auto">'
            f'<span class=sw style="background:rgb({L.color[0]},{L.color[1]},{L.color[2]})">'
            f'</span>{L.name} <small>({len(L)}{isl})</small></label>')
    if islands.any():                                  # show the islands feature ON
        svg = svg.replace("</svg>", _islands_overlay(islands) + "</svg>")
    cls, verdict = ("warn",
                    f'● {total_islands} island(s) — bridged on export · '
                    f'thin {max_thin * 100:.0f}% · {st.primitive_count} prims')
    page = (_PAGE
            .replace('<div id="holder"><em>upload a photo to start</em></div>',
                     f'<div id="holder">{svg}</div>')
            .replace('<div id="verdict">load an image…</div>',
                     f'<div id="verdict" class="{cls}">{verdict}</div>')
            .replace('<button id="toggleisl">◍ Show islands</button>',
                     '<button id="toggleisl" class="on">◉ Hide islands</button>')
            .replace('<div id="layers"></div>', f'<div id="layers">{"".join(rows)}</div>'))
    demo = HERE / "_gui_demo.html"
    demo.write_text(page, encoding="utf-8")
    try:
        subprocess.run([chrome, "--headless=new", "--disable-gpu", "--no-sandbox",
                        "--hide-scrollbars", "--window-size=1120,640",
                        f"--screenshot={OUT / 'gui.png'}", f"file://{demo}"],
                       capture_output=True, timeout=90)
        print("gui: screenshot rendered")
    finally:
        demo.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
