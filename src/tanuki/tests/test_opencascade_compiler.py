"""Tests for the OpenCascade.js backend (generated source only; no JS runtime)."""

from tanuki.backends.opencascade.compiler import compile_to_source
from tanuki.dsl import cube, cylinder, difference, mesh_polygon_solid, model, output, place


def _src(name, build):
    with model(name) as ctx:
        output(build())
    return compile_to_source(ctx.graph)


def test_mesh_polygon_solid_is_extruded_not_unsupported():
    pts = ((0.0, 0.0, 0.0), (10.0, 0.0, 0.0), (10.0, 5.0, 0.0))
    src = _src("tri", lambda: mesh_polygon_solid(pts, 3.0, "tri"))
    assert "Unsupported" not in src
    assert "BRepBuilderAPI_MakePolygon_1" in src
    assert "BRepPrimAPI_MakePrism_1" in src
    assert "gp_Vec_4(0, 0, 3.0)" in src


def test_booleans_pass_progress_range():
    src = _src("bool", lambda: difference(cube(2, 2, 2), [cylinder(0.5, 4) | place(0, 0, 0)]))
    assert "BRepAlgoAPI_Cut_3(" in src and "Message_ProgressRange_1()" in src
    assert "BRepPrimAPI_MakeBox_3(" in src and "BRepPrimAPI_MakeCylinder_3(" in src
