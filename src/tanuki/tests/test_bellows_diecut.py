"""Tests for the bellows_diecut mori module (single unit-cell phase).

Pure-Python (headless, no Blender): unit-cell pattern generation, relief sizing
from edge spacing, the OBJ/SVG/JSON exporters, and that the DSL male/female die
graphs compile to a Blender script.  The actual STL bake (Blender) is a separate
integration step.
"""

import json
import math

import pytest

from tanuki.backends.blender.compiler import compile_to_source
from tanuki.mori.bellows_diecut import (
    BellowsParams, generate_pattern, generate_diecut, PATTERNS,
)
from tanuki.mori.bellows_diecut.core.geometry import (
    FoldType, FoldLine, FoldPattern, cell_from_edges, merge_collinear,
    edge_spacing, relief_dims,
)
from tanuki.mori.bellows_diecut.core import diecut, exporter
from tanuki.mori.bellows_diecut import patterns

# Expected (mountain, valley) edge counts per unit cell — from the SVG reference.
EXPECTED_COUNTS = {
    "yoshimura": (4, 2),    # one diamond: 4 arms (M) + middle & tip/tail axes (V)
    "miura": (5, 7),
    "waterbomb": (2, 7),
    "kresling": (7, 2),
    "resch": (15, 2),
    "accordion": (4, 10),   # 2-row trapezoid brick: long bases (M), shorts + slants (V)
    "accordion_corners": (2, 7),
}


def _params():
    return BellowsParams(cell_scale=0.25)


# ---------------------------------------------------------------------------
# Parameters
# ---------------------------------------------------------------------------

def test_params_defaults_and_dict():
    p = BellowsParams()
    p.validate()
    d = p.to_dict()
    assert d["cell_scale"] == p.cell_scale
    # Relief is auto by default (sized from edge spacing).
    assert p.ridge_height is None and p.ridge_width is None


@pytest.mark.parametrize("bad", [
    dict(cell_scale=0),
    dict(material_thickness=-1),
    dict(ridge_height=0),
    dict(ridge_width=-2),
    dict(base_thickness=0),
    dict(width_ratio=0),
    dict(margin=-1),
])
def test_params_validate_rejects_bad(bad):
    with pytest.raises(ValueError):
        BellowsParams(**bad).validate()


# ---------------------------------------------------------------------------
# Unit-cell pattern generation
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("name", PATTERNS)
def test_pattern_edge_counts_match_svg(name):
    pat = generate_pattern(name, _params())
    assert isinstance(pat, FoldPattern) and pat.name == name
    s = pat.summary()
    m, v = EXPECTED_COUNTS[name]
    assert (s["mountain"], s["valley"]) == (m, v)
    assert s["boundary"] == 4


@pytest.mark.parametrize("name", PATTERNS)
def test_pattern_is_y_up_from_origin(name):
    p = _params()
    pat = generate_pattern(name, p)
    x0, y0, x1, y1 = pat.bounds()
    assert x0 == pytest.approx(0.0) and y0 == pytest.approx(0.0)
    assert x1 > 0 and y1 > 0
    # cell_scale acts as a linear scale on the tile size.
    pat2 = generate_pattern(name, BellowsParams(cell_scale=0.5))
    assert pat2.width == pytest.approx(2 * pat.width)


def test_cell_scale_changes_size_not_topology():
    a = generate_pattern("yoshimura", BellowsParams(cell_scale=0.25))
    b = generate_pattern("yoshimura", BellowsParams(cell_scale=1.0))
    assert a.summary() == b.summary()


def test_cell_from_edges_flips_y_and_normalises():
    # One mountain edge from (0, 0) to (10, 20) in Y-down template space.
    pat = cell_from_edges("t", [(0, 0, 10, 20)], [(0, 0, 0, 20)], scale=2.0)
    xs = [c for fl in pat.lines_of(FoldType.MOUNTAIN) for c in (fl.p0, fl.p1)]
    # Width 10 → 20mm, height 20 → 40mm; Y flipped so template y=0 maps to top.
    assert pat.width == pytest.approx(20.0)
    assert pat.height == pytest.approx(40.0)


