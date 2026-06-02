"""Tests for tanuki.mori.stencil_lab (Phases 1 & 2)."""

from pathlib import Path

import numpy as np
import pytest

from tanuki.mori import stencil_lab as sl
from tanuki.mori.stencil_lab import adjustments as adj
from tanuki.mori.stencil_lab import separation as sep
from tanuki.mori.stencil_lab.geometry import Dot, Polyline
from tanuki.mori.stencil_lab.patterns import PATTERN_NAMES, generate
from tanuki.mori.stencil_lab.patterns import sampling
from tanuki.mori.stencil_lab import fabrication as fab


# ─── Fixtures ───────────────────────────────────────────────────────────────

@pytest.fixture
def gradient_gray():
    """64×64 horizontal black→white gradient, grayscale."""
    x = np.linspace(0.0, 1.0, 64)
    return np.tile(x, (64, 1))


@pytest.fixture
def gradient_rgb(gradient_gray):
    """64×64 RGB image with distinct per-channel gradients."""
    g = gradient_gray
    return np.stack([g, g[:, ::-1], np.flipud(g)], axis=-1)


# ─── image_io ─────────────────────────────────────────────────────────────────

def test_to_grayscale_passthrough(gradient_gray):
    assert sl.to_grayscale(gradient_gray) is gradient_gray


def test_to_grayscale_from_rgb(gradient_rgb):
    g = sl.to_grayscale(gradient_rgb)
    assert g.shape == (64, 64)
    assert 0.0 <= g.min() and g.max() <= 1.0


def test_coverage_is_inverse_tone(gradient_gray):
    cov = sl.coverage(gradient_gray)
    np.testing.assert_allclose(cov, 1.0 - gradient_gray)


def test_save_and_load_roundtrip(tmp_path, gradient_gray):
    p = sl.save_image(gradient_gray, tmp_path / "g.png")
    back = sl.load_image(p, mode="L")
    assert back.shape == (64, 64)
    np.testing.assert_allclose(back, gradient_gray, atol=1.5 / 255)


def test_resize_keeps_aspect(gradient_rgb):
    small = sl.resize(gradient_rgb, max_side=32)
    assert max(small.shape[:2]) == 32


# ─── adjustments ────────────────────────────────────────────────────────────

def test_adjustments_stay_in_range(gradient_gray):
    for fn in (lambda a: adj.brightness(a, 0.5),
               lambda a: adj.contrast(a, 2.0),
               lambda a: adj.gamma(a, 0.5),
               lambda a: adj.blur(a, 3),
               lambda a: adj.sharpen(a, 2.0),
               lambda a: adj.edges(a)):
        out = fn(gradient_gray)
        assert out.shape == gradient_gray.shape
        assert out.min() >= 0.0 and out.max() <= 1.0


def test_invert(gradient_gray):
    np.testing.assert_allclose(adj.invert(gradient_gray), 1.0 - gradient_gray)


def test_threshold_is_binary(gradient_gray):
    out = adj.threshold(gradient_gray, 0.5)
    assert set(np.unique(out)).issubset({0.0, 1.0})


def test_posterize_level_count(gradient_gray):
    out = adj.posterize(gradient_gray, levels=3)
    assert len(np.unique(out)) <= 3


def test_blur_does_not_mutate(gradient_gray):
    original = gradient_gray.copy()
    adj.blur(gradient_gray, 2)
    np.testing.assert_array_equal(gradient_gray, original)


# ─── separation ───────────────────────────────────────────────────────────────

def test_cmyk_channels(gradient_rgb):
    s = sep.cmyk(gradient_rgb)
    assert s.names == ["cyan", "magenta", "yellow", "key"]
    for ch in s:
        assert ch.plane.shape == (64, 64)
        assert ch.plane.min() >= 0.0 and ch.plane.max() <= 1.0


def test_cmyk_white_has_no_ink():
    white = np.ones((8, 8, 3))
    s = sep.cmyk(white)
    for ch in s:
        np.testing.assert_allclose(ch.plane, 0.0, atol=1e-9)


def test_cmyk_black_is_full_key():
    black = np.zeros((8, 8, 3))
    s = sep.cmyk(black)
    np.testing.assert_allclose(s["key"].plane, 1.0)


def test_rgb_separation(gradient_rgb):
    s = sep.rgb(gradient_rgb)
    assert s.names == ["red", "green", "blue"]


def test_grayscale_separation(gradient_gray):
    s = sep.grayscale(gradient_gray)
    assert len(s) == 1 and s.names == ["key"]


def test_duotone_and_tritone(gradient_rgb):
    assert sep.duotone(gradient_rgb).names == ["base", "shadow"]
    assert sep.tritone(gradient_rgb).names == ["shadow", "mid", "highlight"]


# ─── halftone ───────────────────────────────────────────────────────────────

def test_halftone_more_dots_for_darker_image():
    dark = np.full((64, 64), 0.9)    # high coverage → kept
    light = np.full((64, 64), 0.01)  # below min_coverage → dropped
    d_dark = sl.halftone_dots(dark, cell=8)
    d_light = sl.halftone_dots(light, cell=8)
    # both screened on the same grid, but light gets dropped by min_coverage
    assert len(d_dark) > len(d_light)


def test_halftone_dot_radius_grows_with_coverage():
    full = sl.halftone_dots(np.ones((40, 40)), cell=10, scale=1.0)
    half = sl.halftone_dots(np.full((40, 40), 0.25), cell=10, scale=1.0)
    assert full and half
    assert max(d.r for d in full) > max(d.r for d in half)


def test_halftone_requires_2d():
    with pytest.raises(ValueError):
        sl.halftone_dots(np.zeros((4, 4, 3)))


# ─── geometry + pipeline + svg ────────────────────────────────────────────────

def test_build_stencil_layers(gradient_rgb):
    s = sep.cmyk(gradient_rgb)
    stencil = sl.build_stencil(s, (64, 64), cell=6)
    assert len(stencil.layers) == 4
    assert stencil.primitive_count > 0
    assert stencil.width == 64 and stencil.height == 64


def test_layer_get_or_create():
    st = sl.Stencil(10, 10)
    a = st.layer("cyan")
    b = st.layer("cyan")
    assert a is b and len(st.layers) == 1


def test_to_svg_is_wellformed(gradient_rgb):
    stencil = sl.build_stencil(sep.cmyk(gradient_rgb), (64, 64), cell=8)
    svg = sl.to_svg(stencil, background="white")
    assert svg.startswith("<?xml")
    assert svg.rstrip().endswith("</svg>")
    assert svg.count("<g ") == 4
    assert "<circle" in svg


def test_write_svg(tmp_path, gradient_rgb):
    stencil = sl.build_stencil(sep.cmyk(gradient_rgb), (64, 64), cell=8)
    p = sl.write_svg(stencil, tmp_path / "out.svg")
    assert p.exists() and p.read_text().startswith("<?xml")


def test_halftone_stencil_endtoend(tmp_path, gradient_rgb):
    img = sl.save_image(gradient_rgb, tmp_path / "in.png")
    stencil = sl.halftone_stencil(img, method="cmyk", cell=8, max_side=64)
    assert len(stencil.layers) == 4
    assert stencil.primitive_count > 0


