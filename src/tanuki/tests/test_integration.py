"""Integration tests — compile models and run them in Blender headless.

These tests are skipped when Blender is not available.
Run with:  PYTHONPATH=src pytest src/tanuki/tests/test_integration.py -v
"""

import ast
import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest

from tanuki.backends.blender.compiler import compile_to_source

# Skip all tests in this module if Blender is not installed
BLENDER = shutil.which("blender")
pytestmark = pytest.mark.skipif(BLENDER is None, reason="Blender not installed")


def _run_in_blender(script_source: str) -> subprocess.CompletedProcess:
    """Write *script_source* to a temp file and execute it in Blender background mode."""
    with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
        f.write(script_source)
        f.flush()
        script_path = f.name

    result = subprocess.run(
        [BLENDER, "--background", "--python", script_path],
        capture_output=True,
        text=True,
        timeout=60,
    )
    Path(script_path).unlink(missing_ok=True)
    return result


# ── Simple models ──────────────────────────────────────────────

@pytest.mark.skip(reason="belt_holder.py has not been migrated to the current DSL yet")
def test_belt_holder_in_blender():
    from tanuki.mori.print_labo.belt_holder import create_belt_holder

    graph = create_belt_holder()
    source = compile_to_source(graph)
    result = _run_in_blender(source)
    assert result.returncode == 0, f"Blender failed:\n{result.stderr}"


def test_tray_in_blender():
    from tanuki.mori.print_labo.tray import create_tray

    graph = create_tray()
    source = compile_to_source(graph)
    result = _run_in_blender(source)
    assert result.returncode == 0, f"Blender failed:\n{result.stderr}"


@pytest.mark.skip(reason="claw.py has not been migrated to the current DSL yet")
def test_claw_in_blender():
    from tanuki.mori.print_labo.claw import create_claw

    graph = create_claw()
    source = compile_to_source(graph)
    result = _run_in_blender(source)
    assert result.returncode == 0, f"Blender failed:\n{result.stderr}"


def test_minolta_tap_in_blender():
    from tanuki.mori.print_labo.minolta_tap import create_tap

    graph = create_tap()
    source = compile_to_source(graph)
    result = _run_in_blender(source)
    assert result.returncode == 0, f"Blender failed:\n{result.stderr}"


# ── Complex models ─────────────────────────────────────────────

def test_mogura_clockwork_in_blender():
    from tanuki.mori.print_labo.mogura_exposimeter import create_clockwork_knob

    graph = create_clockwork_knob()
    source = compile_to_source(graph)
    result = _run_in_blender(source)
    assert result.returncode == 0, f"Blender failed:\n{result.stderr}"


def test_trap_light_case_in_blender():
    from tanuki.mori.print_labo.trap_light import create_case

    graph = create_case()
    source = compile_to_source(graph)
    result = _run_in_blender(source)
    assert result.returncode == 0, f"Blender failed:\n{result.stderr}"


def test_neganuki_columns_in_blender():
    from tanuki.mori.print_labo.neganuki_scanner import create_columns

    graph = create_columns()
    source = compile_to_source(graph)
    result = _run_in_blender(source)
    assert result.returncode == 0, f"Blender failed:\n{result.stderr}"