def test_registry_and_unknown_pattern():
    assert set(patterns.REGISTRY) == set(PATTERNS)
    with pytest.raises(KeyError):
        patterns.get_generator("nope")


def test_foldline_geometry_helpers():
    fl = FoldLine((0.0, 0.0), (3.0, 4.0), FoldType.MOUNTAIN)
    assert fl.length == pytest.approx(5.0)
    assert fl.midpoint == pytest.approx((1.5, 2.0))
    assert fl.angle_deg == pytest.approx(math.degrees(math.atan2(4, 3)))


def test_merge_collinear_collapses_overlapping_runs():
    folds = [
        FoldLine((0, 0), (10, 0), FoldType.VALLEY),
        FoldLine((9, 0), (20, 0), FoldType.VALLEY),
        FoldLine((20, 0), (30, 0), FoldType.VALLEY),
        FoldLine((0, 0), (10, 10), FoldType.MOUNTAIN),
    ]
    merged = merge_collinear(folds)
    valleys = [m for m in merged if m.kind == FoldType.VALLEY]
    assert len(valleys) == 1 and valleys[0].length == pytest.approx(30.0)


# ---------------------------------------------------------------------------
# Relief sizing from edge spacing
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("name", PATTERNS)
def test_edge_spacing_positive_and_scales(name):
    pat = generate_pattern(name, _params())
    s = edge_spacing(pat)
    assert 0 < s < max(pat.width, pat.height)
    # Spacing scales linearly with cell_scale.
    s2 = edge_spacing(generate_pattern(name, BellowsParams(cell_scale=0.5)))
    assert s2 == pytest.approx(2 * s, rel=1e-6)


@pytest.mark.parametrize("name", PATTERNS)
def test_relief_dims_auto_and_override(name):
    p = _params()
    pat = generate_pattern(name, p)
    rw, rh = relief_dims(pat, p)
    s = edge_spacing(pat)
    assert rw == pytest.approx(p.width_ratio * s)
    assert rh == pytest.approx(p.height_ratio * rw)
    # Explicit overrides win.
    rw2, rh2 = relief_dims(pat, BellowsParams(ridge_width=4.0, ridge_height=1.5))
    assert (rw2, rh2) == (4.0, 1.5)


# ---------------------------------------------------------------------------
# Foldcore (folded surface — no flat regions, matched dies)
# ---------------------------------------------------------------------------

import numpy as np
from collections import Counter
from tanuki.mori.bellows_diecut.core import foldcore


@pytest.mark.parametrize("name", PATTERNS)
def test_arrangement_planar_euler(name):
    pat = generate_pattern(name, _params())
    pts, edges = foldcore.arrangement(pat)
    fcs = foldcore.faces(pts, edges)
    # Connected planar graph counting only bounded faces: V − E + F = 1.
    assert len(pts) - len(edges) + len(fcs) == 1


def test_arrangement_splits_crossings():
    # The waterbomb / resch X-diagonals cross at an interior point that must
    # become a vertex (so the X is split into 4 sub-edges).
    pat = generate_pattern("waterbomb", _params())
    pts, edges = foldcore.arrangement(pat)
    # The plain pattern has 6 outline+frame corners; the X adds the centre.
    assert len(pts) > len(pat.vertices)


@pytest.mark.parametrize("name", PATTERNS)
def test_no_flat_facets(name):
    p = _params()
    pat = generate_pattern(name, p)
    pts, z, tris, _bl = foldcore.build_surface(pat, p)
    v3 = np.column_stack([pts, z])
    for a, b, c in tris:
        n = np.cross(v3[b] - v3[a], v3[c] - v3[a])
        ln = np.linalg.norm(n)
        assert ln > 1e-9 and abs(n[2] / ln) <= 0.999, "horizontal facet (flat region)"