def test_halftone_stencil_grayscale_promotes_for_cmyk(tmp_path, gradient_gray):
    img = sl.save_image(gradient_gray, tmp_path / "g.png")
    stencil = sl.halftone_stencil(img, method="cmyk", max_side=64)
    assert len(stencil.layers) == 4


def test_halftone_stencil_optimizes_for_cutting_by_default(tmp_path, gradient_rgb):
    img = sl.save_image(gradient_rgb, tmp_path / "in.png")
    opt = sl.halftone_stencil(img, method="grayscale", pattern="dots", max_side=64)
    raw = sl.halftone_stencil(img, method="grayscale", pattern="dots", max_side=64,
                              optimize=False)
    # default → cut polygons (fabrication-ready); raw → the artistic dots
    assert opt.primitive_count > 0
    assert all(isinstance(p, Polyline) and p.fill
               for L in opt.layers for p in L.primitives)
    assert any(isinstance(p, Dot) for L in raw.layers for p in L.primitives)
    assert len(opt.layers) == len(raw.layers)


# ════════════════════════════════════════════════════════════════════════════
# Phase 2 — patterns
# ════════════════════════════════════════════════════════════════════════════

@pytest.fixture
def half_dark():
    """48×48 plane, left half full ink, right half empty."""
    p = np.zeros((48, 48))
    p[:, :24] = 1.0
    return p


# ─── sampling helpers ──────────────────────────────────────────────────────

def test_sample_bilinear_bounds(gradient_gray):
    cov = sl.coverage(gradient_gray)
    assert sampling.sample(cov, 0, 0) == pytest.approx(cov[0, 0])
    # out-of-range coordinates clamp instead of raising
    assert 0.0 <= sampling.sample(cov, -5, 999) <= 1.0


def test_runs_split_on_gaps():
    pts = [(float(i), 0.0) for i in range(6)]
    covs = [0.9, 0.9, 0.0, 0.0, 0.8, 0.8]   # one gap → two runs
    runs = sampling.runs_to_polylines(pts, covs, max_width=4.0, min_coverage=0.1)
    assert len(runs) == 2
    assert all(isinstance(r, Polyline) and r.width > 0 for r in runs)


# ─── registry ───────────────────────────────────────────────────────────────

def test_registry_covers_all_patterns(half_dark):
    assert set(PATTERN_NAMES) >= {
        "dots", "lines", "circular", "crosshatch", "sine", "zigzag",
        "spiral", "radial", "hexagons", "honeycomb", "topographic", "stipple",
        "voronoi",
    }
    for name in PATTERN_NAMES:
        prims = generate(half_dark, name, cell=8, angle=30)
        assert isinstance(prims, list)
        # the dark half must produce geometry for every pattern
        assert len(prims) > 0, name
        for prim in prims:
            assert isinstance(prim, (Dot, Polyline))


def test_generate_unknown_pattern_raises(half_dark):
    with pytest.raises(ValueError):
        generate(half_dark, "nope", cell=8)


def test_patterns_reject_3d():
    rgb = np.zeros((8, 8, 3))
    for name in PATTERN_NAMES:
        with pytest.raises(ValueError):
            generate(rgb, name, cell=8)


# ─── individual generators ────────────────────────────────────────────────────

def test_lines_concentrate_on_ink(half_dark):
    lines = sl.halftone_lines(half_dark, spacing=6, angle=0)
    # every emitted segment sits in (or touches) the inked left half
    assert lines
    assert all(min(x for x, _ in ln.points) < 30 for ln in lines)


def test_crosshatch_builds_up_with_darkness():
    light = np.full((40, 40), 0.2)
    dark = np.full((40, 40), 0.9)
    assert len(sl.crosshatch(dark, spacing=6)) > len(sl.crosshatch(light, spacing=6))


def test_hexagons_size_tracks_coverage():
    full = sl.hexagons(np.ones((40, 40)), cell=12)
    faint = sl.hexagons(np.full((40, 40), 0.2), cell=12)
    assert full and faint

    def max_extent(polys):
        return max(
            max(x for x, _ in p.points) - min(x for x, _ in p.points)
            for p in polys
        )

    assert max_extent(full) > max_extent(faint)


def test_honeycomb_outlines_are_closed(half_dark):
    cells = sl.honeycomb(half_dark, cell=10, threshold=0.2)
    assert cells
    assert all(p.closed and not p.fill and len(p.points) == 6 for p in cells)


def test_topographic_emits_contours_at_a_boundary(half_dark):
    contours = sl.topographic(half_dark, cell=4, levels=(0.5,))
    # the black/white boundary down the middle yields contour segments
    assert contours
    xs = [x for c in contours for x, _ in c.points]
    assert min(xs) < 30 < max(xs) or abs(np.mean(xs) - 24) < 12


def test_stipple_density_tracks_coverage():
    dense = sl.stipple(np.ones((60, 60)), cell=5, seed=1)
    sparse = sl.stipple(np.full((60, 60), 0.1), cell=5, seed=1)
    assert len(dense) > len(sparse)
    assert all(isinstance(d, Dot) for d in dense)


def test_stipple_is_deterministic():
    a = sl.stipple(np.full((40, 40), 0.5), cell=5, seed=7)
    b = sl.stipple(np.full((40, 40), 0.5), cell=5, seed=7)
    assert [(d.x, d.y) for d in a] == [(d.x, d.y) for d in b]


def test_sine_and_zigzag_make_rows(half_dark):
    assert sl.sine_wave(half_dark, spacing=8)
    assert sl.zigzag(half_dark, spacing=8)


def test_voronoi_density_tracks_coverage():
    p = np.zeros((100, 100))
    p[:, :50] = 0.95   # dark (dense cells) left, light (sparse) right
    p[:, 50:] = 0.05
    edges = sl.voronoi(p, spacing=8, seed=1)
    assert edges
    left = sum(1 for e in edges if (e.points[0][0] + e.points[1][0]) / 2 < 50)
    assert left > len(edges) - left      # dark half is denser


def test_voronoi_clips_to_bounds():
    p = np.full((80, 80), 0.6)
    edges = sl.voronoi(p, spacing=10, seed=2)
    assert all(0 <= x <= 80 and 0 <= y <= 80 for e in edges for x, y in e.points)


def test_voronoi_is_deterministic():
    p = np.full((60, 60), 0.5)
    a = sl.voronoi(p, spacing=8, seed=3)
    b = sl.voronoi(p, spacing=8, seed=3)
    assert [e.points for e in a] == [e.points for e in b]


def test_voronoi_too_few_seeds_returns_empty():
    assert sl.voronoi(np.zeros((6, 6)), spacing=10) == []


# ─── pipeline integration with non-dot patterns ──────────────────────────────

def test_build_stencil_with_pattern(gradient_rgb):
    s = sep.cmyk(gradient_rgb)
    stencil = sl.build_stencil(s, (64, 64), pattern="lines", cell=6)
    assert len(stencil.layers) == 4
    assert stencil.primitive_count > 0
    assert all(isinstance(p, Polyline) for L in stencil.layers for p in L.primitives)


def test_halftone_stencil_pattern_endtoend(tmp_path, gradient_rgb):
    img = sl.save_image(gradient_rgb, tmp_path / "in.png")
    stencil = sl.halftone_stencil(img, method="duotone", pattern="hexagons",
                                  cell=8, max_side=64)
    assert stencil.primitive_count > 0
    svg = sl.to_svg(stencil)
    assert "<polygon" in svg


