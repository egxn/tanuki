"""Tests for migrated lab models — verify all build and compile to valid Python."""

import ast

import pytest

from tanuki.backends.blender.compiler import compile_to_source


def _assert_valid_python(source: str) -> None:
    """Assert that *source* is syntactically valid Python."""
    ast.parse(source)


# ── belt_holder ────────────────────────────────────────────────

@pytest.mark.skip(reason="belt_holder.py has not been migrated to the current DSL yet")
def test_belt_holder():
    from tanuki.mori.print_labo.belt_holder import create_belt_holder

    graph = create_belt_holder()
    source = compile_to_source(graph)
    _assert_valid_python(source)
    assert "GeometryNodeMeshCylinder" in source
    assert "GeometryNodeMeshBoolean" in source


# ── tray ───────────────────────────────────────────────────────

def test_tray():
    from tanuki.mori.print_labo.tray import create_tray

    graph = create_tray()
    source = compile_to_source(graph)
    _assert_valid_python(source)
    assert "GeometryNodeMeshCube" in source
    assert "DIFFERENCE" in source


# ── claw ───────────────────────────────────────────────────────

@pytest.mark.skip(reason="claw.py has not been migrated to the current DSL yet")
def test_claw():
    from tanuki.mori.print_labo.claw import create_claw

    graph = create_claw()
    source = compile_to_source(graph)
    _assert_valid_python(source)
    assert "GeometryNodeInstanceOnPoints" in source
    assert "UNION" in source


# ── trap_light — multiple sub‑models ─────────────────────────

def test_trap_light_case():
    from tanuki.mori.print_labo.trap_light import create_case

    graph = create_case()
    source = compile_to_source(graph)
    _assert_valid_python(source)
    assert "GeometryNodeMeshCylinder" in source


def test_trap_light_film_35mm():
    from tanuki.mori.print_labo.trap_light import create_cartridge_film_35mm

    graph = create_cartridge_film_35mm()
    source = compile_to_source(graph)
    _assert_valid_python(source)


def test_trap_light_film_roll():
    from tanuki.mori.print_labo.trap_light import create_film_roll

    graph = create_film_roll()
    source = compile_to_source(graph)
    _assert_valid_python(source)


def test_trap_light_knockout_top():
    from tanuki.mori.print_labo.trap_light import create_knockout_covers_top

    graph = create_knockout_covers_top()
    source = compile_to_source(graph)
    _assert_valid_python(source)


def test_trap_light_knockout_bottom():
    from tanuki.mori.print_labo.trap_light import create_knockout_covers_bottom

    graph = create_knockout_covers_bottom()
    source = compile_to_source(graph)
    _assert_valid_python(source)


def test_trap_light_film_lever():
    from tanuki.mori.print_labo.trap_light import create_film_lever

    graph = create_film_lever()
    source = compile_to_source(graph)
    _assert_valid_python(source)


def test_trap_light_film_box():
    from tanuki.mori.print_labo.trap_light import create_film_box

    graph = create_film_box()
    source = compile_to_source(graph)
    _assert_valid_python(source)


def test_trap_light_cog_roll():
    from tanuki.mori.print_labo.trap_light import cog_roll

    graph = cog_roll()
    source = compile_to_source(graph)
    _assert_valid_python(source)


def test_trap_light_lens_mount():
    from tanuki.mori.print_labo.trap_light import lens_mount

    graph = lens_mount()
    source = compile_to_source(graph)
    _assert_valid_python(source)


# ── minolta_tap ────────────────────────────────────────────────

def test_minolta_tap():
    from tanuki.mori.print_labo.minolta_tap import create_tap

    graph = create_tap()
    source = compile_to_source(graph)
    _assert_valid_python(source)
    assert "INTERSECT" in source


# ── mogura_exposimeter ─────────────────────────────────────────

def test_mogura_container():
    from tanuki.mori.print_labo.mogura_exposimeter import create_container

    graph = create_container()
    source = compile_to_source(graph)
    _assert_valid_python(source)


def test_mogura_box():
    from tanuki.mori.print_labo.mogura_exposimeter import create_box

    graph = create_box()
    source = compile_to_source(graph)
    _assert_valid_python(source)


def test_mogura_clockwork_knob():
    from tanuki.mori.print_labo.mogura_exposimeter import create_clockwork_knob

    graph = create_clockwork_knob()
    source = compile_to_source(graph)
    _assert_valid_python(source)


# ── film_spooler (35_120) ─────────────────────────────────────

def test_film_spooler():
    from tanuki.mori.print_labo.film_spooler import create_film_spooler

    graph = create_film_spooler()
    source = compile_to_source(graph)
    _assert_valid_python(source)


def test_film_spooler_h_base_120():
    from tanuki.mori.print_labo.film_spooler import create_h_base_120

    graph = create_h_base_120()
    source = compile_to_source(graph)
    _assert_valid_python(source)


# ── neganuki_scanner — full assembly ──────────────────────────

# Only functions that currently exist in neganuki_scanner.py.
# Removed: create_film_support, create_film_support_base, create_film,
#           create_motor_support, create_h_motor_cog, create_tol_cyl,
#           create_spacer, create_lamp_support_1/2, create_dummy_lamp,
#           create_sensor_support_j1, create_sensor_support_j1_column,
#           create_base_cam, create_cover
# (those parts of the scanner have not been modelled yet)
_SCANNER_FUNCS = [
    "create_sensor_support",
    "create_lens_support",
    "create_columns",
    "create_dummy_stepper",
    "create_cam_tripod_support",
    "create_film_slider",
    "create_film_slider_2",
    "create_film_slider_3",
    "create_dummy_film",
    "create_sprocket_gear",
]


@pytest.mark.parametrize("func_name", _SCANNER_FUNCS)
def test_neganuki_scanner(func_name):
    import tanuki.mori.print_labo.neganuki_scanner as mod

    func = getattr(mod, func_name)
    graph = func()
    source = compile_to_source(graph)
    _assert_valid_python(source)