@pytest.mark.parametrize("name", PATTERNS)
@pytest.mark.parametrize("side", ["male", "female"])
def test_die_is_watertight(name, side):
    p = _params()
    pat = generate_pattern(name, p)
    verts, faces = foldcore.build_die(pat, p, side)
    assert len(verts) > 0 and len(faces) > 0
    edges = Counter()
    for a, b, c in faces:
        for e in ((a, b), (b, c), (c, a)):
            edges[tuple(sorted(e))] += 1
    assert all(v == 2 for v in edges.values()), "non-manifold edge in die"


def test_matched_dies_offset_by_thickness():
    p = _params()
    pat = generate_pattern("yoshimura", p)
    pts, z, _t, _b = foldcore.build_surface(pat, p)
    vm, _ = foldcore.build_die(pat, p, "male")
    vf, _ = foldcore.build_die(pat, p, "female")
    # Male top peaks at the surface max; female folded face is the same surface
    # lifted by one fabric thickness.
    assert vm[:, 2].max() == pytest.approx(z.max(), abs=1e-6)
    assert vf[:, 2].min() == pytest.approx(z.min() + p.material_thickness, abs=1e-6)


# ---------------------------------------------------------------------------
# DSL import-OBJ die graphs + exporters
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("name", PATTERNS)
def test_die_graphs_compile(name, tmp_path):
    p = _params()
    pat = generate_pattern(name, p)
    graphs = diecut.build_graphs(pat, p, tmp_path)
    assert set(graphs) == {"male", "female"}
    assert graphs["male"].name == f"{name}_male"
    assert (tmp_path / f"{name}_male.obj").exists()
    for g in graphs.values():
        src = compile_to_source(g)
        assert "import bpy" in src and "GeometryNodeImportOBJ" in src


def test_export_obj_groups_and_svg(tmp_path):
    pat = generate_pattern("waterbomb", _params())
    obj = exporter.export_obj(pat, tmp_path / "w.obj").read_text()
    for grp in ("g mountain", "g valley", "g boundary"):
        assert grp in obj
    svg = exporter.export_svg(pat, tmp_path / "w.svg").read_text()
    assert svg.startswith("<?xml") and svg.count("<line") == len(pat.fold_lines)


def test_export_json_roundtrip(tmp_path):
    p = _params()
    pat = generate_pattern("resch", p)
    data = json.loads(exporter.export_json(pat, p, tmp_path / "r.json").read_text())
    assert data["pattern"] == "resch"
    assert data["parameters"]["cell_scale"] == p.cell_scale
    assert len(data["fold_lines"]) == len(pat.fold_lines)


# ---------------------------------------------------------------------------
# Tessellation (repeat the tile across the print bed)
# ---------------------------------------------------------------------------

from tanuki.mori.bellows_diecut import generate_tessellation
from tanuki.mori.bellows_diecut.core import tessellate as ts


@pytest.mark.parametrize("name", PATTERNS)
def test_tile_specs_fit_print_bed(name):
    w, h = ts.tessellated_size(name)
    assert 0 < w <= ts.PRINT_BED and 0 < h <= ts.PRINT_BED
    # The tiling rule may grow (brick) or shrink (V-interlock) the footprint, but
    # it stays in the n×tile_X / m×tile_Y ballpark.
    (tx, ty), (n, m) = ts.TILE_SPECS[name]["tile"], ts.TILE_SPECS[name]["grid"]
    assert 0.6 * n * tx <= w <= 1.2 * n * tx
    assert 0.6 * m * ty <= h <= 1.2 * m * ty


def test_tile_depth_formula():
    # Z = tile_Y/2 − fabric − tolerance = tile_Y/2 − 0.8.
    assert ts.tile_depth(14.0) == pytest.approx(6.2)
    assert ts.tile_depth(17.0) == pytest.approx(7.7)