def test_svg_renders_polylines(half_dark):
    st = sl.Stencil(48, 48)
    st.layer("key").add(sl.halftone_lines(half_dark, spacing=6, angle=0))
    svg = sl.to_svg(st)
    assert "<polyline" in svg


# ════════════════════════════════════════════════════════════════════════════
# Phase 3 — fabrication / stencil optimisation
# ════════════════════════════════════════════════════════════════════════════

def _annulus(size=80, inner=18, outer=30):
    """Cut mask shaped like the letter 'O' — a ring of cut with a centre island."""
    yy, xx = np.mgrid[0:size, 0:size]
    r = np.hypot(xx - size / 2, yy - size / 2)
    return fab.StencilMask((r >= inner) & (r <= outer))


# ─── mask construction ────────────────────────────────────────────────────

def test_mask_from_coverage_threshold():
    plane = np.linspace(0, 1, 100).reshape(10, 10)
    m = fab.StencilMask.from_coverage(plane, threshold=0.5)
    assert m.cut.dtype == bool
    assert m.cut.sum() == (plane >= 0.5).sum()
    np.testing.assert_array_equal(m.material, ~m.cut)


def test_mask_rasterizes_dot():
    st = sl.Stencil(40, 40)
    st.layer("key").add(Dot(20, 20, 8))
    m = fab.StencilMask.from_stencil(st)
    assert m.cut[20, 20]            # centre is cut
    assert not m.cut[0, 0]          # corner is material
    # roughly the dot area
    assert abs(m.cut.sum() - np.pi * 8 ** 2) < np.pi * 8 ** 2 * 0.3


def test_mask_copy_is_independent():
    m = _annulus()
    c = m.copy()
    c.cut[:] = False
    assert m.cut.any()


# ─── island detection ────────────────────────────────────────────────────────

def test_detect_island_in_o_shape():
    islands = fab.detect_islands(_annulus())
    assert len(islands) == 1
    isl = islands[0]
    assert isl.centroid[0] == pytest.approx(40, abs=1)
    assert isl.centroid[1] == pytest.approx(40, abs=1)
    assert isl.area > 0


def test_no_islands_when_nothing_enclosed():
    m = fab.StencilMask(np.zeros((40, 40), bool))   # all material
    assert fab.detect_islands(m) == []
    m2 = fab.StencilMask.from_coverage(np.zeros((40, 40)))  # solid material
    assert fab.detect_islands(m2) == []


# ─── bridges ──────────────────────────────────────────────────────────────────

def test_bridge_reconnects_island():
    m = _annulus()
    assert len(fab.detect_islands(m)) == 1
    bridged, n = fab.add_bridges(m, width=3)
    assert n == 1
    assert len(fab.detect_islands(bridged)) == 0


def test_no_bridge_without_islands():
    m = fab.StencilMask(np.zeros((30, 30), bool))
    bridged, n = fab.add_bridges(m)
    assert n == 0


# ─── minimum feature size / reinforcement ─────────────────────────────────────

def test_remove_small_holes():
    cut = np.zeros((40, 40), bool)
    cut[5, 5] = True               # 1px speckle hole
    cut[20:30, 20:30] = True       # 100px real hole
    m = fab.StencilMask(cut)
    cleaned, removed = fab.remove_small_holes(m, min_area=4)
    assert removed == 1
    assert not cleaned.cut[5, 5]
    assert cleaned.cut[25, 25]


def test_remove_small_islands():
    m = _annulus(size=80, inner=2, outer=30)  # tiny centre island
    before = fab.detect_islands(m)[0].area
    cleaned, removed = fab.remove_small_islands(m, min_area=before + 1)
    assert removed == 1
    assert fab.detect_islands(cleaned) == []


def test_thin_material_flags_slivers():
    cut = np.zeros((40, 40), bool)
    cut[:, :19] = True
    cut[:, 21:] = True            # a 2px-wide vertical material sliver remains
    m = fab.StencilMask(cut)
    thin = fab.thin_material(m, min_width=5)
    assert thin.any()


def test_min_hole_diameter():
    cut = np.zeros((60, 60), bool)
    yy, xx = np.mgrid[0:60, 0:60]
    cut[np.hypot(xx - 30, yy - 30) <= 10] = True   # disc radius 10
    d = fab.min_hole_diameter(fab.StencilMask(cut))
    assert d == pytest.approx(20, abs=3)


# ─── checks & orchestrator ────────────────────────────────────────────────────

def test_fabrication_checks_shape():
    results = fab.fabrication_checks(_annulus(), min_feature_px=2.0)
    assert set(results) == {"has_material", "islands", "min_feature", "min_hole"}
    assert all(isinstance(v, list) for v in results.values())
    assert results["islands"]   # the O has an unbridged island → reported


def test_checks_flag_degenerate_sheets():
    all_cut = fab.StencilMask(np.ones((20, 20), bool))
    assert fab.fabrication_checks(all_cut)["has_material"]
    all_mat = fab.StencilMask(np.zeros((20, 20), bool))
    assert fab.fabrication_checks(all_mat)["has_material"]


def test_optimize_mask_clears_islands():
    m = _annulus()
    opt, report = fab.optimize_mask(m, min_island_area=4, bridge_width=3)
    assert report.islands_before == 1
    assert report.islands_after == 0
    assert report.bridges_added == 1
    assert not report.checks["islands"]   # islands check now passes
    assert isinstance(str(report), str)


def test_optimize_report_ready_on_clean_sheet():
    cut = np.zeros((60, 60), bool)
    cut[20:40, 20:40] = True       # one big square hole, no islands
    opt, report = fab.optimize_mask(fab.StencilMask(cut))
    assert report.ready


# ─── vectorisation back to geometry ───────────────────────────────────────────

def test_mask_to_polylines_closed():
    cut = np.zeros((40, 40), bool)
    cut[10:30, 10:30] = True       # one square hole
    polys = fab.mask_to_polylines(cut, simplify=1.0)
    assert len(polys) == 1
    p = polys[0]
    assert p.closed and p.fill and len(p.points) >= 4
    assert p.holes == []           # simply connected → no holes


def _ring_cut(size=80, inner=18, outer=30):
    yy, xx = np.mgrid[0:size, 0:size]
    r = np.hypot(xx - size / 2, yy - size / 2)
    return (r >= inner) & (r <= outer)


def test_mask_to_polylines_traces_inner_hole():
    polys = fab.mask_to_polylines(_ring_cut(), simplify=1.5)
    assert len(polys) == 1
    p = polys[0]
    assert len(p.holes) == 1          # the annulus has one enclosed material island
    # hole centroid sits at the ring centre
    hx = [x for x, _ in p.holes[0]]
    hy = [y for _, y in p.holes[0]]
    assert abs(sum(hx) / len(hx) - 40) < 3
    assert abs(sum(hy) / len(hy) - 40) < 3


def test_holes_survive_to_svg_and_pdf():
    st = fab.StencilMask(_ring_cut()).to_stencil()
    svg = sl.to_svg(st)
    assert 'fill-rule="evenodd"' in svg and "<path" in svg
    pdf = sl.to_pdf(st).decode("latin-1")
    assert "f*" in pdf               # even-odd fill operator


