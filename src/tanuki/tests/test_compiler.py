"""Tests for the Blender compiler — verify generated scripts are valid Python."""

import ast

from tanuki.dsl import (
    cube,
    sphere,
    cylinder,
    cone,
    point,
    union,
    difference,
    intersect,
    join,
    clones,
    model,
    output,
    translate,
    rotate,
    place,
)
from tanuki.backends.blender.compiler import compile_to_source


def _compile_model(name: str, build_fn) -> str:
    """Helper: build a model, compile it, return the source."""
    with model(name) as ctx:
        build_fn()
    return compile_to_source(ctx.graph)


def _assert_valid_python(source: str) -> None:
    """Assert that *source* is syntactically valid Python."""
    ast.parse(source)


# ---------------------------------------------------------------------------
# Basic compilation
# ---------------------------------------------------------------------------


class TestCompilerBasics:
    def test_empty_model(self):
        with model("empty") as ctx:
            pass
        src = compile_to_source(ctx.graph)
        _assert_valid_python(src)
        assert "import bpy" in src

    def test_single_cube(self):
        src = _compile_model("single_cube", lambda: output(cube(10, 10, 10, "box")))
        _assert_valid_python(src)
        assert "GeometryNodeMeshCube" in src
        assert "NodeGroupOutput" in src

    def test_single_cylinder(self):
        src = _compile_model("cyl", lambda: output(cylinder(5, 10, "tube")))
        _assert_valid_python(src)
        assert "GeometryNodeMeshCylinder" in src

    def test_single_sphere(self):
        src = _compile_model("sph", lambda: output(sphere(3, "ball")))
        _assert_valid_python(src)
        assert "GeometryNodeMeshUVSphere" in src

    def test_single_cone(self):
        src = _compile_model("cn", lambda: output(cone(5, 0, 10, "pointy")))
        _assert_valid_python(src)
        assert "GeometryNodeMeshCone" in src


# ---------------------------------------------------------------------------
# Boolean operations
# ---------------------------------------------------------------------------


class TestCompilerBooleans:
    def test_difference(self):
        def build():
            a = cylinder(5, 10, "base")
            b = cylinder(3, 10, "hole")
            output(difference(a, [b]))

        src = _compile_model("diff", build)
        _assert_valid_python(src)
        assert "GeometryNodeMeshBoolean" in src
        assert '"DIFFERENCE"' in src

    def test_union(self):
        def build():
            a = cube(1, 1, 1, "a")
            b = cube(2, 2, 2, "b")
            output(union([a, b]))

        src = _compile_model("un", build)
        _assert_valid_python(src)
        assert '"UNION"' in src

    def test_intersect(self):
        def build():
            a = cube(1, 1, 1, "a")
            b = sphere(1, "b")
            output(intersect([a, b]))

        src = _compile_model("inter", build)
        _assert_valid_python(src)
        assert '"INTERSECT"' in src


# ---------------------------------------------------------------------------
# Transforms
# ---------------------------------------------------------------------------


class TestCompilerTransforms:
    def test_cube_with_position(self):
        src = _compile_model("pos", lambda: output(cube(1, 1, 1, "c") | place(5, 0, 0)))
        _assert_valid_python(src)
        assert "GeometryNodeSetPosition" in src

    def test_cube_with_rotation(self):
        src = _compile_model("rot", lambda: output(cube(1, 1, 1, "c") | rotate(90, 0, 0)))
        _assert_valid_python(src)
        assert "GeometryNodeTransform" in src

    def test_cube_with_translation(self):
        src = _compile_model("trans", lambda: output(cube(1, 1, 1, "c") | translate(1, 2, 3)))
        _assert_valid_python(src)
        assert "GeometryNodeTransform" in src


# ---------------------------------------------------------------------------
# Instancing
# ---------------------------------------------------------------------------


class TestCompilerInstancing:
    def test_clones(self):
        def build():
            s = cube(1, 1, 1, "sprocket")
            positions = [(0, 0, 0), (5, 0, 0), (10, 0, 0)]
            output(clones(s, positions))

        src = _compile_model("clones", build)
        _assert_valid_python(src)
        assert "GeometryNodeInstanceOnPoints" in src
        assert "GeometryNodeJoinGeometry" in src
        assert "GeometryNodePoints" in src


# ---------------------------------------------------------------------------
# Full lab/ models
# ---------------------------------------------------------------------------


class TestCompilerLabModels:
    def test_belt_holder(self):
        """Mirrors deprecated/lab/belt_holder.py"""
        def build():
            base = cylinder(5.5, 15, "hole1")
            hole2 = cylinder(4.5, 15, "hole2")
            output(difference(base, [hole2]))

        src = _compile_model("belt_holder", build)
        _assert_valid_python(src)
        assert "GeometryNodeMeshCylinder" in src
        assert "GeometryNodeMeshBoolean" in src
        assert src.count("GeometryNodeMeshCylinder") == 2

    def test_tray(self):
        """Mirrors deprecated/lab/tray.py"""
        def build():
            base = cube(107.5, 31, 9, "base")
            h1 = cube(103, 31, 9, "h_base_1") | place(0, -2, 2)
            h2 = cube(23, 31, 9, "h_base_2") | place(0, 0, 2)
            h3 = cube(12, 31, 9, "h_base_3") | place(25, 0, 2)
            h4 = cube(12, 31, 9, "h_base_4") | place(-25, 0, 2)
            h5 = cube(3, 31, 2, "h_base_5") | place(36.5, 0, -4.5)
            h6 = cube(3, 31, 2, "h_base_6") | place(-36.5, 0, -4.5)
            output(difference(base, [h1, h2, h3, h4, h5, h6]))

        src = _compile_model("tray", build)
        _assert_valid_python(src)
        # 7 cubes total
        assert src.count("GeometryNodeMeshCube") == 7

    def test_claw(self):
        """Mirrors deprecated/lab/claw.py (simplified)"""
        tolerance = 0.125

        def build():
            leg_l = cube(5.5, 50, 2, "leg_l") | place(14.75, 0, 0)
            leg_r = cube(5.5, 50, 2, "leg_r") | place(-14.75, 0, 0)
            top = cube(35, 10, 2, "top") | place(0, 25, 0)

            hook = cylinder(12, 2, "hook") | place(0, 35, 0)
            h_hook = cylinder(8, 2, "h_hook") | place(0, 35, 0)
            h_hook_2 = cube(20, 16, 2, "h_hook_2") | place(10, 30, 0)
            hook_diff = difference(hook, [h_hook, h_hook_2])

            sprocket = cube(2.7 - tolerance, 1.9 - tolerance, 3, "sprocket") | place(0, 0, 1)
            c_sprocket = 4.7498
            y_positions = [-20 + c_sprocket * i for i in range(9)]
            sprocket_positions = [
                (x, y, 0)
                for y in y_positions
                for x in [28.169 / 2, -28.169 / 2]
            ]
            sprockets = clones(sprocket, sprocket_positions)
            claw = union([leg_l, leg_r, top, hook_diff, sprockets])
            output(claw)

        src = _compile_model("claw", build)
        _assert_valid_python(src)
        assert "GeometryNodeInstanceOnPoints" in src
        assert '"UNION"' in src