@pytest.mark.parametrize("name", PATTERNS)
def test_tessellate_replicates_unit_cell(name):
    n, m = ts.TILE_SPECS[name]["grid"]
    cell = generate_pattern(name, BellowsParams(cell_scale=1.0))
    tile = ts.tessellate(name)
    # One copy of the cell's creases per grid position (before merging at seams).
    per_cell = len(cell.mountains) + len(cell.valleys)
    assert len(tile.mountains) + len(tile.valleys) == per_cell * n * m


def test_brick_offsets_alternate_rows():
    # Miura/Yoshimura tile in running bond: odd rows are shifted half a tile, so
    # the tessellation is half a tile wider than a plain grid.
    tx, _ty = ts.TILE_SPECS["miura"]["tile"]
    n, _m = ts.TILE_SPECS["miura"]["grid"]
    w, _h = ts.tessellated_size("miura")
    assert w == pytest.approx(n * tx + 0.5 * tx)


def test_kresling_v_interlock_reduces_width():
    # Kresling's V notch interlocks (pitch_x < tile), so it is narrower than a
    # plain grid.
    tx, _ty = ts.TILE_SPECS["kresling"]["tile"]
    n, _m = ts.TILE_SPECS["kresling"]["grid"]
    w, _h = ts.tessellated_size("kresling")
    assert w < n * tx


def test_yoshimura_is_square_diamond_grid():
    # Yoshimura tiles as a plain square grid of diamonds (no interlock offset).
    assert ts.TILE_SPECS["yoshimura"]["tiling"] == "square"
    assert "pitch_x" not in ts.TILE_SPECS["yoshimura"]
    assert "pitch_y" not in ts.TILE_SPECS["yoshimura"]
    tx, ty = ts.TILE_SPECS["yoshimura"]["tile"]
    n, m = ts.TILE_SPECS["yoshimura"]["grid"]
    w, h = ts.tessellated_size("yoshimura")
    assert w == pytest.approx(n * tx) and h == pytest.approx(m * ty)


def test_yoshimura_relief_is_egg_crate():
    # The diamond grid pops in and out: the surface reaches both +A and −A.
    from tanuki.mori.bellows_diecut.core import foldcore
    pat = ts.tessellate("yoshimura", grid=(4, 4))
    params = ts.tile_params("yoshimura")
    _pts, z, _tris, _b = foldcore.build_surface(pat, params)
    amp = foldcore.fold_amplitude(pat, params)
    assert z.max() == pytest.approx(amp) and z.min() == pytest.approx(-amp)


@pytest.mark.parametrize("name", PATTERNS)
def test_tessellated_die_is_watertight(name):
    from collections import Counter as _C
    tile = ts.tessellate(name)
    params = ts.tile_params(name)
    verts, faces = foldcore.build_die(tile, params, "male")
    ec = _C()
    for a, b, c in faces:
        for e in ((a, b), (b, c), (c, a)):
            ec[tuple(sorted(e))] += 1
    assert all(v == 2 for v in ec.values())
    # Fold depth follows the README spec.
    assert params.ridge_height == pytest.approx(ts.tile_depth(ts.TILE_SPECS[name]["tile"][1]))


def test_generate_tessellation_writes_outputs(tmp_path):
    res = generate_tessellation("yoshimura", tmp_path, bake=False)
    assert set(res["paths"]) == {"obj", "svg", "json", "bpy"}
    assert (tmp_path / "mesh" / "yoshimura_tile_male.obj").exists()
    assert res["pattern"].name == "yoshimura_tile"


# ---------------------------------------------------------------------------
# Rollers (the fold pattern wrapped onto a cylinder)
# ---------------------------------------------------------------------------

from tanuki.mori.bellows_diecut import generate_rollers
from tanuki.mori.bellows_diecut.core import roller as rl


@pytest.mark.parametrize("name", PATTERNS)
@pytest.mark.parametrize("side", ["male", "female"])
def test_roller_is_watertight_cylinder(name, side):
    import numpy as np
    from collections import Counter as _C
    verts, faces = rl.build_roller(name, side)
    # Watertight: every edge shared by exactly two triangles.
    ec = _C()
    for a, b, c in faces:
        for e in ((a, b), (b, c), (c, a)):
            ec[tuple(sorted(e))] += 1
    assert all(v == 2 for v in ec.values()), "non-manifold edge in roller"
    # It is a cylinder: a bored core (min radius > 0) and a relief rim.
    r = np.hypot(verts[:, 0], verts[:, 1])
    assert r.min() > 0 and r.max() > r.min()
    assert verts[:, 2].ptp() > 0           # spans the axis