def test_holes_become_extra_dxf_and_blender_splines():
    st = fab.StencilMask(_ring_cut()).to_stencil()
    # outer ring + 1 hole → 2 closed polylines / splines
    assert sl.to_dxf(st).count("\nPOLYLINE\n") == 2
    assert sl.to_blender_script(st).count("_poly(cu, [") == 2


def test_holed_polygon_extrudes_to_solid_with_cavity():
    # a square frame: outer 0..20, hole 5..15
    outer = [(0, 0), (20, 0), (20, 20), (0, 20)]
    hole = [(5, 5), (15, 5), (15, 15), (5, 15)]
    st = sl.Stencil(20, 20)
    st.layer("key").add(sl.Polyline(outer, closed=True, fill=True, holes=[hole]))
    stl = sl.to_stl(st, thickness=2.0)
    # caps (8 outer-frame tris each → 16) + outer walls (8) + hole walls (8) = 32
    assert stl.count("facet normal") == 32
    assert stl.count("facet normal") == stl.count("endfacet")


def test_png_renders_holed_polygon():
    outer = [(0, 0), (20, 0), (20, 20), (0, 20)]
    hole = [(5, 5), (15, 5), (15, 15), (5, 15)]
    st = sl.Stencil(20, 20)
    st.layer("key", color=(0, 0, 0)).add(
        sl.Polyline(outer, closed=True, fill=True, holes=[hole]))
    img = sl.render_png(st, background=(255, 255, 255), supersample=1)
    assert img.getpixel((10, 10)) == (255, 255, 255)   # hole shows background
    assert img.getpixel((1, 1)) == (0, 0, 0)            # frame is inked


def test_to_stencil_roundtrip_exports_svg():
    cut = np.zeros((40, 40), bool)
    cut[10:30, 10:30] = True
    st = fab.StencilMask(cut).to_stencil()
    assert st.width == 40 and st.height == 40
    svg = sl.to_svg(st)
    assert "<polygon" in svg


def test_save_preview(tmp_path):
    p = _annulus().save_preview(tmp_path / "mask.png")
    assert p.exists()


# ════════════════════════════════════════════════════════════════════════════
# Phase 4 — Blender geometry export
# ════════════════════════════════════════════════════════════════════════════

import ast

from tanuki.mori.stencil_lab.geometry import Stencil, polygon


@pytest.fixture
def small_stencil():
    st = Stencil(40, 30)
    st.layer("cyan", color=(0, 174, 239)).add([Dot(10, 10, 4), Dot(20, 15, 2)])
    st.layer("key", color=(0, 0, 0)).add(polygon([(5, 5), (35, 5), (20, 25)]))
    return st


def test_blender_script_is_valid_python(small_stencil):
    src = sl.to_blender_script(small_stencil)
    ast.parse(src)                       # raises on invalid syntax
    assert "import bpy" in src
    assert "def build()" in src


def test_blender_script_one_curve_per_layer(small_stencil):
    src = sl.to_blender_script(small_stencil)
    assert src.count("= _new_curve(") == 2        # cyan + key (excludes def)
    # 2 dots + 1 polygon = 3 splines (call sites pass a list literal)
    assert src.count("_poly(cu, [") == 3


def test_blender_dot_resolution_controls_circle_verts(small_stencil):
    src = sl.to_blender_script(small_stencil, dot_resolution=8)
    # first dot's spline should have 8 coordinate tuples
    first = next(l for l in src.splitlines() if l.strip().startswith("_poly("))
    call = ast.parse(first.strip()).body[0].value
    pts = call.args[1]
    assert len(pts.elts) == 8


def test_blender_flips_y_and_scales():
    st = Stencil(100, 100)
    st.layer("key").add(polygon([(0, 0), (10, 0), (10, 10)]))
    src = sl.to_blender_script(st, scale=2.0)
    # point (0,0) top-left → (0, 100) bottom-left → *2 → (0.0, 200.0)
    assert "(0.0, 200.0)" in src


def test_blender_extrude_and_fill_flags(small_stencil):
    solid = sl.to_blender_script(small_stencil, extrude=0.5, fill=True)
    assert "EXTRUDE = 0.5" in solid
    assert "FILL = True" in solid
    flat = sl.to_blender_script(small_stencil, extrude=0.0, fill=False)
    assert "EXTRUDE = 0.0" in flat
    assert "FILL = False" in flat


def test_blender_empty_stencil_still_valid():
    src = sl.to_blender_script(Stencil(10, 10))
    ast.parse(src)
    assert "pass" in src


def test_write_blender_script(tmp_path, small_stencil):
    p = sl.write_blender_script(small_stencil, tmp_path / "out.py", extrude=0.3)
    assert p.exists()
    ast.parse(p.read_text())
    assert p.name in p.read_text()       # fname embedded in header


# ════════════════════════════════════════════════════════════════════════════
# Phase 5 — registration & export formats
# ════════════════════════════════════════════════════════════════════════════

import re

from tanuki.mori.stencil_lab.export import stl as stl_mod


# ─── registration ──────────────────────────────────────────────────────────

@pytest.mark.parametrize("kind,per_corner", [
    ("crosshair", 2), ("target", 3), ("corner", 1),
])
def test_registration_mark_counts(kind, per_corner):
    marks = sl.registration_marks(100, 80, kind=kind)
    assert len(marks) == per_corner * 4      # four corners
    assert all(isinstance(m, Polyline) and not m.fill for m in marks)


def test_registration_unknown_kind():
    with pytest.raises(ValueError):
        sl.registration_marks(10, 10, kind="bogus")


def test_add_registration_marks_to_every_layer(small_stencil):
    before = [len(l) for l in small_stencil.layers]
    sl.add_registration_marks(small_stencil, kind="crosshair")
    after = [len(l) for l in small_stencil.layers]
    # crosshair = 8 marks added to each layer
    assert all(a - b == 8 for a, b in zip(after, before))


def test_add_registration_marks_empty_stencil():
    st = Stencil(50, 50)
    sl.add_registration_marks(st, kind="target")
    assert len(st.layers) == 1 and st.layers[0].name == "registration"
    assert len(st.layers[0]) == 12


def test_split_to_plates(small_stencil):
    plates = sl.split_to_plates(small_stencil, kind="crosshair")
    assert len(plates) == 2
    for plate, src in zip(plates, small_stencil.layers):
        assert len(plate.layers) == 1
        assert plate.layers[0].name == src.name
        assert len(plate.layers[0]) == len(src) + 8   # original + marks


# ─── PNG ──────────────────────────────────────────────────────────────────

def test_png_render_size_and_mode(small_stencil):
    img = sl.render_png(small_stencil, supersample=2)
    assert img.size == (40, 30) and img.mode == "RGB"


def test_png_draws_ink(small_stencil):
    img = sl.render_png(small_stencil, background=(255, 255, 255), supersample=1)
    # not a blank white canvas — ink was drawn somewhere
    assert img.getextrema() != ((255, 255), (255, 255), (255, 255))


def test_write_png(tmp_path, small_stencil):
    from PIL import Image
    p = sl.write_png(small_stencil, tmp_path / "out.png")
    assert p.exists() and Image.open(p).size == (40, 30)