def test_min_tiles_around_is_grid_width():
    for name in PATTERNS:
        assert rl.min_tiles_around(name) == ts.TILE_SPECS[name]["grid"][0]


def test_generate_rollers_writes_outputs(tmp_path):
    res = generate_rollers("kresling", tmp_path, bake=False)
    assert set(res["paths"]) == {"obj", "svg", "json", "bpy"}
    assert (tmp_path / "mesh" / "kresling_roller_male.obj").exists()
    assert (tmp_path / "mesh" / "kresling_roller_female.obj").exists()
    bpy_src = res["paths"]["bpy"].read_text()
    assert "setup_kresling_roller_male" in bpy_src


# ---------------------------------------------------------------------------
# Parametric Geometry Nodes rollers (Blender script emitter)
# ---------------------------------------------------------------------------

from tanuki.mori.bellows_diecut import generate_rollers_gn
from tanuki.mori.bellows_diecut.core import roller_gn


@pytest.mark.parametrize("name", PATTERNS)
def test_flat_block_pitch_matches_tiling(name):
    import numpy as np
    verts, faces, dx, dy = roller_gn.flat_block(name)
    gn, gm = roller_gn._block_grid(name)
    spec = ts.TILE_SPECS[name]
    assert dx == pytest.approx(gn * spec.get("pitch_x", 1.0) * spec["tile"][0])
    assert dy == pytest.approx(gm * spec["tile"][1])
    # the block is a real surface centred near the origin
    assert len(verts) > 2 and len(faces) > 0
    assert abs(np.asarray(verts)[:, 0].mean()) < dx
    if name.startswith("accordion"):
        xs = np.asarray(verts)[:, 0]
        assert xs.max() - xs.min() == pytest.approx(dx)


@pytest.mark.parametrize("name", PATTERNS)
def test_gn_script_is_valid_and_parametric(name, tmp_path):
    import ast
    path = generate_rollers_gn(name, tmp_path)
    assert path.name == f"{name}_roller_gn.py"
    src = path.read_text()
    ast.parse(src)                                   # valid Python
    # exposes the BellowsRoller node group with the parametric sockets
    assert '"BellowsRoller"' in src
    for sock in ("Diameter", "Tiles around", "Tiles along", "Relief depth", "Core wall"):
        assert sock in src
    # builds both meshing rollers (male = +relief, female = −relief)
    assert f"{name}_roller_male" in src and f"{name}_roller_female" in src


def test_generate_diecut_writes_outputs_and_bake_script(tmp_path):
    # bake=False (no Blender in the fast suite): OBJ/SVG/JSON + self-contained
    # DSL bake script; STLs are produced only when baked in Blender.
    res = generate_diecut("yoshimura", _params(), tmp_path, bake=False)
    paths = res["paths"]
    assert set(paths) == {"obj", "svg", "json", "bpy"}
    for kind in paths:
        assert paths[kind].exists() and paths[kind].stat().st_size > 0
    bpy_src = paths["bpy"].read_text()
    assert "setup_yoshimura_male" in bpy_src and "bake_and_export_stl" in bpy_src


# ---------------------------------------------------------------------------
# JSON configuration (tile, fold height, axial repeats — rest auto)
# ---------------------------------------------------------------------------

from tanuki.mori.bellows_diecut import config, configure, write_config_template


@pytest.fixture
def _reset_config():
    yield
    config.reset()


def test_config_template_is_minimal_and_round_trips(tmp_path, _reset_config):
    path = write_config_template(tmp_path / "cfg.json")
    data = json.loads(path.read_text())
    assert set(data) == {"patterns"}
    for name in PATTERNS:
        assert set(data["patterns"][name]) == {"tile", "fold_height", "repeats", "around"}


def test_config_around_overrides_circumference(_reset_config):
    auto = ts.TILE_SPECS["waterbomb"]["grid"][0]
    configure({"patterns": {"waterbomb": {"around": auto + 3}}})
    assert ts.TILE_SPECS["waterbomb"]["grid"][0] == auto + 3
    # omitting around keeps the automatic value
    config.reset()
    assert ts.TILE_SPECS["waterbomb"]["grid"][0] == auto


def test_apply_config_sets_tile_fold_and_axial_repeats(_reset_config):
    around_before = ts.TILE_SPECS["yoshimura"]["grid"][0]
    configure({"patterns": {"yoshimura": {"tile": [22, 22], "fold_height": 3.0,
                                          "repeats": 5}}})
    spec = ts.TILE_SPECS["yoshimura"]
    assert spec["tile"] == (22.0, 22.0)
    assert spec["grid"] == (around_before, 5)          # circumference auto-kept
    assert spec["fold_height"] == 3.0
    # fold_height drives the relief amplitude
    pat = ts.tessellate("yoshimura", grid=(2, 2))
    params = ts.tile_params("yoshimura")
    from tanuki.mori.bellows_diecut.core import foldcore
    _p, z, _t, _b = foldcore.build_surface(pat, params)
    assert z.max() == pytest.approx(3.0) and z.min() == pytest.approx(-3.0)


def test_config_flows_into_generation(tmp_path, _reset_config):
    cfg = {"patterns": {"waterbomb": {"tile": [30, 30], "fold_height": 5, "repeats": 3}}}
    generate_tessellation("waterbomb", tmp_path, bake=False, config=cfg)
    _w, h = ts.tessellated_size("waterbomb")          # repeats (axial) = 3 × 30mm
    assert h == pytest.approx(90.0)


# ---------------------------------------------------------------------------
# Web UI server (stdlib http.server)
# ---------------------------------------------------------------------------

def test_web_preview_mesh_has_mesh_and_lines(_reset_config):
    from tanuki.mori.bellows_diecut.web.server import preview_mesh
    d = preview_mesh("yoshimura", 16, 16, 5.0)
    assert len(d["positions"]) > 0 and len(d["indices"]) > 0
    assert d["lines"]["mountain"] and len(d["bbox"]) == 4


def test_web_endpoints_serve_and_generate(tmp_path, _reset_config):
    import json as _json
    import threading
    import urllib.request
    from http.server import ThreadingHTTPServer
    from tanuki.mori.bellows_diecut.web.server import make_app

    httpd = ThreadingHTTPServer(("127.0.0.1", 0), make_app(tmp_path))
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{httpd.server_address[1]}"
    try:
        pats = _json.loads(urllib.request.urlopen(base + "/api/patterns").read())
        assert "yoshimura" in pats["patterns"]
        tile = _json.loads(urllib.request.urlopen(
            base + "/api/tile?pattern=waterbomb&tile_x=18&tile_y=18&fold_height=5").read())
        assert tile["positions"] and tile["lines"]["mountain"]
        req = urllib.request.Request(
            base + "/api/generate", method="POST",
            data=_json.dumps({"pattern": "waterbomb", "tile_x": 18, "tile_y": 18,
                              "fold_height": 5, "repeats": 3, "bake": False}).encode(),
            headers={"Content-Type": "application/json"})
        job_id = _json.loads(urllib.request.urlopen(req).read())["job_id"]
        # poll the background job to completion (no bake → fast)
        import time
        for _ in range(50):
            job = _json.loads(urllib.request.urlopen(base + "/api/job/" + job_id).read())
            if job["status"] != "running":
                break
            time.sleep(0.2)
        assert job["status"] == "done", job.get("error")
        assert any("roller" in f for f in job["files"])
        assert (tmp_path / "waterbomb_roller_gn.py").exists()
    finally:
        httpd.shutdown()