# ─── DXF ──────────────────────────────────────────────────────────────────

def test_dxf_structure_and_entities(small_stencil):
    dxf = sl.to_dxf(small_stencil)
    assert "SECTION" in dxf and "ENTITIES" in dxf and dxf.rstrip().endswith("EOF")
    assert dxf.count("\nCIRCLE\n") == 2          # two dots
    assert "\nPOLYLINE\n" in dxf
    assert "cyan" in dxf and "key" in dxf        # layer names preserved


def test_dxf_flips_y():
    st = Stencil(100, 100)
    st.layer("key").add(Dot(10, 0, 5))           # y=0 (top) → y=100 in DXF
    dxf = sl.to_dxf(st)
    assert "20\n100.0000" in dxf


def test_write_dxf(tmp_path, small_stencil):
    p = sl.write_dxf(small_stencil, tmp_path / "out.dxf")
    assert p.exists() and "ENTITIES" in p.read_text()


# ─── PDF ──────────────────────────────────────────────────────────────────

def test_pdf_is_wellformed(small_stencil):
    pdf = sl.to_pdf(small_stencil)
    assert pdf.startswith(b"%PDF-1.4")
    assert pdf.rstrip().endswith(b"%%EOF")
    # every xref offset must land on an "N 0 obj" record
    startxref = int(re.search(rb"startxref\s+(\d+)", pdf).group(1))
    assert pdf[startxref:startxref + 4] == b"xref"
    for m in re.finditer(rb"^(\d{10}) 00000 n", pdf, re.MULTILINE):
        off = int(m.group(1))
        assert re.match(rb"\d+ 0 obj", pdf[off:off + 12])


def test_pdf_contains_paint_ops(small_stencil):
    pdf = sl.to_pdf(small_stencil).decode("latin-1")
    assert " rg" in pdf and " c\n" in pdf and "f" in pdf   # colour, bézier, fill


def test_write_pdf(tmp_path, small_stencil):
    p = sl.write_pdf(small_stencil, tmp_path / "out.pdf")
    assert p.exists() and p.read_bytes().startswith(b"%PDF")


# ─── STL ──────────────────────────────────────────────────────────────────

def test_triangulate_square():
    tris = stl_mod.triangulate([(0, 0), (2, 0), (2, 2), (0, 2)])
    assert len(tris) == 2          # a quad → two triangles


def test_triangulate_concave_l_shape():
    poly = [(0, 0), (4, 0), (4, 1), (1, 1), (1, 4), (0, 4)]  # L (6 verts)
    tris = stl_mod.triangulate(poly)
    assert len(tris) == 4          # n-2 triangles for a simple polygon


def test_stl_extrudes_only_filled():
    st = Stencil(20, 20)
    st.layer("key").add([
        polygon([(2, 2), (18, 2), (18, 18), (2, 18)]),  # filled square → solid
        Polyline([(0, 0), (20, 20)], width=1),          # stroked line → skipped
    ])
    stl = sl.to_stl(st, thickness=1.0)
    # square solid = 2 top + 2 bottom + 8 walls = 12 facets
    assert stl.count("facet normal") == 12
    n_vertices = stl.count("vertex ")
    assert n_vertices == 12 * 3


def test_stl_first_facet_points_up():
    st = Stencil(20, 20)
    st.layer("key").add(polygon([(2, 2), (18, 2), (18, 18), (2, 18)]))
    stl = sl.to_stl(st, thickness=1.0)
    first = re.search(r"facet normal (\S+) (\S+) (\S+)", stl)
    nz = float(first.group(3))
    assert nz > 0.9               # top cap faces +Z


def test_stl_wellformed_structure(small_stencil):
    stl = sl.to_stl(small_stencil, thickness=2.0)
    assert stl.startswith("solid")
    assert stl.count("facet normal") == stl.count("endfacet")
    assert stl.count("outer loop") == stl.count("endloop")


def test_write_stl(tmp_path, small_stencil):
    p = sl.write_stl(small_stencil, tmp_path / "out.stl", thickness=1.5)
    assert p.exists() and p.read_text().startswith("solid")


# ════════════════════════════════════════════════════════════════════════════
# Phase 6 — canvas tiling / panelisation
# ════════════════════════════════════════════════════════════════════════════

from tanuki.mori.stencil_lab import tiling


def _big_stencil():
    st = Stencil(250, 180)
    st.layer("key", color=(0, 0, 0)).add([Dot(50, 50, 4), Dot(150, 90, 4), Dot(240, 170, 4)])
    st.layer("key").add(polygon([(10, 10), (240, 10), (240, 170), (10, 170)]))
    return st


def test_tile_grid_dimensions_with_overlap():
    grid = sl.tile_grid(250, 180, 100, 100, overlap=20)
    assert len(grid) == 2 and len(grid[0]) == 3      # 2 rows × 3 cols
    # last column clamped to the canvas edge
    assert grid[0][-1][2] == 250


def test_tile_grid_single_when_bed_bigger():
    grid = sl.tile_grid(100, 80, 200, 200)
    assert len(grid) == 1 and len(grid[0]) == 1
    assert grid[0][0] == (0, 0, 100, 80)


def test_tile_overlap_must_be_smaller_than_bed():
    with pytest.raises(ValueError):
        sl.tile_grid(200, 200, 50, 50, overlap=50)


def test_tile_stencil_fits_bed_and_local_origin():
    tiles = sl.tile_stencil(_big_stencil(), 100, 100, overlap=20)
    assert len(tiles) == 6
    for t in tiles:
        assert t.stencil.width <= 100 and t.stencil.height <= 100
        for layer in t.stencil.layers:
            for prim in layer.primitives:
                x0, y0, x1, y1 = prim.bbox()
                assert x0 >= -0.01 and y0 >= -0.01
                assert x1 <= t.stencil.width + 0.01 and y1 <= t.stencil.height + 0.01


def test_tile_adds_crop_marks():
    tiles = sl.tile_stencil(_big_stencil(), 120, 120)
    crop = [l for l in tiles[0].stencil.layers if l.name == "crop"][0]
    assert len(crop) == 4                            # one tick per corner
    assert all(not p.fill for p in crop.primitives)


def test_tile_no_crop_marks_when_disabled():
    tiles = sl.tile_stencil(_big_stencil(), 120, 120, crop_marks=False)
    assert all(l.name != "crop" for l in tiles[0].stencil.layers)


def test_clip_segment_to_rect():
    # horizontal line crossing a box [0,0,10,10] from x=-5 to x=15 at y=5
    seg = tiling._clip_segment((-5, 5), (15, 5), (0, 0, 10, 10))
    assert seg == ((0.0, 5.0), (10.0, 5.0))
    # fully outside → None
    assert tiling._clip_segment((20, 20), (30, 30), (0, 0, 10, 10)) is None


def test_clip_open_polyline_splits_runs():
    # zig in/out of the box should yield clipped sub-polylines
    pts = [(-5, 5), (5, 5), (5, 15), (15, 15)]
    runs = tiling._clip_polyline(pts, (0, 0, 10, 10))
    assert runs and all(len(r) >= 2 for r in runs)
    for r in runs:
        assert all(0 <= x <= 10 and 0 <= y <= 10 for x, y in r)


def test_clip_filled_polygon_to_rect():
    # a big square clipped by a smaller rect → clipped to the rect
    poly = polygon([(0, 0), (100, 0), (100, 100), (0, 100)])
    clipped = tiling.clip_to_rect(poly, (10, 10, 40, 40))
    assert len(clipped) == 1
    p = clipped[0]
    assert p.fill
    xs = [x for x, _ in p.points]
    ys = [y for _, y in p.points]
    assert min(xs) >= 10 and max(xs) <= 40 and min(ys) >= 10 and max(ys) <= 40


def test_clip_polygon_holes_preserved():
    p = polygon([(0, 0), (100, 0), (100, 100), (0, 100)],
                holes=[[(40, 40), (60, 40), (60, 60), (40, 60)]])
    # rect fully containing the hole keeps it
    clipped = tiling.clip_to_rect(p, (20, 20, 80, 80))[0]
    assert len(clipped.holes) == 1


def test_dot_clipped_by_centre_membership():
    inside = tiling.clip_to_rect(Dot(5, 5, 3), (0, 0, 10, 10))
    outside = tiling.clip_to_rect(Dot(50, 50, 3), (0, 0, 10, 10))
    assert len(inside) == 1 and outside == []


def test_tiles_cover_all_dots_with_overlap():
    # every dot centre must appear in at least one tile (translated back)
    st = _big_stencil()
    tiles = sl.tile_stencil(st, 100, 100, overlap=20, crop_marks=False)
    recovered = set()
    for t in tiles:
        x0, y0, _, _ = t.rect
        for layer in t.stencil.layers:
            for prim in layer.primitives:
                if isinstance(prim, Dot):
                    recovered.add((round(prim.x + x0), round(prim.y + y0)))
    for d in (50, 50), (150, 90), (240, 170):
        assert d in recovered


# ════════════════════════════════════════════════════════════════════════════
# Phase 7 — cuttability analysis ("can we cut without losing information?")
# ════════════════════════════════════════════════════════════════════════════

def _disc(size, cx, cy, r):
    yy, xx = np.mgrid[0:size, 0:size]
    return np.hypot(xx - cx, yy - cy) <= r


def test_cuttable_solid_with_hole():
    cut = _disc(80, 40, 40, 12)              # one round hole in a solid sheet
    rep = fab.analyze_cuttability(fab.StencilMask(cut), min_feature_px=3)
    assert rep.cuttable
    assert rep.at_risk_px == 0
    assert rep.score == pytest.approx(1.0)
    assert rep.single_piece
    assert rep.regions == []


def test_all_material_is_trivially_cuttable():
    rep = fab.analyze_cuttability(fab.StencilMask(np.zeros((40, 40), bool)))
    assert rep.cuttable and rep.score == pytest.approx(1.0)


def test_all_cut_is_not_cuttable():
    rep = fab.analyze_cuttability(fab.StencilMask(np.ones((40, 40), bool)))
    assert not rep.cuttable
    assert rep.material_px == 0 and rep.score == 0.0


def test_ring_has_one_isolated_bridgeable_island():
    yy, xx = np.mgrid[0:80, 0:80]
    r = np.hypot(xx - 40, yy - 40)
    cut = (r >= 18) & (r <= 30)              # annular cut → centre island
    rep = fab.analyze_cuttability(fab.StencilMask(cut), min_feature_px=3)
    assert not rep.cuttable
    assert len(rep.regions) == 1
    reg = rep.regions[0]
    assert reg.kind == "isolated"
    assert reg.bridgeable
    assert reg.area == pytest.approx(np.pi * 18 ** 2, rel=0.1)
    assert rep.needs_bridges == 1
    # the big centre is a real island (information loss), not thin material
    assert rep.island_count == 1 and rep.island_px > 0
    assert rep.thin_px == 0 and rep.loses_information


def test_island_mask_marks_enclosed_material():
    yy, xx = np.mgrid[0:80, 0:80]
    r = np.hypot(xx - 40, yy - 40)
    cut = (r >= 18) & (r <= 30)              # ring → centre disc is the island
    im = fab.island_mask(fab.StencilMask(cut), min_feature_px=2)
    assert im.dtype == bool and im.shape == (80, 80)
    assert im[40, 40]                        # centre disc flagged
    assert not im[0, 0]                      # border material is safe
    assert im.sum() == pytest.approx(np.pi * 18 ** 2, rel=0.1)
    # all-solid sheet → no islands
    assert not fab.island_mask(fab.StencilMask(np.zeros((20, 20), bool))).any()


def test_min_island_area_drops_speckle():
    # one big enclosed island + a 1-px speckle island
    cut = np.zeros((60, 60), bool)
    yy, xx = np.mgrid[0:60, 0:60]
    cut[(np.hypot(xx - 30, yy - 30) >= 10) & (np.hypot(xx - 30, yy - 30) <= 18)] = True
    cut[2, 2] = False  # (already material) — make a speckle: ring around a single px
    cut[0:5, 0:5] = True
    cut[2, 2] = False  # 1-px material island enclosed by a 5x5 cut block
    big = fab.analyze_cuttability(fab.StencilMask(cut), min_feature_px=2, min_island_area=1)
    filt = fab.analyze_cuttability(fab.StencilMask(cut), min_feature_px=2, min_island_area=4)
    assert big.island_count > filt.island_count        # speckle dropped by the filter


def test_islands_vs_thin_material_are_separated():
    # a thin straight isthmus of material (weak-neck), no enclosed island
    mat = np.zeros((80, 80), bool)
    mat[0:6, :] = True            # anchored strip
    mat[6:60, 39:41] = True       # 2-px neck hanging down (no enclosed pocket)
    rep = fab.analyze_cuttability(fab.StencilMask(~mat), min_feature_px=6)
    assert rep.island_count == 0          # nothing falls out…
    assert rep.thin_px > 0                # …but it's flagged as thin/fragile
    assert not rep.loses_information


def _weak_neck_mask():
    mat = np.zeros((80, 80), bool)
    mat[0:6, :] = True            # strip anchored to the top frame
    mat[6:34, 39:41] = True       # 2-px neck
    mat[34:70, 20:60] = True      # the blob hanging off it
    return fab.StencilMask(~mat)


def test_weak_neck_flagged_when_below_min_feature():
    rep = fab.analyze_cuttability(_weak_neck_mask(), min_feature_px=6)
    assert not rep.cuttable
    assert len(rep.regions) == 1
    assert rep.regions[0].kind == "weak-neck"
    # the blob's material still touches the frame through the neck → one piece
    assert rep.single_piece


def test_stricter_min_feature_never_reduces_risk():
    mask = _weak_neck_mask()
    loose = fab.analyze_cuttability(mask, min_feature_px=1).at_risk_px
    strict = fab.analyze_cuttability(mask, min_feature_px=6).at_risk_px
    assert strict >= loose


def test_subkerf_hole_blocks_cuttable():
    cut = np.zeros((40, 40), bool)
    cut[20, 20] = True                       # 1-px hole — below any sane kerf
    rep = fab.analyze_cuttability(fab.StencilMask(cut), min_feature_px=3)
    assert rep.subkerf_hole_count == 1
    assert not rep.cuttable


def test_safe_and_at_risk_partition_material():
    mask = _weak_neck_mask()
    safe = fab.safe_material(mask, min_feature_px=6)
    risk = fab.at_risk_material(mask, min_feature_px=6)
    # safe ∪ risk == material, and they don't overlap
    assert np.array_equal(safe | risk, mask.material)
    assert not (safe & risk).any()


def test_bridges_reduce_at_risk_material():
    yy, xx = np.mgrid[0:80, 0:80]
    r = np.hypot(xx - 40, yy - 40)
    mask = fab.StencilMask((r >= 18) & (r <= 30))
    before = fab.analyze_cuttability(mask, min_feature_px=3).at_risk_px
    bridged, _ = fab.add_bridges(mask, width=4)
    after = fab.analyze_cuttability(bridged, min_feature_px=3).at_risk_px
    assert after < before


def test_report_summary_is_string():
    rep = fab.analyze_cuttability(fab.StencilMask(_disc(60, 30, 30, 10)))
    assert isinstance(str(rep), str)
    assert "verdict" in rep.summary()


# ─── optimize_for_cutting (cut-ready generation) ──────────────────────────────

def test_optimize_for_cutting_returns_cut_polygons_and_bridges_islands():
    # a filled frame (square with a square hole) → its rasterised centre is a
    # material island enclosed by the cut frame.
    ring = sl.polygon([(10, 10), (70, 10), (70, 70), (10, 70)],
                      holes=[[(30, 30), (50, 30), (50, 50), (30, 50)]])
    st = sl.Stencil(80, 80)
    st.layer("key", color=(0, 0, 0)).add(ring)

    before = fab.analyze_cuttability(fab.StencilMask.from_stencil(st), min_feature_px=2)
    assert len(before.regions) >= 1            # the enclosed centre is at-risk

    cut = sl.optimize_for_cutting(st, bridge_width=4, min_island_area=4)
    assert cut.primitive_count > 0
    assert all(isinstance(p, Polyline) and p.fill and p.closed
               for L in cut.layers for p in L.primitives)

    after = fab.analyze_cuttability(fab.StencilMask.from_stencil(cut), min_feature_px=2)
    assert after.at_risk_px < before.at_risk_px   # bridging reduced the risk


def test_optimize_for_cutting_preserves_layers():
    st = sl.Stencil(40, 40)
    st.layer("cyan", color=(0, 174, 239)).add(Dot(20, 20, 8))
    st.layer("key", color=(0, 0, 0)).add(Dot(10, 10, 6))
    cut = sl.optimize_for_cutting(st)
    assert [l.name for l in cut.layers] == ["cyan", "key"]
    assert [l.color for l in cut.layers] == [(0, 174, 239), (0, 0, 0)]


# ─── new patterns: splotches (shadow blobs) & threshold_lines (self-bridging) ──

def test_splotches_filled_blobs_grow_with_coverage():
    dark = sl.splotches(np.full((60, 60), 0.95), cell=12, seed=1)
    faint = sl.splotches(np.full((60, 60), 0.2), cell=12, seed=1)
    assert dark and faint
    assert all(isinstance(p, Polyline) and p.fill and p.closed for p in dark)

    def extent(polys):
        return max(max(x for x, _ in p.points) - min(x for x, _ in p.points)
                   for p in polys)
    assert extent(dark) > extent(faint)        # darker → bigger blobs


def test_splotches_skip_highlights_and_need_2d():
    assert sl.splotches(np.zeros((40, 40)), cell=10) == []
    with pytest.raises(ValueError):
        sl.splotches(np.zeros((8, 8, 3)))


def test_threshold_lines_only_cut_in_dark_regions():
    plane = np.zeros((40, 60))
    plane[:, :30] = 0.9                        # left half dark, right half light
    strips = sl.threshold_lines(plane, threshold=0.5, period=8, duty=0.5)
    assert strips
    assert all(p.fill for p in strips)
    assert all(min(x for x, _ in p.points) < 32 for p in strips)


def test_threshold_lines_zero_duty_cuts_nothing():
    plane = np.full((40, 40), 0.9)
    assert sl.threshold_lines(plane, threshold=0.5, duty=0.0) == []


def test_threshold_lines_self_bridges_enclosed_material():
    yy, xx = np.mgrid[0:120, 0:120]
    r = np.hypot(xx - 60, yy - 60)
    plane = np.zeros((120, 120))
    plane[(r >= 20) & (r <= 48)] = 0.9

    solid = sl.Stencil(120, 120)
    solid.layer("k").add(sl.polygon(
        [(60 + 48 * np.cos(a), 60 + 48 * np.sin(a)) for a in np.linspace(0, 2 * np.pi, 48)],
        holes=[[(60 + 20 * np.cos(a), 60 + 20 * np.sin(a)) for a in np.linspace(0, 2 * np.pi, 32)]]))
    carried = sl.Stencil(120, 120)
    carried.layer("k").add(sl.threshold_lines(plane, threshold=0.5, period=8, duty=0.5))

    solid_r = fab.analyze_cuttability(fab.StencilMask.from_stencil(solid), min_feature_px=2)
    carried_r = fab.analyze_cuttability(fab.StencilMask.from_stencil(carried), min_feature_px=2)
    assert not solid_r.cuttable and solid_r.regions    # centre island falls out
    assert carried_r.cuttable                          # carrier ribs hold it
    assert carried_r.at_risk_px < solid_r.at_risk_px


def test_new_patterns_in_registry():
    assert {"splotches", "threshold_lines"} <= set(PATTERN_NAMES)
    plane = np.full((48, 48), 0.8)
    for name in ("splotches", "threshold_lines"):
        prims = generate(plane, name, cell=10, angle=0)
        assert prims and all(isinstance(p, (Dot, Polyline)) for p in prims)


# ─── line_screen (amplitude-modulated line stencil, street-art look) ──────────

def _poly_area(p):
    pts = p.points
    return 0.5 * abs(sum(pts[i][0] * pts[(i + 1) % len(pts)][1]
                         - pts[(i + 1) % len(pts)][0] * pts[i][1]
                         for i in range(len(pts))))


def test_line_screen_ribbons_are_filled_polygons():
    out = sl.line_screen(np.full((40, 40), 0.6), period=6, angle=0)
    assert out and all(isinstance(p, Polyline) and p.fill and p.closed for p in out)


def test_line_screen_width_grows_with_coverage():
    dark = sl.line_screen(np.full((40, 40), 0.95), period=6, angle=0)
    faint = sl.line_screen(np.full((40, 40), 0.15), period=6, angle=0)
    assert dark and faint
    # darker → fatter ribbons → more filled area
    assert sum(_poly_area(p) for p in dark) > sum(_poly_area(p) for p in faint)


def test_line_screen_blank_highlights_and_need_2d():
    assert sl.line_screen(np.zeros((30, 30)), period=6) == []   # below min_coverage
    with pytest.raises(ValueError):
        sl.line_screen(np.zeros((8, 8, 3)))


def test_line_screen_in_registry():
    assert "line_screen" in PATTERN_NAMES
    prims = generate(np.full((40, 40), 0.7), "line_screen", cell=6, angle=0)
    assert prims and all(isinstance(p, Polyline) for p in prims)


def test_line_screen_wave_undulates():
    plane = np.full((60, 60), 0.8)
    straight = sl.line_screen(plane, period=8, angle=0, wave_amplitude=0)
    wavy = sl.line_screen(plane, period=8, angle=0, wave_amplitude=6, wave_length=30)
    assert straight and wavy and all(p.fill for p in wavy)

    def yspan(p):
        ys = [y for _, y in p.points]
        return max(ys) - min(ys)
    # undulation makes ribbons cover a far larger vertical range than flat ones
    assert max(yspan(p) for p in wavy) > max(yspan(p) for p in straight)


# ════════════════════════════════════════════════════════════════════════════
# Phase 8 — physical sizing / printing on sheets
# ════════════════════════════════════════════════════════════════════════════

from tanuki.mori.stencil_lab import sizing


def _toy_mm_ready():
    st = sl.Stencil(100, 80)          # 100×80 px
    st.layer("key", color=(0, 0, 0)).add([Dot(20, 20, 6),
                                          sl.polygon([(0, 0), (40, 0), (40, 40), (0, 40)])])
    return st


def test_unit_conversions_roundtrip():
    assert sizing.mm_to_px(25.4, 100) == pytest.approx(100)
    assert sizing.px_to_mm(100, 100) == pytest.approx(25.4)
    assert sizing.px_for_print(254, 100) == 1000


def test_paper_size_and_landscape():
    assert sizing.paper_size("a4") == (210, 297)
    assert sizing.paper_size("a4", landscape=True) == (297, 210)
    assert sizing.paper_size("pliego") == (700, 1000)
    with pytest.raises(ValueError):
        sizing.paper_size("nope")


def test_scale_stencil_scales_everything():
    st = _toy_mm_ready()
    big = sizing.scale_stencil(st, 2.0, units="mm")
    assert big.width == 200 and big.height == 160 and big.units == "mm"
    d = next(p for L in big.layers for p in L.primitives if isinstance(p, Dot))
    assert (d.x, d.y, d.r) == (40, 40, 12)


def test_fit_to_physical_keeps_aspect():
    st = _toy_mm_ready()                # aspect 100:80 = 1.25
    mm = sizing.fit_to_physical(st, width_mm=500)
    assert mm.units == "mm"
    assert mm.width == pytest.approx(500)
    assert mm.height == pytest.approx(400)     # 500 * 80/100
    with pytest.raises(ValueError):
        sizing.fit_to_physical(st)             # needs a dimension


def test_sheets_needed_and_tile_to_paper_fit():
    mm = sizing.fit_to_physical(_toy_mm_ready(), width_mm=700)   # 700×560 mm
    cols, rows = sizing.sheets_needed(mm, "a4", margin_mm=10, overlap_mm=10)
    assert cols >= 2 and rows >= 2                # a 70 cm design needs several A4
    bw, bh = sizing.printable_area("a4", margin_mm=10)
    tiles = sizing.tile_to_paper(mm, "a4", margin_mm=10, overlap_mm=10)
    assert len(tiles) == cols * rows
    assert all(t.stencil.width <= bw + 0.01 and t.stencil.height <= bh + 0.01
               for t in tiles)


def test_poster_by_cols():
    scaled, tiles = sizing.poster(_toy_mm_ready(), "a4", cols=3,
                                  margin_mm=10, overlap_mm=10)
    assert scaled.units == "mm"
    # 3 sheets across (minus overlaps) → at least 3 columns of tiles
    assert max(t.col for t in tiles) + 1 >= 3


def test_svg_emits_mm_dimensions():
    mm = sizing.fit_to_physical(_toy_mm_ready(), width_mm=300)
    svg = sl.to_svg(mm)
    assert 'width="300mm"' in svg and 'mm"' in svg


def test_pdf_scales_mm_to_points():
    mm = sizing.fit_to_physical(_toy_mm_ready(), width_mm=100)   # 100 mm
    pdf = sl.to_pdf(mm).decode("latin-1")
    m = re.search(r"MediaBox \[0 0 ([\d.]+) ", pdf)
    assert float(m.group(1)) == pytest.approx(100 * 72 / 25.4, rel=1e-3)   # ≈283 pt
    # px stencils stay 1:1 (no scaling)
    px = sl.to_pdf(_toy_mm_ready()).decode("latin-1")
    assert "MediaBox [0 0 100 80]" in px


# ════════════════════════════════════════════════════════════════════════════
# Phase 9 — FastAPI GUI (skipped unless fastapi + httpx are installed)
# ════════════════════════════════════════════════════════════════════════════

def _gui_client():
    pytest.importorskip("fastapi")
    pytest.importorskip("httpx")
    from fastapi.testclient import TestClient
    from tanuki.mori.stencil_lab.gui import app
    return TestClient(app)


def _upload_tanuki(client):
    img = Path(__file__).resolve().parents[1] / "mori/stencil_lab/docs/tanuki.jpg"
    with open(img, "rb") as f:
        return client.post("/api/upload",
                           files={"file": ("t.jpg", f, "image/jpeg")}).json()["id"]


def test_gui_index_and_preview():
    c = _gui_client()
    assert c.get("/").status_code == 200
    uid = _upload_tanuki(c)
    d = c.get("/api/preview", params={"id": uid, "method": "cmyk",
                                      "pattern": "dots", "cell": 7, "max_side": 320}).json()
    # per-plate analysis: one entry per CMYK channel, with its own island count
    assert [l["name"] for l in d["layers"]] == ["cyan", "magenta", "yellow", "key"]
    assert all("islands" in l and "thin" in l for l in d["layers"])
    assert d["svg"].count("<g ") == 4          # one toggleable group per plate
    assert d["status"] in ("clean", "bridge", "loss")
    assert isinstance(d["islands"], int) and 0.0 <= d["thin"] <= 1.0
    assert c.get("/api/preview", params={"id": "bogus"}).status_code == 404


def test_gui_export_svg_and_paper_zip():
    import io, zipfile
    c = _gui_client()
    uid = _upload_tanuki(c)
    r = c.post("/api/export", data={"id": uid, "method": "grayscale",
               "pattern": "line_screen", "cell": 8, "fmt": "svg",
               "optimize": "true", "max_side": 300})
    assert r.status_code == 200 and r.headers["content-type"] == "image/svg+xml"
    # output size = tabloid (landscape) split across A4 → a zip of sheets
    r = c.post("/api/export", data={"id": uid, "method": "grayscale", "pattern": "dots",
               "cell": 8, "fmt": "pdf", "optimize": "true", "max_side": 260,
               "out_size": "tabloid", "landscape": "true", "paper": "a4"})
    assert r.status_code == 200 and r.headers["content-type"] == "application/zip"
    assert len(zipfile.ZipFile(io.BytesIO(r.content)).namelist()) > 1


def test_gui_islands_overlay_toggle():
    c = _gui_client()
    uid = _upload_tanuki(c)
    base = {"id": uid, "method": "grayscale", "pattern": "dots",
            "cell": 4, "max_side": 280}
    off = c.get("/api/preview", params={**base, "show_islands": "false"}).json()
    on = c.get("/api/preview", params={**base, "show_islands": "true"}).json()
    assert "<image" not in off["svg"]
    # the overlay is a transparent red PNG embedded in the SVG, scaling with it
    assert "<image" in on["svg"] and "data:image/png;base64," in on["svg"]
    # the toggle button is wired up in the page
    assert 'id="toggleisl"' in c.get("/").text
