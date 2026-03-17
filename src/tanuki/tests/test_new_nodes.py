"""Tests for new node categories: mesh primitives, curves, mesh ops, instance ops."""

import ast

from tanuki.dsl import (
    circle,
    grid,
    ico_sphere,
    line,
    curve_arc,
    curve_circle,
    curve_line,
    curve_quadrilateral,
    curve_star,
    curve_spiral,
    bezier_segment,
    quadratic_bezier,
    extrude,
    subdivide,
    subdivide_surface,
    set_shade_smooth,
    merge_by_distance,
    dual_mesh,
    mesh_to_curve,
    mesh_to_points,
    mesh_to_volume,
    volume_to_mesh,
    set_mesh_normal,
    curve_to_mesh,
    realize_instances,
    rotate_instances,
    scale_instances,
    translate_instances,
    geometry_to_instance,
    instances_to_points,
    split_to_instances,
    fill_curve,
    fillet_curve,
    resample_curve,
    reverse_curve,
    subdivide_curve,
    trim_curve,
    curve_to_points,
    deform_curves_on_surface,
    sample_curve,
    set_curve_normal,
    set_curve_radius,
    set_curve_tilt,
    set_handle_positions,
    set_handle_type,
    set_spline_cyclic,
    set_spline_resolution,
    set_spline_type,
    edge_paths_to_curves,
    interpolate_curves,
    points_to_curves,
    curves_to_grease_pencil,
    grease_pencil_to_curves,
    string_to_curves,
    set_material,
    replace_material,
    set_material_index,
    distribute_points_in_volume,
    points_to_volume,
    volume_cube,
    convex_hull,
    delete_geometry,
    distribute_points_on_faces,
    duplicate_elements,
    flip_faces,
    scale_elements,
    split_edges,
    triangulate,
    bounding_box,
    separate_components,
    separate_geometry,
    set_id,
    set_point_radius,
    sort_elements,
    store_named_attribute,
    remove_named_attribute,
    points_to_vertices,
    set_geometry_name,
    set_face_set,
    set_selection,
    merge_layers,
    set_grease_pencil_depth,
    set_grease_pencil_softness,
    import_obj,
    import_stl,
    import_ply,
    import_csv,
    import_vdb,
    switch,
    get_named_grid,
    store_named_grid,
    set_grease_pencil_color,
    viewer,
    collection_info,
    object_info,
    curve_length,
    domain_size,
    geometry_proximity,
    sample_nearest,
    sample_index,
    attribute_statistic,
    raycast,
    sample_nearest_surface,
    sample_uv_surface,
    mesh_to_sdf_grid,
    mesh_to_density_grid,
    cube,
    sphere,
    join,
    clones,
    model,
    output,
    translate,
    rotate,
    scale_by,
)
from tanuki.ir.nodes import (
    IRGeometryOp,
    IRPrimitive,
    IRSeparateComponents,
    IRTransform,
    PrimitiveType,
)
from tanuki.backends.blender.compiler import compile_to_source


def _compile_model(name: str, build_fn) -> str:
    with model(name) as ctx:
        build_fn()
    return compile_to_source(ctx.graph)


def _assert_valid_python(source: str) -> None:
    ast.parse(source)


# ---------------------------------------------------------------------------
# New Mesh Primitives — IR level
# ---------------------------------------------------------------------------


class TestNewMeshPrimitives:
    def test_circle(self):
        c = circle(32, 1.0, "NGON", "ring")
        assert isinstance(c, IRPrimitive)
        assert c.primitive_type == PrimitiveType.CIRCLE
        assert c.properties["radius"] == 1.0
        assert c.properties["fill_type"] == "NGON"

    def test_grid(self):
        g = grid(2.0, 2.0, 10, 10, "floor")
        assert isinstance(g, IRPrimitive)
        assert g.primitive_type == PrimitiveType.GRID
        assert g.properties["size_x"] == 2.0

    def test_ico_sphere(self):
        s = ico_sphere(1.0, 3, "ball")
        assert isinstance(s, IRPrimitive)
        assert s.primitive_type == PrimitiveType.ICO_SPHERE
        assert s.properties["subdivisions"] == 3

    def test_line(self):
        l = line(10, (0, 0, 0), (0, 0, 5), "rod")
        assert isinstance(l, IRPrimitive)
        assert l.primitive_type == PrimitiveType.LINE
        assert l.properties["end_location"] == (0, 0, 5)


# ---------------------------------------------------------------------------
# Curve Primitives — IR level
# ---------------------------------------------------------------------------


class TestCurvePrimitives:
    def test_curve_arc(self):
        a = curve_arc(16, 2.0, 0.0, 3.14)
        assert a.primitive_type == PrimitiveType.CURVE_ARC
        assert a.properties["sweep_angle"] == 3.14

    def test_curve_circle(self):
        c = curve_circle(32, 1.5)
        assert c.primitive_type == PrimitiveType.CURVE_CIRCLE
        assert c.properties["radius"] == 1.5

    def test_curve_line(self):
        l = curve_line((0, 0, 0), (1, 1, 1))
        assert l.primitive_type == PrimitiveType.CURVE_LINE

    def test_curve_quadrilateral(self):
        q = curve_quadrilateral(2.0, 3.0)
        assert q.primitive_type == PrimitiveType.CURVE_QUADRILATERAL
        assert q.properties["width"] == 2.0

    def test_curve_star(self):
        s = curve_star(8, 0.5, 1.0)
        assert s.primitive_type == PrimitiveType.CURVE_STAR
        assert s.properties["points"] == 8

    def test_curve_spiral(self):
        sp = curve_spiral(128, 2.0, 0.5, 1.5, 2.0)
        assert sp.primitive_type == PrimitiveType.CURVE_SPIRAL
        assert sp.properties["rotations"] == 2.0


# ---------------------------------------------------------------------------
# Mesh Ops — IR level
# ---------------------------------------------------------------------------


class TestMeshOps:
    def test_extrude(self):
        node = cube(1, 1, 1, "c") | extrude(0.5)
        assert isinstance(node, IRGeometryOp)
        assert "Extrude" in node.op_type
        assert node.properties["offset_scale"] == 0.5

    def test_subdivide(self):
        node = cube(1, 1, 1, "c") | subdivide(2)
        assert isinstance(node, IRGeometryOp)
        assert node.properties["level"] == 2

    def test_subdivide_surface(self):
        node = cube(1, 1, 1, "c") | subdivide_surface(3)
        assert isinstance(node, IRGeometryOp)
        assert node.properties["level"] == 3

    def test_set_shade_smooth(self):
        node = cube(1, 1, 1, "c") | set_shade_smooth(True)
        assert isinstance(node, IRGeometryOp)
        assert node.properties["shade_smooth"] is True

    def test_merge_by_distance(self):
        node = cube(1, 1, 1, "c") | merge_by_distance(0.01)
        assert isinstance(node, IRGeometryOp)
        assert node.properties["distance"] == 0.01


# ---------------------------------------------------------------------------
# Instance Ops — IR level
# ---------------------------------------------------------------------------


class TestInstanceOps:
    def test_realize_instances(self):
        node = cube(1, 1, 1, "c") | realize_instances()
        assert isinstance(node, IRGeometryOp)
        assert "RealizeInstances" in node.op_type

    def test_rotate_instances(self):
        node = cube(1, 1, 1, "c") | rotate_instances(0, 0, 1.57)
        assert isinstance(node, IRGeometryOp)
        assert node.properties["rotation"] == (0, 0, 1.57)

    def test_scale_instances(self):
        node = cube(1, 1, 1, "c") | scale_instances(2, 2, 2)
        assert isinstance(node, IRGeometryOp)
        assert node.properties["scale"] == (2, 2, 2)

    def test_translate_instances(self):
        node = cube(1, 1, 1, "c") | translate_instances(1, 2, 3)
        assert isinstance(node, IRGeometryOp)
        assert node.properties["translation"] == (1, 2, 3)


# ---------------------------------------------------------------------------
# Compiler — new mesh primitives
# ---------------------------------------------------------------------------


class TestNewMeshCompiler:
    def test_circle(self):
        src = _compile_model("tc", lambda: output(circle(32, 1.0)))
        _assert_valid_python(src)
        assert "GeometryNodeMeshCircle" in src

    def test_grid(self):
        src = _compile_model("tg", lambda: output(grid(2, 2, 10, 10)))
        _assert_valid_python(src)
        assert "GeometryNodeMeshGrid" in src

    def test_ico_sphere(self):
        src = _compile_model("ti", lambda: output(ico_sphere(1.0, 2)))
        _assert_valid_python(src)
        assert "GeometryNodeMeshIcoSphere" in src

    def test_line(self):
        src = _compile_model("tl", lambda: output(line(10)))
        _assert_valid_python(src)
        assert "GeometryNodeMeshLine" in src


# ---------------------------------------------------------------------------
# Compiler — curves
# ---------------------------------------------------------------------------


class TestCurveCompiler:
    def test_curve_arc(self):
        src = _compile_model("ca", lambda: output(curve_arc(16, 2.0)))
        _assert_valid_python(src)
        assert "GeometryNodeCurveArc" in src

    def test_curve_circle(self):
        src = _compile_model("cc", lambda: output(curve_circle(32, 1.5)))
        _assert_valid_python(src)
        assert "GeometryNodeCurvePrimitiveCircle" in src

    def test_curve_line(self):
        src = _compile_model("cl", lambda: output(curve_line()))
        _assert_valid_python(src)
        assert "GeometryNodeCurvePrimitiveLine" in src

    def test_curve_star(self):
        src = _compile_model("cs", lambda: output(curve_star(8, 0.5, 1.0)))
        _assert_valid_python(src)
        assert "GeometryNodeCurveStar" in src

    def test_curve_spiral(self):
        src = _compile_model("csp", lambda: output(curve_spiral()))
        _assert_valid_python(src)
        assert "GeometryNodeCurveSpiral" in src


# ---------------------------------------------------------------------------
# Compiler — mesh ops
# ---------------------------------------------------------------------------


class TestMeshOpsCompiler:
    def test_extrude(self):
        src = _compile_model("ex", lambda: output(cube(1, 1, 1, "c") | extrude(0.5)))
        _assert_valid_python(src)
        assert "GeometryNodeExtrudeMesh" in src

    def test_subdivide(self):
        src = _compile_model("sd", lambda: output(cube(1, 1, 1, "c") | subdivide(2)))
        _assert_valid_python(src)
        assert "GeometryNodeSubdivideMesh" in src

    def test_shade_smooth(self):
        src = _compile_model("ss", lambda: output(ico_sphere(1.0, 2) | set_shade_smooth(True)))
        _assert_valid_python(src)
        assert "GeometryNodeSetShadeSmooth" in src

    def test_merge_by_distance(self):
        src = _compile_model("md", lambda: output(cube(1, 1, 1, "c") | merge_by_distance(0.01)))
        _assert_valid_python(src)
        assert "GeometryNodeMergeByDistance" in src


# ---------------------------------------------------------------------------
# Compiler — instance ops
# ---------------------------------------------------------------------------


class TestInstanceOpsCompiler:
    def test_realize(self):
        src = _compile_model("ri", lambda: output(cube(1, 1, 1, "c") | realize_instances()))
        _assert_valid_python(src)
        assert "GeometryNodeRealizeInstances" in src

    def test_rotate(self):
        src = _compile_model("ro", lambda: output(cube(1, 1, 1, "c") | rotate_instances(0, 0, 1.57)))
        _assert_valid_python(src)
        assert "GeometryNodeRotateInstances" in src

    def test_scale(self):
        src = _compile_model("sc", lambda: output(cube(1, 1, 1, "c") | scale_instances(2, 2, 2)))
        _assert_valid_python(src)
        assert "GeometryNodeScaleInstances" in src

    def test_translate(self):
        src = _compile_model("tr", lambda: output(cube(1, 1, 1, "c") | translate_instances(1, 2, 3)))
        _assert_valid_python(src)
        assert "GeometryNodeTranslateInstances" in src


# ---------------------------------------------------------------------------
# Composition figures — test composability
# ---------------------------------------------------------------------------


class TestFigures:
    def test_smooth_ico_sphere(self):
        """Ico sphere with shade smooth."""
        src = _compile_model("smooth", lambda: output(
            ico_sphere(1.0, 3) | set_shade_smooth(True)
        ))
        _assert_valid_python(src)
        assert "GeometryNodeMeshIcoSphere" in src
        assert "GeometryNodeSetShadeSmooth" in src

    def test_extruded_grid(self):
        """Grid with extrusion."""
        src = _compile_model("extgrid", lambda: output(
            grid(2, 2, 10, 10) | extrude(0.3)
        ))
        _assert_valid_python(src)
        assert "GeometryNodeMeshGrid" in src
        assert "GeometryNodeExtrudeMesh" in src

    def test_star_pattern(self):
        """Star curve compiled."""
        src = _compile_model("star", lambda: output(
            curve_star(12, 0.3, 1.5)
        ))
        _assert_valid_python(src)
        assert "GeometryNodeCurveStar" in src

    def test_spiral_tower(self):
        """Spiral with transform."""
        src = _compile_model("tower", lambda: output(
            curve_spiral(64, 3.0, 0.5, 2.0, 5.0) | translate(0, 0, 1)
        ))
        _assert_valid_python(src)
        assert "GeometryNodeCurveSpiral" in src
        assert "GeometryNodeTransform" in src

    def test_subdivided_cube(self):
        """Cube with subdivision surface and shade smooth."""
        src = _compile_model("subdcube", lambda: output(
            cube(1, 1, 1, "c") | subdivide_surface(2) | set_shade_smooth(True)
        ))
        _assert_valid_python(src)
        assert "GeometryNodeSubdivisionSurface" in src
        assert "GeometryNodeSetShadeSmooth" in src

    def test_circle_with_transform(self):
        """Circle mesh with rotation."""
        src = _compile_model("circrot", lambda: output(
            circle(32, 1.0) | rotate(90, 0, 0)
        ))
        _assert_valid_python(src)
        assert "GeometryNodeMeshCircle" in src
        assert "GeometryNodeTransform" in src


# ---------------------------------------------------------------------------
# Curve Ops — IR level
# ---------------------------------------------------------------------------


class TestCurveOps:
    def test_fill_curve(self):
        node = curve_circle() | fill_curve()
        assert isinstance(node, IRGeometryOp)
        assert node.op_type == "GeometryNodeFillCurve"
        assert node.properties["group_id"] == 0

    def test_fillet_curve(self):
        node = curve_quadrilateral() | fillet_curve(count=3, radius=0.5, limit_radius=True)
        assert isinstance(node, IRGeometryOp)
        assert node.op_type == "GeometryNodeFilletCurve"
        assert node.properties["count"] == 3
        assert node.properties["radius"] == 0.5
        assert node.properties["limit_radius"] is True

    def test_resample_curve(self):
        node = curve_circle() | resample_curve(20)
        assert isinstance(node, IRGeometryOp)
        assert node.op_type == "GeometryNodeResampleCurve"
        assert node.properties["count"] == 20

    def test_reverse_curve(self):
        node = curve_line() | reverse_curve()
        assert isinstance(node, IRGeometryOp)
        assert node.op_type == "GeometryNodeReverseCurve"

    def test_subdivide_curve(self):
        node = curve_circle() | subdivide_curve(3)
        assert isinstance(node, IRGeometryOp)
        assert node.op_type == "GeometryNodeSubdivideCurve"
        assert node.properties["cuts"] == 3

    def test_trim_curve(self):
        node = curve_circle() | trim_curve(0.1, 0.9)
        assert isinstance(node, IRGeometryOp)
        assert node.op_type == "GeometryNodeTrimCurve"
        assert node.properties["start"] == 0.1
        assert node.properties["end"] == 0.9

    def test_curve_to_points(self):
        node = curve_circle() | curve_to_points(16)
        assert isinstance(node, IRGeometryOp)
        assert node.op_type == "GeometryNodeCurveToPoints"
        assert node.properties["count"] == 16

    def test_deform_curves_on_surface(self):
        node = curve_circle() | deform_curves_on_surface()
        assert isinstance(node, IRGeometryOp)
        assert node.op_type == "GeometryNodeDeformCurvesOnSurface"

    def test_sample_curve(self):
        node = curve_circle() | sample_curve(factor=0.5)
        assert isinstance(node, IRGeometryOp)
        assert node.op_type == "GeometryNodeSampleCurve"
        assert node.properties["factor"] == 0.5

    def test_pipe_chain(self):
        """Curve operations compose via pipe."""
        node = curve_circle() | resample_curve(20) | fillet_curve(radius=0.1) | reverse_curve()
        assert isinstance(node, IRGeometryOp)
        assert node.op_type == "GeometryNodeReverseCurve"
        assert node.child.op_type == "GeometryNodeFilletCurve"
        assert node.child.child.op_type == "GeometryNodeResampleCurve"


# ---------------------------------------------------------------------------
# Compiler — curve ops
# ---------------------------------------------------------------------------


class TestCurveOpsCompiler:
    def test_fill_curve(self):
        src = _compile_model("fc", lambda: output(curve_circle() | fill_curve()))
        _assert_valid_python(src)
        assert "GeometryNodeFillCurve" in src

    def test_fillet_curve(self):
        src = _compile_model("fl", lambda: output(curve_quadrilateral() | fillet_curve(radius=0.5)))
        _assert_valid_python(src)
        assert "GeometryNodeFilletCurve" in src

    def test_resample_curve(self):
        src = _compile_model("rs", lambda: output(curve_circle() | resample_curve(20)))
        _assert_valid_python(src)
        assert "GeometryNodeResampleCurve" in src

    def test_reverse_curve(self):
        src = _compile_model("rv", lambda: output(curve_line() | reverse_curve()))
        _assert_valid_python(src)
        assert "GeometryNodeReverseCurve" in src

    def test_subdivide_curve(self):
        src = _compile_model("sc", lambda: output(curve_circle() | subdivide_curve(3)))
        _assert_valid_python(src)
        assert "GeometryNodeSubdivideCurve" in src

    def test_trim_curve(self):
        src = _compile_model("tc", lambda: output(curve_circle() | trim_curve(0.1, 0.9)))
        _assert_valid_python(src)
        assert "GeometryNodeTrimCurve" in src

    def test_curve_to_points(self):
        src = _compile_model("cp", lambda: output(curve_circle() | curve_to_points(16)))
        _assert_valid_python(src)
        assert "GeometryNodeCurveToPoints" in src

    def test_deform_curves_on_surface(self):
        src = _compile_model("df", lambda: output(curve_circle() | deform_curves_on_surface()))
        _assert_valid_python(src)
        assert "GeometryNodeDeformCurvesOnSurface" in src

    def test_sample_curve(self):
        src = _compile_model("sm", lambda: output(curve_circle() | sample_curve(factor=0.5)))
        _assert_valid_python(src)
        assert "GeometryNodeSampleCurve" in src

    def test_filleted_rectangle(self):
        """Rectangle with filleted corners compiled."""
        src = _compile_model("filrect", lambda: output(
            curve_quadrilateral(4.0, 2.0) | fillet_curve(count=4, radius=0.3)
        ))
        _assert_valid_python(src)
        assert "GeometryNodeCurvePrimitiveQuadrilateral" in src
        assert "GeometryNodeFilletCurve" in src

    def test_trimmed_and_filled(self):
        """Trim a circle then fill it to mesh."""
        src = _compile_model("trimfill", lambda: output(
            curve_circle() | trim_curve(0.0, 0.75) | fill_curve()
        ))
        _assert_valid_python(src)
        assert "GeometryNodeTrimCurve" in src
        assert "GeometryNodeFillCurve" in src


# ---------------------------------------------------------------------------
# Curve Attribute Setters — IR level
# ---------------------------------------------------------------------------


class TestCurveAttributeOps:
    def test_set_curve_normal(self):
        node = curve_circle() | set_curve_normal((1.0, 0.0, 0.0))
        assert isinstance(node, IRGeometryOp)
        assert node.op_type == "GeometryNodeSetCurveNormal"
        assert node.properties["normal"] == (1.0, 0.0, 0.0)

    def test_set_curve_radius(self):
        node = curve_circle() | set_curve_radius(0.1)
        assert isinstance(node, IRGeometryOp)
        assert node.op_type == "GeometryNodeSetCurveRadius"
        assert node.properties["radius"] == 0.1

    def test_set_curve_tilt(self):
        node = curve_spiral() | set_curve_tilt(0.5)
        assert isinstance(node, IRGeometryOp)
        assert node.op_type == "GeometryNodeSetCurveTilt"
        assert node.properties["tilt"] == 0.5

    def test_set_handle_positions(self):
        node = curve_line() | set_handle_positions(position=(1, 0, 0), offset=(0, 1, 0))
        assert isinstance(node, IRGeometryOp)
        assert node.op_type == "GeometryNodeSetCurveHandlePositions"
        assert node.properties["position"] == (1, 0, 0)
        assert node.properties["offset"] == (0, 1, 0)

    def test_set_handle_type(self):
        node = curve_line() | set_handle_type("VECTOR")
        assert isinstance(node, IRGeometryOp)
        assert node.op_type == "GeometryNodeCurveSetHandles"
        assert node.properties["handle_type"] == "VECTOR"

    def test_set_spline_cyclic(self):
        node = curve_line() | set_spline_cyclic(True)
        assert isinstance(node, IRGeometryOp)
        assert node.op_type == "GeometryNodeSetSplineCyclic"
        assert node.properties["cyclic"] is True

    def test_set_spline_resolution(self):
        node = curve_circle() | set_spline_resolution(24)
        assert isinstance(node, IRGeometryOp)
        assert node.op_type == "GeometryNodeSetSplineResolution"
        assert node.properties["resolution"] == 24

    def test_set_spline_type(self):
        node = curve_line() | set_spline_type("BEZIER")
        assert isinstance(node, IRGeometryOp)
        assert node.op_type == "GeometryNodeCurveSplineType"
        assert node.properties["spline_type"] == "BEZIER"

    def test_pipe_chain_attrs(self):
        """Attribute setters compose via pipe."""
        node = (
            curve_circle()
            | set_curve_radius(0.05)
            | set_spline_cyclic(True)
            | set_spline_resolution(24)
        )
        assert node.op_type == "GeometryNodeSetSplineResolution"
        assert node.child.op_type == "GeometryNodeSetSplineCyclic"
        assert node.child.child.op_type == "GeometryNodeSetCurveRadius"


# ---------------------------------------------------------------------------
# Compiler — curve attribute setters
# ---------------------------------------------------------------------------


class TestCurveAttributeOpsCompiler:
    def test_set_curve_normal(self):
        src = _compile_model("scn", lambda: output(curve_circle() | set_curve_normal()))
        _assert_valid_python(src)
        assert "GeometryNodeSetCurveNormal" in src

    def test_set_curve_radius(self):
        src = _compile_model("scr", lambda: output(curve_circle() | set_curve_radius(0.1)))
        _assert_valid_python(src)
        assert "GeometryNodeSetCurveRadius" in src

    def test_set_curve_tilt(self):
        src = _compile_model("sct", lambda: output(curve_spiral() | set_curve_tilt(0.5)))
        _assert_valid_python(src)
        assert "GeometryNodeSetCurveTilt" in src

    def test_set_handle_positions(self):
        src = _compile_model("shp", lambda: output(
            curve_line() | set_handle_positions(position=(1, 0, 0))
        ))
        _assert_valid_python(src)
        assert "GeometryNodeSetCurveHandlePositions" in src

    def test_set_handle_type(self):
        src = _compile_model("sht", lambda: output(curve_line() | set_handle_type("VECTOR")))
        _assert_valid_python(src)
        assert "GeometryNodeCurveSetHandles" in src
        assert "VECTOR" in src

    def test_set_spline_cyclic(self):
        src = _compile_model("ssc", lambda: output(curve_line() | set_spline_cyclic(True)))
        _assert_valid_python(src)
        assert "GeometryNodeSetSplineCyclic" in src

    def test_set_spline_resolution(self):
        src = _compile_model("ssr", lambda: output(curve_circle() | set_spline_resolution(24)))
        _assert_valid_python(src)
        assert "GeometryNodeSetSplineResolution" in src

    def test_set_spline_type(self):
        src = _compile_model("sst", lambda: output(curve_line() | set_spline_type("BEZIER")))
        _assert_valid_python(src)
        assert "GeometryNodeCurveSplineType" in src
        assert "BEZIER" in src

    def test_cyclic_filled_circle(self):
        """Set cyclic then fill — practical pattern."""
        src = _compile_model("cfill", lambda: output(
            curve_arc(sweep_angle=270.0)
            | set_spline_cyclic(True)
            | fill_curve()
        ))
        _assert_valid_python(src)
        assert "GeometryNodeSetSplineCyclic" in src
        assert "GeometryNodeFillCurve" in src


# ---------------------------------------------------------------------------
# New mesh ops (remaining mesh nodes) — IR level
# ---------------------------------------------------------------------------


class TestRemainingMeshOpsIR:
    def test_dual_mesh(self):
        node = cube(1, 1, 1, "c") | dual_mesh(keep_boundaries=True)
        assert isinstance(node, IRGeometryOp)
        assert node.op_type == "GeometryNodeDualMesh"
        assert node.properties["keep_boundaries"] is True

    def test_mesh_to_curve(self):
        node = cube(1, 1, 1, "c") | mesh_to_curve()
        assert isinstance(node, IRGeometryOp)
        assert node.op_type == "GeometryNodeMeshToCurve"

    def test_mesh_to_points(self):
        node = cube(1, 1, 1, "c") | mesh_to_points(radius=0.1, mode="FACES")
        assert isinstance(node, IRGeometryOp)
        assert node.properties["radius"] == 0.1
        assert node.properties["mode"] == "FACES"

    def test_mesh_to_volume(self):
        node = cube(1, 1, 1, "c") | mesh_to_volume(density=2.0, voxel_size=0.5)
        assert isinstance(node, IRGeometryOp)
        assert node.op_type == "GeometryNodeMeshToVolume"
        assert node.properties["density"] == 2.0

    def test_volume_to_mesh(self):
        node = cube(1, 1, 1, "c") | volume_to_mesh(threshold=0.2)
        assert isinstance(node, IRGeometryOp)
        assert node.op_type == "GeometryNodeVolumeToMesh"
        assert node.properties["threshold"] == 0.2

    def test_set_mesh_normal(self):
        node = cube(1, 1, 1, "c") | set_mesh_normal(remove_custom=False)
        assert isinstance(node, IRGeometryOp)
        assert node.op_type == "GeometryNodeSetMeshNormal"
        assert node.properties["remove_custom"] is False

    def test_curve_to_mesh_no_profile(self):
        node = curve_circle(32, 1.0) | curve_to_mesh()
        assert isinstance(node, IRGeometryOp)
        assert node.op_type == "GeometryNodeCurveToMesh"
        assert len(node.extra_children) == 0

    def test_curve_to_mesh_with_profile(self):
        profile = curve_circle(8, 0.1)
        node = curve_circle(32, 1.0) | curve_to_mesh(profile=profile)
        assert isinstance(node, IRGeometryOp)
        assert "Profile Curve" in node.extra_children


# ---------------------------------------------------------------------------
# New mesh ops — Compiler
# ---------------------------------------------------------------------------


class TestRemainingMeshOpsCompiler:
    def test_dual_mesh(self):
        src = _compile_model("dm", lambda: output(ico_sphere(1.0, 2) | dual_mesh()))
        _assert_valid_python(src)
        assert "GeometryNodeDualMesh" in src
        assert '"Mesh"' in src  # input socket

    def test_mesh_to_curve(self):
        src = _compile_model("mtc", lambda: output(cube(1, 1, 1, "c") | mesh_to_curve()))
        _assert_valid_python(src)
        assert "GeometryNodeMeshToCurve" in src

    def test_mesh_to_points(self):
        src = _compile_model("mtp", lambda: output(cube(1, 1, 1, "c") | mesh_to_points(0.05)))
        _assert_valid_python(src)
        assert "GeometryNodeMeshToPoints" in src

    def test_mesh_to_volume(self):
        src = _compile_model("mtv", lambda: output(cube(1, 1, 1, "c") | mesh_to_volume()))
        _assert_valid_python(src)
        assert "GeometryNodeMeshToVolume" in src

    def test_volume_to_mesh(self):
        src = _compile_model("vtm", lambda: output(cube(1, 1, 1, "c") | volume_to_mesh()))
        _assert_valid_python(src)
        assert "GeometryNodeVolumeToMesh" in src

    def test_set_mesh_normal(self):
        src = _compile_model("smn", lambda: output(cube(1, 1, 1, "c") | set_mesh_normal()))
        _assert_valid_python(src)
        assert "GeometryNodeSetMeshNormal" in src

    def test_curve_to_mesh_no_profile(self):
        src = _compile_model("ctm", lambda: output(curve_circle(32, 1.0) | curve_to_mesh()))
        _assert_valid_python(src)
        assert "GeometryNodeCurveToMesh" in src

    def test_curve_to_mesh_with_profile(self):
        profile = curve_circle(8, 0.1)
        src = _compile_model("ctmp", lambda: output(
            curve_circle(32, 1.0) | curve_to_mesh(profile=profile, fill_caps=True)
        ))
        _assert_valid_python(src)
        assert "GeometryNodeCurveToMesh" in src
        assert "GeometryNodeCurvePrimitiveCircle" in src
        assert "Profile Curve" in src

    def test_correct_input_sockets(self):
        """Verify the input socket names are correct for new ops."""
        src = _compile_model("socks", lambda: output(cube(1, 1, 1, "c") | dual_mesh()))
        _assert_valid_python(src)
        # dual_mesh input should be "Mesh", not "Geometry"
        assert '.inputs["Mesh"]' in src


# ---------------------------------------------------------------------------
# Composition figures with new ops
# ---------------------------------------------------------------------------


class TestNewFigures:
    def test_dual_smooth_sphere(self):
        """Ico sphere → dual mesh → shade smooth."""
        src = _compile_model("dualsmooth", lambda: output(
            ico_sphere(1.0, 2) | dual_mesh() | set_shade_smooth(True)
        ))
        _assert_valid_python(src)
        assert "GeometryNodeDualMesh" in src
        assert "GeometryNodeSetShadeSmooth" in src

    def test_torus_via_curve_to_mesh(self):
        """Curve circle + small profile circle → torus."""
        profile = curve_circle(8, 0.2)
        src = _compile_model("torus", lambda: output(
            curve_circle(32, 1.0) | curve_to_mesh(profile=profile, fill_caps=True)
        ))
        _assert_valid_python(src)
        assert "GeometryNodeCurveToMesh" in src

    def test_mesh_to_points_chain(self):
        """Cube → mesh to points → translate."""
        src = _compile_model("ptschain", lambda: output(
            cube(1, 1, 1, "c") | mesh_to_points(0.02) | translate(0, 0, 1)
        ))
        _assert_valid_python(src)
        assert "GeometryNodeMeshToPoints" in src
        assert "GeometryNodeTransform" in src

    def test_curve_pipe(self):
        """Curve line → curve to mesh (no profile) → translate."""
        src = _compile_model("pipe", lambda: output(
            curve_line() | curve_to_mesh() | translate(0, 0, 2)
        ))
        _assert_valid_python(src)
        assert "GeometryNodeCurvePrimitiveLine" in src
        assert "GeometryNodeCurveToMesh" in src


# ---------------------------------------------------------------------------
# Batch 3 — New curve primitives (IR level)
# ---------------------------------------------------------------------------


class TestBatch3CurvePrimitivesIR:
    def test_bezier_segment(self):
        node = bezier_segment()
        assert isinstance(node, IRPrimitive)
        assert node.primitive_type == PrimitiveType.CURVE_BEZIER_SEGMENT
        assert node.properties["resolution"] == 16
        assert node.properties["start"] == (-1.0, 0.0, 0.0)
        assert node.properties["start_handle"] == (-0.5, 0.5, 0.0)
        assert node.properties["end_handle"] == (0.0, 0.0, 0.0)
        assert node.properties["end"] == (1.0, 0.0, 0.0)

    def test_bezier_segment_custom(self):
        node = bezier_segment(
            resolution=32,
            start=(0, 0, 0),
            start_handle=(0.5, 1, 0),
            end_handle=(1.5, 1, 0),
            end=(2, 0, 0),
        )
        assert node.properties["resolution"] == 32
        assert node.properties["start"] == (0, 0, 0)

    def test_quadratic_bezier(self):
        node = quadratic_bezier()
        assert isinstance(node, IRPrimitive)
        assert node.primitive_type == PrimitiveType.CURVE_QUADRATIC_BEZIER
        assert node.properties["resolution"] == 16
        assert node.properties["start"] == (-1.0, 0.0, 0.0)
        assert node.properties["middle"] == (0.0, 2.0, 0.0)
        assert node.properties["end"] == (1.0, 0.0, 0.0)

    def test_quadratic_bezier_custom(self):
        node = quadratic_bezier(resolution=8, middle=(0, 5, 0))
        assert node.properties["resolution"] == 8
        assert node.properties["middle"] == (0, 5, 0)


# ---------------------------------------------------------------------------
# Batch 3 — New curve primitives (compiler)
# ---------------------------------------------------------------------------


class TestBatch3CurvePrimitivesCompiler:
    def test_bezier_segment_compiles(self):
        src = _compile_model("bseg", lambda: output(bezier_segment()))
        _assert_valid_python(src)
        assert "GeometryNodeCurvePrimitiveBezierSegment" in src
        assert 'inputs["Resolution"]' in src
        assert 'inputs["Start"]' in src
        assert 'inputs["Start Handle"]' in src
        assert 'inputs["End Handle"]' in src
        assert 'inputs["End"]' in src

    def test_quadratic_bezier_compiles(self):
        src = _compile_model("qbez", lambda: output(quadratic_bezier()))
        _assert_valid_python(src)
        assert "GeometryNodeCurveQuadraticBezier" in src
        assert 'inputs["Resolution"]' in src
        assert 'inputs["Start"]' in src
        assert 'inputs["Middle"]' in src
        assert 'inputs["End"]' in src


# ---------------------------------------------------------------------------
# Batch 3 — New curve operations (IR level)
# ---------------------------------------------------------------------------


class TestBatch3CurveOpsIR:
    def test_edge_paths_to_curves(self):
        node = cube(1, 1, 1) | edge_paths_to_curves()
        assert isinstance(node, IRGeometryOp)
        assert node.op_type == "GeometryNodeEdgePathsToCurves"
        assert node.properties["start_vertices"] is True
        assert node.properties["next_vertex_index"] == -1

    def test_interpolate_curves(self):
        pts = cube(1, 1, 1)
        node = curve_circle() | interpolate_curves(points=pts, max_neighbors=6)
        assert isinstance(node, IRGeometryOp)
        assert node.op_type == "GeometryNodeInterpolateCurves"
        assert node.properties["max_neighbors"] == 6
        assert "Points" in node.extra_children

    def test_points_to_curves(self):
        node = cube(1, 1, 1) | points_to_curves(curve_group_id=2, weight=0.5)
        assert isinstance(node, IRGeometryOp)
        assert node.op_type == "GeometryNodePointsToCurves"
        assert node.properties["curve_group_id"] == 2
        assert node.properties["weight"] == 0.5

    def test_curves_to_grease_pencil(self):
        node = curve_circle() | curves_to_grease_pencil()
        assert isinstance(node, IRGeometryOp)
        assert node.op_type == "GeometryNodeCurvesToGreasePencil"
        assert node.properties["instances_as_layers"] is True

    def test_grease_pencil_to_curves(self):
        node = curve_circle() | grease_pencil_to_curves()
        assert isinstance(node, IRGeometryOp)
        assert node.op_type == "GeometryNodeGreasePencilToCurves"
        assert node.properties["layers_as_instances"] is True

    def test_string_to_curves(self):
        node = cube(1, 1, 1) | string_to_curves(string="Hello", size=2.0)
        assert isinstance(node, IRGeometryOp)
        assert node.op_type == "GeometryNodeStringToCurves"
        assert node.properties["string"] == "Hello"
        assert node.properties["size"] == 2.0
        assert node.properties["character_spacing"] == 1.0


# ---------------------------------------------------------------------------
# Batch 3 — New curve operations (compiler)
# ---------------------------------------------------------------------------


class TestBatch3CurveOpsCompiler:
    def test_edge_paths_to_curves_compiles(self):
        src = _compile_model("edgepaths", lambda: output(
            cube(1, 1, 1) | edge_paths_to_curves()
        ))
        _assert_valid_python(src)
        assert "GeometryNodeEdgePathsToCurves" in src
        assert 'inputs["Mesh"]' in src

    def test_interpolate_curves_compiles(self):
        pts = cube(1, 1, 1)
        src = _compile_model("interp", lambda: output(
            curve_circle() | interpolate_curves(points=pts, max_neighbors=8)
        ))
        _assert_valid_python(src)
        assert "GeometryNodeInterpolateCurves" in src
        assert 'inputs["Points"]' in src
        assert 'inputs["Max Neighbors"]' in src

    def test_points_to_curves_compiles(self):
        src = _compile_model("ptscurv", lambda: output(
            cube(1, 1, 1) | points_to_curves()
        ))
        _assert_valid_python(src)
        assert "GeometryNodePointsToCurves" in src
        assert 'inputs["Points"]' in src

    def test_curves_to_grease_pencil_compiles(self):
        src = _compile_model("c2gp", lambda: output(
            curve_circle() | curves_to_grease_pencil()
        ))
        _assert_valid_python(src)
        assert "GeometryNodeCurvesToGreasePencil" in src

    def test_grease_pencil_to_curves_compiles(self):
        src = _compile_model("gp2c", lambda: output(
            curve_circle() | grease_pencil_to_curves()
        ))
        _assert_valid_python(src)
        assert "GeometryNodeGreasePencilToCurves" in src

    def test_string_to_curves_compiles(self):
        src = _compile_model("str2c", lambda: output(
            cube(1, 1, 1) | string_to_curves(string="Test", size=1.5)
        ))
        _assert_valid_python(src)
        assert "GeometryNodeStringToCurves" in src
        assert "'Test'" in src or '"Test"' in src
        assert 'inputs["Size"]' in src


# ---------------------------------------------------------------------------
# Batch 3 — Composition tests
# ---------------------------------------------------------------------------


class TestBatch3Figures:
    def test_bezier_to_mesh(self):
        """Bezier segment → curve to mesh → translate."""
        src = _compile_model("bezmesh", lambda: output(
            bezier_segment() | curve_to_mesh() | translate(1, 0, 0)
        ))
        _assert_valid_python(src)
        assert "GeometryNodeCurvePrimitiveBezierSegment" in src
        assert "GeometryNodeCurveToMesh" in src

    def test_quadratic_bezier_fillet(self):
        """Quadratic bezier → fillet → resample."""
        src = _compile_model("qbezfil", lambda: output(
            quadratic_bezier(resolution=12) | fillet_curve(count=2) | resample_curve(20)
        ))
        _assert_valid_python(src)
        assert "GeometryNodeCurveQuadraticBezier" in src
        assert "GeometryNodeFilletCurve" in src

    def test_interpolate_pipeline(self):
        """Interpolate curves with guide curves and target points."""
        pts = cube(1, 1, 1)
        src = _compile_model("interpipe", lambda: output(
            curve_spiral() | interpolate_curves(points=pts)
        ))
        _assert_valid_python(src)
        assert "GeometryNodeInterpolateCurves" in src
        assert "GeometryNodeCurveSpiral" in src


# ---------------------------------------------------------------------------
# Batch 4 — Instance operations (IR level)
# ---------------------------------------------------------------------------


class TestBatch4InstanceOpsIR:
    def test_geometry_to_instance(self):
        node = cube(1, 1, 1) | geometry_to_instance()
        assert isinstance(node, IRGeometryOp)
        assert node.op_type == "GeometryNodeGeometryToInstance"

    def test_instances_to_points(self):
        node = cube(1, 1, 1) | instances_to_points(radius=0.1)
        assert isinstance(node, IRGeometryOp)
        assert node.op_type == "GeometryNodeInstancesToPoints"
        assert node.properties["radius"] == 0.1
        assert node.properties["position"] == (0.0, 0.0, 0.0)

    def test_instances_to_points_defaults(self):
        node = cube(1, 1, 1) | instances_to_points()
        assert node.properties["radius"] == 0.05

    def test_split_to_instances(self):
        node = cube(1, 1, 1) | split_to_instances(group_id=3)
        assert isinstance(node, IRGeometryOp)
        assert node.op_type == "GeometryNodeSplitToInstances"
        assert node.properties["group_id"] == 3

    def test_split_to_instances_default(self):
        node = cube(1, 1, 1) | split_to_instances()
        assert node.properties["group_id"] == 0


# ---------------------------------------------------------------------------
# Batch 4 — Instance operations (compiler)
# ---------------------------------------------------------------------------


class TestBatch4InstanceOpsCompiler:
    def test_geometry_to_instance_compiles(self):
        src = _compile_model("g2i", lambda: output(
            cube(1, 1, 1) | geometry_to_instance()
        ))
        _assert_valid_python(src)
        assert "GeometryNodeGeometryToInstance" in src
        assert 'inputs["Geometry"]' in src

    def test_instances_to_points_compiles(self):
        src = _compile_model("i2p", lambda: output(
            cube(1, 1, 1) | instances_to_points(radius=0.1)
        ))
        _assert_valid_python(src)
        assert "GeometryNodeInstancesToPoints" in src
        assert 'inputs["Radius"]' in src

    def test_split_to_instances_compiles(self):
        src = _compile_model("spl", lambda: output(
            cube(1, 1, 1) | split_to_instances(group_id=5)
        ))
        _assert_valid_python(src)
        assert "GeometryNodeSplitToInstances" in src
        assert 'inputs["Group ID"]' in src


# ---------------------------------------------------------------------------
# Batch 4 — Composition tests
# ---------------------------------------------------------------------------


class TestBatch4Figures:
    def test_geo_to_instance_chain(self):
        """Cube → geometry to instance → translate instances."""
        src = _compile_model("g2i_chain", lambda: output(
            cube(1, 1, 1) | geometry_to_instance() | translate_instances(1, 0, 0)
        ))
        _assert_valid_python(src)
        assert "GeometryNodeGeometryToInstance" in src
        assert "GeometryNodeTranslateInstances" in src

    def test_split_and_scale(self):
        """Cube → split to instances → scale instances."""
        src = _compile_model("split_scale", lambda: output(
            cube(1, 1, 1) | split_to_instances() | scale_instances(2, 2, 2)
        ))
        _assert_valid_python(src)
        assert "GeometryNodeSplitToInstances" in src
        assert "GeometryNodeScaleInstances" in src

    def test_instances_to_points_pipeline(self):
        """Geometry to instance → instances to points."""
        src = _compile_model("i2p_pipe", lambda: output(
            cube(1, 1, 1) | geometry_to_instance() | instances_to_points(radius=0.02)
        ))
        _assert_valid_python(src)
        assert "GeometryNodeInstancesToPoints" in src
        assert "GeometryNodeGeometryToInstance" in src


# ---------------------------------------------------------------------------
# Batch 5 — Material operations (IR level)
# ---------------------------------------------------------------------------


class TestMaterialOpsIR:
    def test_set_material(self):
        node = cube(1, 1, 1) | set_material("Wood")
        assert isinstance(node, IRGeometryOp)
        assert node.op_type == "GeometryNodeSetMaterial"
        assert node.properties["material"] == "Wood"

    def test_set_material_default(self):
        node = cube(1, 1, 1) | set_material()
        assert node.properties["material"] == ""

    def test_replace_material(self):
        node = cube(1, 1, 1) | replace_material(old="Metal", new="Glass")
        assert isinstance(node, IRGeometryOp)
        assert node.op_type == "GeometryNodeReplaceMaterial"
        assert node.properties["material_old"] == "Metal"
        assert node.properties["material_new"] == "Glass"

    def test_set_material_index(self):
        node = cube(1, 1, 1) | set_material_index(2)
        assert isinstance(node, IRGeometryOp)
        assert node.op_type == "GeometryNodeSetMaterialIndex"
        assert node.properties["material_index"] == 2

    def test_set_material_index_default(self):
        node = cube(1, 1, 1) | set_material_index()
        assert node.properties["material_index"] == 0


# ---------------------------------------------------------------------------
# Batch 5 — Material operations (compiler)
# ---------------------------------------------------------------------------


class TestMaterialOpsCompiler:
    def test_set_material_compiles(self):
        src = _compile_model("setmat", lambda: output(
            cube(1, 1, 1) | set_material("Wood")
        ))
        _assert_valid_python(src)
        assert "GeometryNodeSetMaterial" in src
        assert 'bpy.data.materials.get' in src
        assert "'Wood'" in src or '"Wood"' in src

    def test_set_material_empty_compiles(self):
        """Empty material name should not emit bpy.data.materials lookup."""
        src = _compile_model("setmat_e", lambda: output(
            cube(1, 1, 1) | set_material()
        ))
        _assert_valid_python(src)
        assert "GeometryNodeSetMaterial" in src
        assert "bpy.data.materials" not in src

    def test_replace_material_compiles(self):
        src = _compile_model("repmat", lambda: output(
            cube(1, 1, 1) | replace_material(old="Metal", new="Glass")
        ))
        _assert_valid_python(src)
        assert "GeometryNodeReplaceMaterial" in src
        assert "'Metal'" in src or '"Metal"' in src
        assert "'Glass'" in src or '"Glass"' in src

    def test_set_material_index_compiles(self):
        src = _compile_model("matidx", lambda: output(
            cube(1, 1, 1) | set_material_index(3)
        ))
        _assert_valid_python(src)
        assert "GeometryNodeSetMaterialIndex" in src
        assert 'inputs["Material Index"]' in src


# ---------------------------------------------------------------------------
# Batch 5 — Material composition tests
# ---------------------------------------------------------------------------


class TestMaterialFigures:
    def test_set_material_pipeline(self):
        """Cube → set material → translate."""
        src = _compile_model("matpipe", lambda: output(
            cube(1, 1, 1) | set_material("Stone") | translate(1, 0, 0)
        ))
        _assert_valid_python(src)
        assert "GeometryNodeSetMaterial" in src
        assert "GeometryNodeTransform" in src

    def test_replace_then_set_index(self):
        """Cube → replace material → set material index."""
        src = _compile_model("matrep", lambda: output(
            cube(1, 1, 1) | replace_material("A", "B") | set_material_index(1)
        ))
        _assert_valid_python(src)
        assert "GeometryNodeReplaceMaterial" in src
        assert "GeometryNodeSetMaterialIndex" in src


# ---------------------------------------------------------------------------
# Batch 6 — Volume operations (IR level)
# ---------------------------------------------------------------------------


class TestVolumeOpsIR:
    def test_distribute_points_in_volume(self):
        node = cube(1, 1, 1) | distribute_points_in_volume(density=2.0, seed=42)
        assert isinstance(node, IRGeometryOp)
        assert node.op_type == "GeometryNodeDistributePointsInVolume"
        assert node.properties["density"] == 2.0
        assert node.properties["seed"] == 42
        assert node.properties["spacing"] == (0.3, 0.3, 0.3)
        assert node.properties["threshold"] == 0.1

    def test_distribute_points_in_volume_defaults(self):
        node = cube(1, 1, 1) | distribute_points_in_volume()
        assert node.properties["density"] == 1.0
        assert node.properties["seed"] == 0

    def test_points_to_volume(self):
        node = cube(1, 1, 1) | points_to_volume(density=0.5, radius=1.0)
        assert isinstance(node, IRGeometryOp)
        assert node.op_type == "GeometryNodePointsToVolume"
        assert node.properties["density"] == 0.5
        assert node.properties["radius"] == 1.0
        assert node.properties["voxel_size"] == 0.3

    def test_points_to_volume_defaults(self):
        node = cube(1, 1, 1) | points_to_volume()
        assert node.properties["voxel_amount"] == 64.0

    def test_volume_cube(self):
        node = volume_cube()
        assert isinstance(node, IRPrimitive)
        assert node.primitive_type == PrimitiveType.VOLUME_CUBE
        assert node.properties["density"] == 1.0
        assert node.properties["background"] == 0.0
        assert node.properties["min"] == (-1.0, -1.0, -1.0)
        assert node.properties["max"] == (1.0, 1.0, 1.0)
        assert node.properties["resolution_x"] == 32

    def test_volume_cube_custom(self):
        node = volume_cube(
            density=2.0, min=(-2, -2, -2), max=(2, 2, 2),
            resolution_x=16, resolution_y=16, resolution_z=16,
        )
        assert node.properties["density"] == 2.0
        assert node.properties["min"] == (-2, -2, -2)
        assert node.properties["resolution_x"] == 16


# ---------------------------------------------------------------------------
# Batch 6 — Volume operations (compiler)
# ---------------------------------------------------------------------------


class TestVolumeOpsCompiler:
    def test_distribute_points_in_volume_compiles(self):
        src = _compile_model("dpv", lambda: output(
            cube(1, 1, 1) | distribute_points_in_volume(seed=5)
        ))
        _assert_valid_python(src)
        assert "GeometryNodeDistributePointsInVolume" in src
        assert 'inputs["Volume"]' in src
        assert 'inputs["Seed"]' in src

    def test_points_to_volume_compiles(self):
        src = _compile_model("p2v", lambda: output(
            cube(1, 1, 1) | points_to_volume(radius=0.8)
        ))
        _assert_valid_python(src)
        assert "GeometryNodePointsToVolume" in src
        assert 'inputs["Points"]' in src
        assert 'inputs["Radius"]' in src

    def test_volume_cube_compiles(self):
        src = _compile_model("vcube", lambda: output(volume_cube()))
        _assert_valid_python(src)
        assert "GeometryNodeVolumeCube" in src
        assert 'inputs["Density"]' in src
        assert 'inputs["Background"]' in src
        assert 'inputs["Min"]' in src
        assert 'inputs["Max"]' in src
        assert 'inputs["Resolution X"]' in src


# ---------------------------------------------------------------------------
# Batch 6 — Volume composition tests
# ---------------------------------------------------------------------------


class TestVolumeFigures:
    def test_volume_to_mesh_pipeline(self):
        """Volume cube → volume to mesh → translate."""
        src = _compile_model("vol_pipe", lambda: output(
            volume_cube() | volume_to_mesh() | translate(0, 0, 1)
        ))
        _assert_valid_python(src)
        assert "GeometryNodeVolumeCube" in src
        assert "GeometryNodeVolumeToMesh" in src
        assert "GeometryNodeTransform" in src

    def test_points_to_volume_pipeline(self):
        """Cube → mesh to points → points to volume → volume to mesh."""
        src = _compile_model("p2v_pipe", lambda: output(
            cube(1, 1, 1) | mesh_to_points(0.1) | points_to_volume() | volume_to_mesh()
        ))
        _assert_valid_python(src)
        assert "GeometryNodeMeshToPoints" in src
        assert "GeometryNodePointsToVolume" in src
        assert "GeometryNodeVolumeToMesh" in src


# ── Batch 7: Other Ops ──────────────────────────────────────────────


class TestOtherOpsIR:
    """IR-level tests for 8 Other geometry operations."""

    def test_convex_hull(self):
        node = cube(1, 1, 1) | convex_hull()
        assert isinstance(node, IRGeometryOp)
        assert node.op_type == "GeometryNodeConvexHull"

    def test_delete_geometry(self):
        node = cube(1, 1, 1) | delete_geometry(mode="EDGE_FACE", domain="FACE")
        assert isinstance(node, IRGeometryOp)
        assert node.op_type == "GeometryNodeDeleteGeometry"
        assert node.properties["mode"] == "EDGE_FACE"
        assert node.properties["domain"] == "FACE"

    def test_delete_geometry_defaults(self):
        node = cube(1, 1, 1) | delete_geometry()
        assert node.properties["mode"] == "ALL"
        assert node.properties["domain"] == "POINT"

    def test_distribute_points_on_faces(self):
        node = cube(1, 1, 1) | distribute_points_on_faces(density=5.0, seed=42)
        assert isinstance(node, IRGeometryOp)
        assert node.op_type == "GeometryNodeDistributePointsOnFaces"
        assert node.properties["density"] == 5.0
        assert node.properties["seed"] == 42

    def test_distribute_points_on_faces_defaults(self):
        node = cube(1, 1, 1) | distribute_points_on_faces()
        assert node.properties["density"] == 10.0
        assert node.properties["density_max"] == 10.0
        assert node.properties["density_factor"] == 1.0
        assert node.properties["distance_min"] == 0.0
        assert node.properties["distribute_method"] == "RANDOM"

    def test_duplicate_elements(self):
        node = cube(1, 1, 1) | duplicate_elements(amount=3, domain="FACE")
        assert isinstance(node, IRGeometryOp)
        assert node.op_type == "GeometryNodeDuplicateElements"
        assert node.properties["amount"] == 3
        assert node.properties["domain"] == "FACE"

    def test_flip_faces(self):
        node = cube(1, 1, 1) | flip_faces()
        assert isinstance(node, IRGeometryOp)
        assert node.op_type == "GeometryNodeFlipFaces"

    def test_scale_elements(self):
        node = cube(1, 1, 1) | scale_elements(scale=2.0, domain="EDGE", scale_mode="SINGLE_AXIS")
        assert isinstance(node, IRGeometryOp)
        assert node.op_type == "GeometryNodeScaleElements"
        assert node.properties["element_scale"] == 2.0
        assert node.properties["domain"] == "EDGE"
        assert node.properties["scale_mode"] == "SINGLE_AXIS"

    def test_scale_elements_defaults(self):
        node = cube(1, 1, 1) | scale_elements()
        assert node.properties["element_scale"] == 1.0
        assert node.properties["center"] == (0.0, 0.0, 0.0)
        assert node.properties["axis"] == (1.0, 0.0, 0.0)
        assert node.properties["domain"] == "FACE"
        assert node.properties["scale_mode"] == "UNIFORM"

    def test_split_edges(self):
        node = cube(1, 1, 1) | split_edges()
        assert isinstance(node, IRGeometryOp)
        assert node.op_type == "GeometryNodeSplitEdges"

    def test_triangulate(self):
        node = cube(1, 1, 1) | triangulate(quad_method="FIXED", ngon_method="CLIP")
        assert isinstance(node, IRGeometryOp)
        assert node.op_type == "GeometryNodeTriangulate"
        assert node.properties["quad_method"] == "FIXED"
        assert node.properties["ngon_method"] == "CLIP"

    def test_triangulate_defaults(self):
        node = cube(1, 1, 1) | triangulate()
        assert node.properties["quad_method"] == "BEAUTY"
        assert node.properties["ngon_method"] == "BEAUTY"


class TestOtherOpsCompiler:
    """Compiler tests for 8 Other geometry operations."""

    def test_convex_hull_compiles(self):
        src = _compile_model("ch", lambda: output(cube(1, 1, 1) | convex_hull()))
        _assert_valid_python(src)
        assert "GeometryNodeConvexHull" in src

    def test_delete_geometry_compiles(self):
        src = _compile_model("dg", lambda: output(
            cube(1, 1, 1) | delete_geometry(mode="EDGE_FACE", domain="FACE")
        ))
        _assert_valid_python(src)
        assert "GeometryNodeDeleteGeometry" in src
        assert '.mode = "EDGE_FACE"' in src
        assert '.domain = "FACE"' in src

    def test_distribute_points_on_faces_compiles(self):
        src = _compile_model("dpf", lambda: output(
            cube(1, 1, 1) | distribute_points_on_faces(density=5.0, seed=42, distribute_method="POISSON")
        ))
        _assert_valid_python(src)
        assert "GeometryNodeDistributePointsOnFaces" in src
        assert '.distribute_method = "POISSON"' in src

    def test_duplicate_elements_compiles(self):
        src = _compile_model("dup", lambda: output(
            cube(1, 1, 1) | duplicate_elements(amount=3, domain="FACE")
        ))
        _assert_valid_python(src)
        assert "GeometryNodeDuplicateElements" in src
        assert '.domain = "FACE"' in src

    def test_flip_faces_compiles(self):
        src = _compile_model("ff", lambda: output(cube(1, 1, 1) | flip_faces()))
        _assert_valid_python(src)
        assert "GeometryNodeFlipFaces" in src

    def test_scale_elements_compiles(self):
        src = _compile_model("se", lambda: output(
            cube(1, 1, 1) | scale_elements(scale=2.0, domain="EDGE", scale_mode="SINGLE_AXIS")
        ))
        _assert_valid_python(src)
        assert "GeometryNodeScaleElements" in src
        assert '.domain = "EDGE"' in src
        assert '.scale_mode = "SINGLE_AXIS"' in src

    def test_split_edges_compiles(self):
        src = _compile_model("sp", lambda: output(cube(1, 1, 1) | split_edges()))
        _assert_valid_python(src)
        assert "GeometryNodeSplitEdges" in src

    def test_triangulate_compiles(self):
        src = _compile_model("tri", lambda: output(
            cube(1, 1, 1) | triangulate(quad_method="FIXED", ngon_method="CLIP")
        ))
        _assert_valid_python(src)
        assert "GeometryNodeTriangulate" in src
        assert '.quad_method = "FIXED"' in src
        assert '.ngon_method = "CLIP"' in src


class TestOtherOpsFigures:
    """Integration tests showing composed pipelines with Other ops."""

    def test_triangulate_split_pipeline(self):
        """Cube → triangulate → split edges → translate."""
        src = _compile_model("tri_split", lambda: output(
            cube(1, 1, 1) | triangulate() | split_edges() | translate(0, 0, 1)
        ))
        _assert_valid_python(src)
        assert "GeometryNodeTriangulate" in src
        assert "GeometryNodeSplitEdges" in src

    def test_distribute_scale_pipeline(self):
        """Cube → distribute points on faces → scale."""
        src = _compile_model("dist_scale", lambda: output(
            cube(2, 2, 2) | distribute_points_on_faces(density=20.0) | scale_by(0.5, 0.5, 0.5)
        ))
        _assert_valid_python(src)
        assert "GeometryNodeDistributePointsOnFaces" in src

    def test_convex_hull_of_duplicated(self):
        """Cube → duplicate elements → convex hull."""
        src = _compile_model("dup_ch", lambda: output(
            cube(1, 1, 1) | duplicate_elements(amount=5) | convex_hull()
        ))
        _assert_valid_python(src)
        assert "GeometryNodeDuplicateElements" in src
        assert "GeometryNodeConvexHull" in src


# ── Batch 8: Other Ops (continued) ───────────────────────────────────────────


class TestOtherOps2IR:
    """IR-level tests for batch 8 Other nodes."""

    def test_bounding_box(self):
        node = cube(1, 1, 1) | bounding_box()
        assert isinstance(node, IRGeometryOp)
        assert node.op_type == "GeometryNodeBoundBox"
        assert node.properties["use_radius"] is True

    def test_bounding_box_no_radius(self):
        node = cube(1, 1, 1) | bounding_box(use_radius=False)
        assert node.properties["use_radius"] is False

    def test_separate_components_mesh(self):
        node = cube(1, 1, 1) | separate_components("Mesh")
        assert isinstance(node, IRSeparateComponents)
        assert node.component == "Mesh"

    def test_separate_components_volume(self):
        node = cube(1, 1, 1) | separate_components("Volume")
        assert node.component == "Volume"

    def test_separate_components_default(self):
        node = cube(1, 1, 1) | separate_components()
        assert node.component == "Mesh"

    def test_separate_geometry(self):
        node = cube(1, 1, 1) | separate_geometry()
        assert isinstance(node, IRGeometryOp)
        assert node.op_type == "GeometryNodeSeparateGeometry"

    def test_set_id(self):
        node = cube(1, 1, 1) | set_id(42)
        assert isinstance(node, IRGeometryOp)
        assert node.op_type == "GeometryNodeSetID"
        assert node.properties["id_value"] == 42

    def test_set_id_default(self):
        node = cube(1, 1, 1) | set_id()
        assert node.properties["id_value"] == 0

    def test_set_point_radius(self):
        node = cube(1, 1, 1) | set_point_radius(0.1)
        assert isinstance(node, IRGeometryOp)
        assert node.op_type == "GeometryNodeSetPointRadius"
        assert node.properties["radius"] == 0.1

    def test_set_point_radius_default(self):
        node = cube(1, 1, 1) | set_point_radius()
        assert node.properties["radius"] == 0.05

    def test_sort_elements(self):
        node = cube(1, 1, 1) | sort_elements(sort_weight=1.5, group_id=3, domain="FACE")
        assert isinstance(node, IRGeometryOp)
        assert node.op_type == "GeometryNodeSortElements"
        assert node.properties["sort_weight"] == 1.5
        assert node.properties["group_id"] == 3
        assert node.properties["domain"] == "FACE"

    def test_sort_elements_defaults(self):
        node = cube(1, 1, 1) | sort_elements()
        assert node.properties["sort_weight"] == 0.0
        assert node.properties["group_id"] == 0
        assert node.properties["domain"] == "POINT"


class TestOtherOps2Compiler:
    """Compiler tests for batch 8 Other nodes."""

    def test_bounding_box_compiles(self):
        src = _compile_model("bbox", lambda: output(cube(1, 1, 1) | bounding_box()))
        _assert_valid_python(src)
        assert "GeometryNodeBoundBox" in src

    def test_separate_components_compiles(self):
        src = _compile_model("sep_c", lambda: output(cube(1, 1, 1) | separate_components("Mesh")))
        _assert_valid_python(src)
        assert "GeometryNodeSeparateComponents" in src

    def test_separate_components_curve_compiles(self):
        src = _compile_model("sep_cv", lambda: output(cube(1, 1, 1) | separate_components("Curve")))
        _assert_valid_python(src)
        assert "GeometryNodeSeparateComponents" in src

    def test_separate_geometry_compiles(self):
        src = _compile_model("sep_g", lambda: output(cube(1, 1, 1) | separate_geometry()))
        _assert_valid_python(src)
        assert "GeometryNodeSeparateGeometry" in src

    def test_set_id_compiles(self):
        src = _compile_model("sid", lambda: output(cube(1, 1, 1) | set_id(42)))
        _assert_valid_python(src)
        assert "GeometryNodeSetID" in src

    def test_set_point_radius_compiles(self):
        src = _compile_model("spr", lambda: output(cube(1, 1, 1) | set_point_radius(0.1)))
        _assert_valid_python(src)
        assert "GeometryNodeSetPointRadius" in src

    def test_sort_elements_compiles(self):
        src = _compile_model("sort", lambda: output(
            cube(1, 1, 1) | sort_elements(sort_weight=1.0, domain="FACE")
        ))
        _assert_valid_python(src)
        assert "GeometryNodeSortElements" in src
        assert '.domain = "FACE"' in src


class TestOtherOps2Figures:
    """Integration tests for batch 8 Other ops."""

    def test_bbox_pipeline(self):
        """Cube → bounding box → translate."""
        src = _compile_model("bbox_pipe", lambda: output(
            cube(1, 1, 1) | bounding_box() | translate(0, 0, 1)
        ))
        _assert_valid_python(src)
        assert "GeometryNodeBoundBox" in src
        assert "GeometryNodeTransform" in src

    def test_separate_and_transform(self):
        """Cube → separate components (Mesh) → translate."""
        src = _compile_model("sep_tr", lambda: output(
            cube(1, 1, 1) | separate_components("Mesh") | translate(1, 0, 0)
        ))
        _assert_valid_python(src)
        assert "GeometryNodeSeparateComponents" in src

    def test_set_id_and_sort(self):
        """Cube → set id → sort elements."""
        src = _compile_model("id_sort", lambda: output(
            cube(1, 1, 1) | set_id(10) | sort_elements(sort_weight=2.0)
        ))
        _assert_valid_python(src)
        assert "GeometryNodeSetID" in src
        assert "GeometryNodeSortElements" in src


# ── Batch 9: Attribute Ops ───────────────────────────────────────────────


class TestAttributeOpsIR:
    """IR-level tests for attribute operations."""

    def test_store_named_attribute(self):
        node = cube(1, 1, 1) | store_named_attribute(name="density", value=1.5, data_type="FLOAT", domain="FACE")
        assert isinstance(node, IRGeometryOp)
        assert node.op_type == "GeometryNodeStoreNamedAttribute"
        assert node.properties["name"] == "density"
        assert node.properties["value"] == 1.5
        assert node.properties["data_type"] == "FLOAT"
        assert node.properties["domain"] == "FACE"

    def test_store_named_attribute_defaults(self):
        node = cube(1, 1, 1) | store_named_attribute()
        assert node.properties["name"] == ""
        assert node.properties["value"] == 0.0
        assert node.properties["data_type"] == "FLOAT"
        assert node.properties["domain"] == "POINT"

    def test_remove_named_attribute(self):
        node = cube(1, 1, 1) | remove_named_attribute(name="density")
        assert isinstance(node, IRGeometryOp)
        assert node.op_type == "GeometryNodeRemoveAttribute"
        assert node.properties["name"] == "density"

    def test_remove_named_attribute_default(self):
        node = cube(1, 1, 1) | remove_named_attribute()
        assert node.properties["name"] == ""


class TestAttributeOpsCompiler:
    """Compiler tests for attribute operations."""

    def test_store_named_attribute_compiles(self):
        src = _compile_model("sna", lambda: output(
            cube(1, 1, 1) | store_named_attribute(name="density", value=1.5, data_type="FLOAT", domain="FACE")
        ))
        _assert_valid_python(src)
        assert "GeometryNodeStoreNamedAttribute" in src
        assert '.data_type = "FLOAT"' in src
        assert '.domain = "FACE"' in src
        assert '"Name"].default_value' in src

    def test_store_named_attribute_vector_type(self):
        src = _compile_model("sna_v", lambda: output(
            cube(1, 1, 1) | store_named_attribute(name="offset", value=2.0, data_type="FLOAT_VECTOR")
        ))
        _assert_valid_python(src)
        assert '.data_type = "FLOAT_VECTOR"' in src

    def test_remove_named_attribute_compiles(self):
        src = _compile_model("rna", lambda: output(
            cube(1, 1, 1) | remove_named_attribute(name="density")
        ))
        _assert_valid_python(src)
        assert "GeometryNodeRemoveAttribute" in src
        assert '"Name"].default_value' in src


class TestAttributeOpsFigures:
    """Integration tests for attribute ops."""

    def test_store_then_remove(self):
        """Cube → store named attribute → remove named attribute."""
        src = _compile_model("attr_pipe", lambda: output(
            cube(1, 1, 1)
            | store_named_attribute(name="weight", value=1.0)
            | remove_named_attribute(name="weight")
        ))
        _assert_valid_python(src)
        assert "GeometryNodeStoreNamedAttribute" in src
        assert "GeometryNodeRemoveAttribute" in src

    def test_store_attribute_and_transform(self):
        """Cube → store named attribute → translate."""
        src = _compile_model("attr_tr", lambda: output(
            cube(1, 1, 1) | store_named_attribute(name="id", value=5.0) | translate(0, 0, 1)
        ))
        _assert_valid_python(src)
        assert "GeometryNodeStoreNamedAttribute" in src
        assert "GeometryNodeTransform" in src


# ---------------------------------------------------------------------------
# Batch 10 — More Other ops
# ---------------------------------------------------------------------------


class TestOtherOps2IR:
    """IR-level tests for batch 10 other ops."""

    def test_points_to_vertices_ir(self):
        op = points_to_vertices()
        node = op(IRPrimitive(primitive_type=PrimitiveType.POINT, properties={}, label="pt"))
        assert isinstance(node, IRGeometryOp)
        assert node.op_type == "GeometryNodePointsToVertices"

    def test_set_geometry_name_ir(self):
        op = set_geometry_name(name="debug")
        node = op(IRPrimitive(primitive_type=PrimitiveType.CUBE, properties={"size": (1, 1, 1)}, label="c"))
        assert isinstance(node, IRGeometryOp)
        assert node.op_type == "GeometryNodeSetGeometryName"
        assert node.properties["name"] == "debug"

    def test_set_face_set_ir(self):
        op = set_face_set(face_set=3)
        node = op(IRPrimitive(primitive_type=PrimitiveType.CUBE, properties={"size": (1, 1, 1)}, label="c"))
        assert isinstance(node, IRGeometryOp)
        assert node.op_type == "GeometryNodeToolSetFaceSet"
        assert node.properties["face_set"] == 3

    def test_set_selection_ir(self):
        op = set_selection(domain="FACE", selection_type="FLOAT")
        node = op(IRPrimitive(primitive_type=PrimitiveType.CUBE, properties={"size": (1, 1, 1)}, label="c"))
        assert isinstance(node, IRGeometryOp)
        assert node.op_type == "GeometryNodeToolSetSelection"
        assert node.properties["domain"] == "FACE"
        assert node.properties["selection_type"] == "FLOAT"

    def test_merge_layers_ir(self):
        op = merge_layers(mode="MERGE_BY_ID", group_id=5)
        node = op(IRPrimitive(primitive_type=PrimitiveType.POINT, properties={}, label="gp"))
        assert isinstance(node, IRGeometryOp)
        assert node.op_type == "GeometryNodeMergeLayers"
        assert node.properties["mode"] == "MERGE_BY_ID"
        assert node.properties["group_id"] == 5

    def test_set_grease_pencil_depth_ir(self):
        op = set_grease_pencil_depth(depth_order="3D")
        node = op(IRPrimitive(primitive_type=PrimitiveType.POINT, properties={}, label="gp"))
        assert isinstance(node, IRGeometryOp)
        assert node.op_type == "GeometryNodeSetGreasePencilDepth"
        assert node.properties["depth_order"] == "3D"

    def test_set_grease_pencil_softness_ir(self):
        op = set_grease_pencil_softness(softness=0.5)
        node = op(IRPrimitive(primitive_type=PrimitiveType.POINT, properties={}, label="gp"))
        assert isinstance(node, IRGeometryOp)
        assert node.op_type == "GeometryNodeSetGreasePencilSoftness"
        assert node.properties["softness"] == 0.5


class TestOtherOps2Compiler:
    """Compilation tests for batch 10 other ops."""

    def test_points_to_vertices_compiles(self):
        src = _compile_model("ptv", lambda: output(
            cube(1, 1, 1) | points_to_vertices()
        ))
        _assert_valid_python(src)
        assert "GeometryNodePointsToVertices" in src

    def test_set_geometry_name_compiles(self):
        src = _compile_model("sgn", lambda: output(
            cube(1, 1, 1) | set_geometry_name(name="my_geo")
        ))
        _assert_valid_python(src)
        assert "GeometryNodeSetGeometryName" in src
        assert '"Name"].default_value' in src

    def test_set_face_set_compiles(self):
        src = _compile_model("sfs", lambda: output(
            cube(1, 1, 1) | set_face_set(face_set=2)
        ))
        _assert_valid_python(src)
        assert "GeometryNodeToolSetFaceSet" in src

    def test_set_selection_compiles(self):
        src = _compile_model("ssel", lambda: output(
            cube(1, 1, 1) | set_selection(domain="FACE", selection_type="FLOAT")
        ))
        _assert_valid_python(src)
        assert "GeometryNodeToolSetSelection" in src
        assert 'selection_type = "FLOAT"' in src

    def test_merge_layers_compiles(self):
        src = _compile_model("ml", lambda: output(
            cube(1, 1, 1) | merge_layers(mode="MERGE_BY_ID", group_id=3)
        ))
        _assert_valid_python(src)
        assert "GeometryNodeMergeLayers" in src
        assert 'mode = "MERGE_BY_ID"' in src

    def test_set_grease_pencil_depth_compiles(self):
        src = _compile_model("gpd", lambda: output(
            cube(1, 1, 1) | set_grease_pencil_depth(depth_order="3D")
        ))
        _assert_valid_python(src)
        assert "GeometryNodeSetGreasePencilDepth" in src
        assert 'depth_order = "3D"' in src

    def test_set_grease_pencil_softness_compiles(self):
        src = _compile_model("gps", lambda: output(
            cube(1, 1, 1) | set_grease_pencil_softness(softness=0.8)
        ))
        _assert_valid_python(src)
        assert "GeometryNodeSetGreasePencilSoftness" in src


class TestOtherOps2Figures:
    """Integration tests for batch 10 other ops."""

    def test_points_to_vertices_pipeline(self):
        src = _compile_model("ptv_pipe", lambda: output(
            cube(1, 1, 1) | points_to_vertices() | translate(0, 0, 1)
        ))
        _assert_valid_python(src)
        assert "GeometryNodePointsToVertices" in src
        assert "GeometryNodeTransform" in src

    def test_set_name_then_transform(self):
        src = _compile_model("name_tr", lambda: output(
            cube(1, 1, 1) | set_geometry_name(name="base") | translate(1, 0, 0)
        ))
        _assert_valid_python(src)
        assert "GeometryNodeSetGeometryName" in src
        assert "GeometryNodeTransform" in src

    def test_face_set_and_selection(self):
        src = _compile_model("fs_sel", lambda: output(
            cube(1, 1, 1) | set_face_set(face_set=1) | set_selection(domain="FACE")
        ))
        _assert_valid_python(src)
        assert "GeometryNodeToolSetFaceSet" in src
        assert "GeometryNodeToolSetSelection" in src

    def test_grease_pencil_chain(self):
        src = _compile_model("gp_chain", lambda: output(
            cube(1, 1, 1)
            | set_grease_pencil_depth(depth_order="3D")
            | set_grease_pencil_softness(softness=0.3)
            | merge_layers(mode="MERGE_BY_NAME")
        ))
        _assert_valid_python(src)
        assert "GeometryNodeSetGreasePencilDepth" in src
        assert "GeometryNodeSetGreasePencilSoftness" in src
        assert "GeometryNodeMergeLayers" in src


# ---------------------------------------------------------------------------
# Batch 11 — Importers
# ---------------------------------------------------------------------------


class TestImportersIR:
    """IR-level tests for importer primitives."""

    def test_import_obj_ir(self):
        node = import_obj(path="/tmp/model.obj")
        assert isinstance(node, IRPrimitive)
        assert node.primitive_type == PrimitiveType.IMPORT_OBJ
        assert node.properties["path"] == "/tmp/model.obj"

    def test_import_stl_ir(self):
        node = import_stl(path="/tmp/model.stl")
        assert isinstance(node, IRPrimitive)
        assert node.primitive_type == PrimitiveType.IMPORT_STL

    def test_import_ply_ir(self):
        node = import_ply(path="/tmp/model.ply")
        assert isinstance(node, IRPrimitive)
        assert node.primitive_type == PrimitiveType.IMPORT_PLY

    def test_import_csv_ir(self):
        node = import_csv(path="/tmp/points.csv", delimiter=";")
        assert isinstance(node, IRPrimitive)
        assert node.primitive_type == PrimitiveType.IMPORT_CSV
        assert node.properties["delimiter"] == ";"

    def test_import_vdb_ir(self):
        node = import_vdb(path="/tmp/volume.vdb")
        assert isinstance(node, IRPrimitive)
        assert node.primitive_type == PrimitiveType.IMPORT_VDB


class TestImportersCompiler:
    """Compilation tests for importers."""

    def test_import_obj_compiles(self):
        src = _compile_model("obj", lambda: output(import_obj(path="/tmp/m.obj")))
        _assert_valid_python(src)
        assert "GeometryNodeImportOBJ" in src
        assert '["Path"].default_value' in src

    def test_import_stl_compiles(self):
        src = _compile_model("stl", lambda: output(import_stl(path="/tmp/m.stl")))
        _assert_valid_python(src)
        assert "GeometryNodeImportSTL" in src

    def test_import_ply_compiles(self):
        src = _compile_model("ply", lambda: output(import_ply(path="/tmp/m.ply")))
        _assert_valid_python(src)
        assert "GeometryNodeImportPLY" in src

    def test_import_csv_compiles(self):
        src = _compile_model("csv", lambda: output(import_csv(path="/tmp/p.csv", delimiter=";")))
        _assert_valid_python(src)
        assert "GeometryNodeImportCSV" in src
        assert '["Delimiter"].default_value' in src

    def test_import_vdb_compiles(self):
        src = _compile_model("vdb", lambda: output(import_vdb(path="/tmp/v.vdb")))
        _assert_valid_python(src)
        assert "GeometryNodeImportVDB" in src


class TestImportersFigures:
    """Integration tests for importers in pipelines."""

    def test_import_obj_transform(self):
        src = _compile_model("obj_tr", lambda: output(
            import_obj(path="/tmp/m.obj") | translate(0, 0, 1)
        ))
        _assert_valid_python(src)
        assert "GeometryNodeImportOBJ" in src
        assert "GeometryNodeTransform" in src

    def test_import_stl_subdivide(self):
        src = _compile_model("stl_sub", lambda: output(
            import_stl(path="/tmp/m.stl") | subdivide(level=2)
        ))
        _assert_valid_python(src)
        assert "GeometryNodeImportSTL" in src
        assert "GeometryNodeSubdivideMesh" in src

    def test_import_csv_points_to_vertices(self):
        src = _compile_model("csv_ptv", lambda: output(
            import_csv(path="/tmp/p.csv") | points_to_vertices()
        ))
        _assert_valid_python(src)
        assert "GeometryNodeImportCSV" in src
        assert "GeometryNodePointsToVertices" in src


# ---------------------------------------------------------------------------
# Batch 12 — Switch, Volume Grid ops, GP Color, Viewer
# ---------------------------------------------------------------------------


class TestBatch12IR:
    """IR-level tests for batch 12 ops."""

    def test_switch_ir(self):
        s = sphere(1)
        op = switch(switch_value=True, true_child=s)
        node = op(IRPrimitive(primitive_type=PrimitiveType.CUBE, properties={"size": (1, 1, 1)}, label="c"))
        assert isinstance(node, IRGeometryOp)
        assert node.op_type == "GeometryNodeSwitch"
        assert node.properties["switch"] is True
        assert node.properties["input_type"] == "GEOMETRY"
        assert "True" in node.extra_children

    def test_switch_ir_default(self):
        op = switch()
        node = op(IRPrimitive(primitive_type=PrimitiveType.CUBE, properties={"size": (1, 1, 1)}, label="c"))
        assert node.properties["switch"] is False
        assert node.extra_children == {}

    def test_get_named_grid_ir(self):
        op = get_named_grid(name="density", remove=False, data_type="FLOAT")
        node = op(IRPrimitive(primitive_type=PrimitiveType.VOLUME_CUBE, properties={"density": 1.0, "background": 0.0, "min": (-1, -1, -1), "max": (1, 1, 1), "resolution_x": 32, "resolution_y": 32, "resolution_z": 32}, label="v"))
        assert isinstance(node, IRGeometryOp)
        assert node.op_type == "GeometryNodeGetNamedGrid"
        assert node.properties["name"] == "density"
        assert node.properties["remove"] is False

    def test_store_named_grid_ir(self):
        op = store_named_grid(name="temp", grid_value=0.5, data_type="FLOAT")
        node = op(IRPrimitive(primitive_type=PrimitiveType.VOLUME_CUBE, properties={"density": 1.0, "background": 0.0, "min": (-1, -1, -1), "max": (1, 1, 1), "resolution_x": 32, "resolution_y": 32, "resolution_z": 32}, label="v"))
        assert isinstance(node, IRGeometryOp)
        assert node.op_type == "GeometryNodeStoreNamedGrid"
        assert node.properties["grid_value"] == 0.5

    def test_set_grease_pencil_color_ir(self):
        op = set_grease_pencil_color(color=(1.0, 0.0, 0.0, 1.0), opacity=0.8)
        node = op(IRPrimitive(primitive_type=PrimitiveType.POINT, properties={}, label="gp"))
        assert isinstance(node, IRGeometryOp)
        assert node.op_type == "GeometryNodeSetGreasePencilColor"
        assert node.properties["color"] == (1.0, 0.0, 0.0, 1.0)
        assert node.properties["opacity"] == 0.8

    def test_viewer_ir(self):
        op = viewer(value=1.0, data_type="INT", domain="POINT")
        node = op(IRPrimitive(primitive_type=PrimitiveType.CUBE, properties={"size": (1, 1, 1)}, label="c"))
        assert isinstance(node, IRGeometryOp)
        assert node.op_type == "GeometryNodeViewer"
        assert node.properties["domain"] == "POINT"


class TestBatch12Compiler:
    """Compilation tests for batch 12 ops."""

    def test_switch_compiles(self):
        src = _compile_model("sw", lambda: output(
            cube(1, 1, 1) | switch(switch_value=True, true_child=sphere(1))
        ))
        _assert_valid_python(src)
        assert "GeometryNodeSwitch" in src
        assert 'input_type = "GEOMETRY"' in src

    def test_get_named_grid_compiles(self):
        src = _compile_model("gng", lambda: output(
            volume_cube(1.0, 0.0) | get_named_grid(name="density", data_type="FLOAT")
        ))
        _assert_valid_python(src)
        assert "GeometryNodeGetNamedGrid" in src
        assert '"Name"].default_value' in src

    def test_store_named_grid_compiles(self):
        src = _compile_model("sng", lambda: output(
            volume_cube(1.0, 0.0) | store_named_grid(name="temp", grid_value=0.5)
        ))
        _assert_valid_python(src)
        assert "GeometryNodeStoreNamedGrid" in src

    def test_set_grease_pencil_color_compiles(self):
        src = _compile_model("gpc", lambda: output(
            cube(1, 1, 1) | set_grease_pencil_color(color=(1.0, 0.0, 0.0, 1.0), opacity=0.5)
        ))
        _assert_valid_python(src)
        assert "GeometryNodeSetGreasePencilColor" in src
        assert '["Color"].default_value' in src

    def test_viewer_compiles(self):
        src = _compile_model("vw", lambda: output(
            cube(1, 1, 1) | viewer(value=1.0) | translate(0, 0, 1)
        ))
        _assert_valid_python(src)
        assert "GeometryNodeViewer" in src
        assert "GeometryNodeTransform" in src

    def test_viewer_passthrough(self):
        """Viewer should act as pass-through — pipeline continues after it."""
        src = _compile_model("vw_pt", lambda: output(
            cube(1, 1, 1) | viewer() | subdivide(level=2)
        ))
        _assert_valid_python(src)
        assert "GeometryNodeViewer" in src
        assert "GeometryNodeSubdivideMesh" in src


class TestBatch12Figures:
    """Integration tests for batch 12 ops."""

    def test_switch_pipeline(self):
        src = _compile_model("sw_pipe", lambda: output(
            cube(1, 1, 1) | switch(switch_value=False, true_child=sphere(1)) | translate(0, 0, 1)
        ))
        _assert_valid_python(src)
        assert "GeometryNodeSwitch" in src
        assert "GeometryNodeTransform" in src

    def test_volume_grid_roundtrip(self):
        src = _compile_model("grid_rt", lambda: output(
            volume_cube(1.0, 0.0)
            | store_named_grid(name="density", grid_value=1.0)
            | get_named_grid(name="density")
        ))
        _assert_valid_python(src)
        assert "GeometryNodeStoreNamedGrid" in src
        assert "GeometryNodeGetNamedGrid" in src

    def test_gp_color_chain(self):
        src = _compile_model("gp_cc", lambda: output(
            cube(1, 1, 1)
            | set_grease_pencil_color(color=(0.5, 0.5, 0.5, 1.0), opacity=0.9)
            | set_grease_pencil_softness(softness=0.2)
        ))
        _assert_valid_python(src)
        assert "GeometryNodeSetGreasePencilColor" in src
        assert "GeometryNodeSetGreasePencilSoftness" in src

    def test_viewer_between_ops(self):
        src = _compile_model("vw_mid", lambda: output(
            cube(1, 1, 1) | extrude(offset_scale=0.5) | viewer() | translate(0, 1, 0)
        ))
        _assert_valid_python(src)
        assert "GeometryNodeViewer" in src
        assert "GeometryNodeExtrudeMesh" in src
        assert "GeometryNodeTransform" in src


# ---------------------------------------------------------------------------
# Batch 13 — Collection Info, Object Info
# ---------------------------------------------------------------------------


class TestBatch13IR:
    """IR-level tests for collection/object info primitives."""

    def test_collection_info_ir(self):
        node = collection_info(collection="MyCollection", separate_children=True)
        assert isinstance(node, IRPrimitive)
        assert node.primitive_type == PrimitiveType.COLLECTION_INFO
        assert node.properties["collection"] == "MyCollection"
        assert node.properties["separate_children"] is True

    def test_collection_info_defaults(self):
        node = collection_info()
        assert node.properties["collection"] == ""
        assert node.properties["separate_children"] is False
        assert node.properties["reset_children"] is False
        assert node.properties["transform_space"] == "ORIGINAL"

    def test_object_info_ir(self):
        node = object_info(object="Cube", as_instance=True, transform_space="RELATIVE")
        assert isinstance(node, IRPrimitive)
        assert node.primitive_type == PrimitiveType.OBJECT_INFO
        assert node.properties["object"] == "Cube"
        assert node.properties["as_instance"] is True
        assert node.properties["transform_space"] == "RELATIVE"

    def test_object_info_defaults(self):
        node = object_info()
        assert node.properties["object"] == ""
        assert node.properties["as_instance"] is False
        assert node.properties["transform_space"] == "ORIGINAL"


class TestBatch13Compiler:
    """Compilation tests for collection/object info."""

    def test_collection_info_compiles(self):
        src = _compile_model("ci", lambda: output(collection_info(collection="Parts")))
        _assert_valid_python(src)
        assert "GeometryNodeCollectionInfo" in src
        assert "bpy.data.collections.get('Parts')" in src

    def test_collection_info_separate(self):
        src = _compile_model("ci_sep", lambda: output(
            collection_info(collection="Items", separate_children=True, transform_space="RELATIVE")
        ))
        _assert_valid_python(src)
        assert "GeometryNodeCollectionInfo" in src
        assert '"Separate Children"].default_value = True' in src
        assert 'transform_space = "RELATIVE"' in src

    def test_object_info_compiles(self):
        src = _compile_model("oi", lambda: output(object_info(object="Suzanne")))
        _assert_valid_python(src)
        assert "GeometryNodeObjectInfo" in src
        assert "bpy.data.objects.get('Suzanne')" in src

    def test_object_info_as_instance(self):
        src = _compile_model("oi_inst", lambda: output(
            object_info(object="Base", as_instance=True, transform_space="RELATIVE")
        ))
        _assert_valid_python(src)
        assert '"As Instance"].default_value = True' in src
        assert 'transform_space = "RELATIVE"' in src


class TestBatch13Figures:
    """Integration tests for collection/object info in pipelines."""

    def test_collection_info_transform(self):
        src = _compile_model("ci_tr", lambda: output(
            collection_info(collection="Parts") | translate(0, 0, 2)
        ))
        _assert_valid_python(src)
        assert "GeometryNodeCollectionInfo" in src
        assert "GeometryNodeTransform" in src

    def test_object_info_subdivide(self):
        src = _compile_model("oi_sub", lambda: output(
            object_info(object="Cube") | subdivide(level=2)
        ))
        _assert_valid_python(src)
        assert "GeometryNodeObjectInfo" in src
        assert "GeometryNodeSubdivideMesh" in src

    def test_collection_and_object_join(self):
        src = _compile_model("ci_oi_join", lambda: output(
            join([
                collection_info(collection="A"),
                object_info(object="B"),
            ])
        ))
        _assert_valid_python(src)
        assert "GeometryNodeCollectionInfo" in src
        assert "GeometryNodeObjectInfo" in src
        assert "GeometryNodeJoinGeometry" in src


# ===================================================================
# Batch 14 — Info / Query nodes
# ===================================================================


class TestBatch14IR:
    """IR-level tests for info/query nodes."""

    def test_curve_length_ir(self):
        node = cube(1, 1, 1) | curve_length()
        assert isinstance(node, IRGeometryOp)
        assert node.op_type == "GeometryNodeCurveLength"

    def test_domain_size_ir(self):
        node = cube(1, 1, 1) | domain_size()
        assert isinstance(node, IRGeometryOp)
        assert node.op_type == "GeometryNodeAttributeDomainSize"

    def test_geometry_proximity_ir(self):
        node = cube(1, 1, 1) | geometry_proximity(target_element="POINTS")
        assert isinstance(node, IRGeometryOp)
        assert node.op_type == "GeometryNodeProximity"
        assert node.properties["target_element"] == "POINTS"

    def test_sample_nearest_ir(self):
        node = cube(1, 1, 1) | sample_nearest(domain="FACE")
        assert isinstance(node, IRGeometryOp)
        assert node.op_type == "GeometryNodeSampleNearest"
        assert node.properties["domain"] == "FACE"

    def test_sample_index_ir(self):
        node = cube(1, 1, 1) | sample_index(value=1.0, index=5, data_type="FLOAT", clamp=True)
        assert isinstance(node, IRGeometryOp)
        assert node.op_type == "GeometryNodeSampleIndex"
        assert node.properties["index"] == 5
        assert node.properties["clamp"] is True

    def test_attribute_statistic_ir(self):
        node = cube(1, 1, 1) | attribute_statistic(attribute=2.0, domain="FACE")
        assert isinstance(node, IRGeometryOp)
        assert node.op_type == "GeometryNodeAttributeStatistic"
        assert node.properties["attribute"] == 2.0


class TestBatch14Compiler:
    """Compiler output tests for info/query nodes."""

    def test_curve_length_compile(self):
        src = _compile_model("cl", lambda: output(cube(1, 1, 1) | curve_length()))
        _assert_valid_python(src)
        assert "GeometryNodeCurveLength" in src

    def test_domain_size_compile(self):
        src = _compile_model("ds", lambda: output(cube(1, 1, 1) | domain_size()))
        _assert_valid_python(src)
        assert "GeometryNodeAttributeDomainSize" in src

    def test_geometry_proximity_compile(self):
        src = _compile_model("prox", lambda: output(
            cube(1, 1, 1) | geometry_proximity(target_element="EDGES")
        ))
        _assert_valid_python(src)
        assert "GeometryNodeProximity" in src
        assert 'target_element = "EDGES"' in src

    def test_sample_nearest_compile(self):
        src = _compile_model("sn", lambda: output(
            cube(1, 1, 1) | sample_nearest(domain="FACE", sample_position=(1.0, 2.0, 3.0))
        ))
        _assert_valid_python(src)
        assert "GeometryNodeSampleNearest" in src
        assert 'domain = "FACE"' in src
        assert "FunctionNodeInputVector" in src

    def test_sample_index_compile(self):
        src = _compile_model("si", lambda: output(
            cube(1, 1, 1) | sample_index(value=1.5, index=3, clamp=True)
        ))
        _assert_valid_python(src)
        assert "GeometryNodeSampleIndex" in src
        assert '"Clamp"].default_value = True' in src

    def test_attribute_statistic_compile(self):
        src = _compile_model("as", lambda: output(
            cube(1, 1, 1) | attribute_statistic(attribute=0.5, domain="POINT")
        ))
        _assert_valid_python(src)
        assert "GeometryNodeAttributeStatistic" in src
        assert 'domain = "POINT"' in src


class TestBatch14Figures:
    """Integration tests for info/query nodes in pipelines."""

    def test_curve_length_pipeline(self):
        src = _compile_model("cl_pipe", lambda: output(
            cube(1, 1, 1) | mesh_to_curve() | curve_length()
        ))
        _assert_valid_python(src)
        assert "GeometryNodeMeshToCurve" in src
        assert "GeometryNodeCurveLength" in src

    def test_proximity_with_position(self):
        src = _compile_model("prox_pos", lambda: output(
            cube(2, 2, 2) | geometry_proximity(
                target_element="FACES",
                sample_position=(1.0, 0.0, 0.0),
            )
        ))
        _assert_valid_python(src)
        assert "GeometryNodeProximity" in src
        assert 'target_element = "FACES"' in src

    def test_sample_nearest_on_sphere(self):
        src = _compile_model("sn_sph", lambda: output(
            sphere(1.0) | sample_nearest(sample_position=(0.5, 0.5, 0.5))
        ))
        _assert_valid_python(src)
        assert "GeometryNodeSampleNearest" in src
        assert "FunctionNodeInputVector" in src


# ===================================================================
# Batch 15 — Sampling + Grid conversion nodes
# ===================================================================


class TestBatch15IR:
    """IR-level tests for sampling/grid nodes."""

    def test_raycast_ir(self):
        node = cube(1, 1, 1) | raycast(ray_length=50.0)
        assert isinstance(node, IRGeometryOp)
        assert node.op_type == "GeometryNodeRaycast"
        assert node.properties["ray_length"] == 50.0

    def test_sample_nearest_surface_ir(self):
        node = cube(1, 1, 1) | sample_nearest_surface(value=1.0)
        assert isinstance(node, IRGeometryOp)
        assert node.op_type == "GeometryNodeSampleNearestSurface"

    def test_sample_uv_surface_ir(self):
        node = cube(1, 1, 1) | sample_uv_surface(
            uv_map=(0.5, 0.5, 0.0), sample_uv=(0.1, 0.2, 0.0)
        )
        assert isinstance(node, IRGeometryOp)
        assert node.op_type == "GeometryNodeSampleUVSurface"
        assert node.properties["uv_map"] == (0.5, 0.5, 0.0)

    def test_mesh_to_sdf_grid_ir(self):
        node = cube(1, 1, 1) | mesh_to_sdf_grid(voxel_size=0.1, band_width=5)
        assert isinstance(node, IRGeometryOp)
        assert node.op_type == "GeometryNodeMeshToSDFGrid"
        assert node.properties["band_width"] == 5

    def test_mesh_to_density_grid_ir(self):
        node = cube(1, 1, 1) | mesh_to_density_grid(density=2.0, gradient_width=0.5)
        assert isinstance(node, IRGeometryOp)
        assert node.op_type == "GeometryNodeMeshToDensityGrid"
        assert node.properties["gradient_width"] == 0.5


class TestBatch15Compiler:
    """Compiler output tests for sampling/grid nodes."""

    def test_raycast_compile(self):
        src = _compile_model("rc", lambda: output(
            cube(1, 1, 1) | raycast(
                ray_direction=(0.0, -1.0, 0.0),
                ray_length=50.0,
                data_type="FLOAT",
            )
        ))
        _assert_valid_python(src)
        assert "GeometryNodeRaycast" in src
        assert "FunctionNodeInputVector" in src  # ray_direction vector

    def test_sample_nearest_surface_compile(self):
        src = _compile_model("sns", lambda: output(
            cube(1, 1, 1) | sample_nearest_surface(
                value=1.0,
                sample_position=(0.0, 1.0, 0.0),
            )
        ))
        _assert_valid_python(src)
        assert "GeometryNodeSampleNearestSurface" in src

    def test_sample_uv_surface_compile(self):
        src = _compile_model("suv", lambda: output(
            cube(1, 1, 1) | sample_uv_surface(
                uv_map=(0.5, 0.5, 0.0),
                sample_uv=(0.1, 0.2, 0.0),
            )
        ))
        _assert_valid_python(src)
        assert "GeometryNodeSampleUVSurface" in src
        assert "FunctionNodeInputVector" in src

    def test_mesh_to_sdf_grid_compile(self):
        src = _compile_model("sdf", lambda: output(
            cube(1, 1, 1) | mesh_to_sdf_grid(voxel_size=0.2, band_width=4)
        ))
        _assert_valid_python(src)
        assert "GeometryNodeMeshToSDFGrid" in src

    def test_mesh_to_density_grid_compile(self):
        src = _compile_model("dg", lambda: output(
            cube(1, 1, 1) | mesh_to_density_grid(density=2.0, voxel_size=0.1)
        ))
        _assert_valid_python(src)
        assert "GeometryNodeMeshToDensityGrid" in src


class TestBatch15Figures:
    """Integration tests for sampling/grid nodes in pipelines."""

    def test_raycast_on_subdivided(self):
        src = _compile_model("rc_sub", lambda: output(
            cube(2, 2, 2)
            | subdivide(level=2)
            | raycast(ray_direction=(0.0, 0.0, -1.0), ray_length=10.0)
        ))
        _assert_valid_python(src)
        assert "GeometryNodeSubdivideMesh" in src
        assert "GeometryNodeRaycast" in src

    def test_sdf_grid_pipeline(self):
        src = _compile_model("sdf_pipe", lambda: output(
            cube(1, 1, 1) | subdivide(level=1) | mesh_to_sdf_grid(voxel_size=0.1)
        ))
        _assert_valid_python(src)
        assert "GeometryNodeMeshToSDFGrid" in src

    def test_density_grid_pipeline(self):
        src = _compile_model("dg_pipe", lambda: output(
            sphere(1.0) | mesh_to_density_grid(density=1.5, gradient_width=0.3)
        ))
        _assert_valid_python(src)
        assert "GeometryNodeMeshToDensityGrid" in src


# ===========================================================================
# Batch 17 — Field Input Nodes (Curve Info, Mesh Info, Instance Info, Topology)
# ===========================================================================


from tanuki.dsl import (
    radius,
    is_edge_smooth,
    is_face_planar,
    is_face_smooth,
    curve_tangent,
    curve_tilt,
    is_spline_cyclic,
    spline_resolution,
    curve_handle_positions,
    endpoint_selection,
    handle_type_selection,
    spline_length,
    spline_parameter,
    curve_of_point,
    offset_point_in_curve,
    points_of_curve,
    shortest_edge_paths,
    instance_rotation,
    instance_scale,
    material_index,
)
from tanuki.ir.nodes import IRFieldInput


class TestBatch17FieldInputIR:
    """IR-level tests for new field input nodes."""

    def test_radius(self):
        n = radius()
        assert isinstance(n, IRFieldInput)
        assert n.field_type == "GeometryNodeInputRadius"
        assert n.output_socket == "Radius"

    def test_is_edge_smooth(self):
        n = is_edge_smooth()
        assert isinstance(n, IRFieldInput)
        assert n.field_type == "GeometryNodeInputEdgeSmooth"
        assert n.output_socket == "Smooth"

    def test_is_face_planar_default(self):
        n = is_face_planar()
        assert isinstance(n, IRFieldInput)
        assert n.field_type == "GeometryNodeInputMeshFaceIsPlanar"
        assert n.output_socket == "Planar"
        assert n.input_defaults == {"Threshold": 0.01}

    def test_is_face_planar_custom(self):
        n = is_face_planar(threshold=0.05)
        assert n.input_defaults == {"Threshold": 0.05}

    def test_is_face_smooth(self):
        n = is_face_smooth()
        assert isinstance(n, IRFieldInput)
        assert n.field_type == "GeometryNodeInputShadeSmooth"
        assert n.output_socket == "Smooth"

    def test_curve_tangent(self):
        n = curve_tangent()
        assert isinstance(n, IRFieldInput)
        assert n.field_type == "GeometryNodeInputTangent"
        assert n.output_socket == "Tangent"

    def test_curve_tilt(self):
        n = curve_tilt()
        assert isinstance(n, IRFieldInput)
        assert n.field_type == "GeometryNodeInputCurveTilt"
        assert n.output_socket == "Tilt"

    def test_is_spline_cyclic(self):
        n = is_spline_cyclic()
        assert isinstance(n, IRFieldInput)
        assert n.field_type == "GeometryNodeInputSplineCyclic"
        assert n.output_socket == "Cyclic"

    def test_spline_resolution(self):
        n = spline_resolution()
        assert isinstance(n, IRFieldInput)
        assert n.field_type == "GeometryNodeInputSplineResolution"
        assert n.output_socket == "Resolution"

    def test_curve_handle_positions_default(self):
        n = curve_handle_positions()
        assert isinstance(n, IRFieldInput)
        assert n.field_type == "GeometryNodeInputCurveHandlePositions"
        assert n.output_socket == "Left"
        assert n.input_defaults == {"Relative": False}

    def test_curve_handle_positions_right(self):
        n = curve_handle_positions(relative=True, output="Right")
        assert n.output_socket == "Right"
        assert n.input_defaults == {"Relative": True}

    def test_endpoint_selection(self):
        n = endpoint_selection(start_size=2, end_size=3)
        assert isinstance(n, IRFieldInput)
        assert n.field_type == "GeometryNodeCurveEndpointSelection"
        assert n.output_socket == "Selection"
        assert n.input_defaults == {"Start Size": 2, "End Size": 3}

    def test_handle_type_selection(self):
        n = handle_type_selection(handle_type="AUTO", mode="RIGHT")
        assert isinstance(n, IRFieldInput)
        assert n.field_type == "GeometryNodeCurveHandleTypeSelection"
        assert n.output_socket == "Selection"
        assert n.properties["handle_type"] == "AUTO"
        assert n.properties["mode"] == {"RIGHT"}

    def test_spline_length(self):
        n = spline_length()
        assert isinstance(n, IRFieldInput)
        assert n.output_socket == "Length"
        n2 = spline_length(output="Point Count")
        assert n2.output_socket == "Point Count"

    def test_spline_parameter(self):
        n = spline_parameter()
        assert n.output_socket == "Factor"
        n2 = spline_parameter(output="Length")
        assert n2.output_socket == "Length"
        n3 = spline_parameter(output="Index")
        assert n3.output_socket == "Index"

    def test_curve_of_point(self):
        n = curve_of_point(point_index=5, output="Index in Curve")
        assert isinstance(n, IRFieldInput)
        assert n.field_type == "GeometryNodeCurveOfPoint"
        assert n.output_socket == "Index in Curve"
        assert n.input_defaults == {"Point Index": 5}

    def test_offset_point_in_curve(self):
        n = offset_point_in_curve(point_index=0, offset=2, output="Point Index")
        assert isinstance(n, IRFieldInput)
        assert n.field_type == "GeometryNodeOffsetPointInCurve"
        assert n.output_socket == "Point Index"
        assert n.input_defaults == {"Point Index": 0, "Offset": 2}

    def test_points_of_curve(self):
        n = points_of_curve(curve_index=1, output="Total")
        assert isinstance(n, IRFieldInput)
        assert n.field_type == "GeometryNodePointsOfCurve"
        assert n.output_socket == "Total"
        assert n.input_defaults["Curve Index"] == 1

    def test_shortest_edge_paths(self):
        n = shortest_edge_paths(end_vertex=True, edge_cost=2.5, output="Total Cost")
        assert isinstance(n, IRFieldInput)
        assert n.field_type == "GeometryNodeInputShortestEdgePaths"
        assert n.output_socket == "Total Cost"
        assert n.input_defaults == {"End Vertex": True, "Edge Cost": 2.5}

    def test_instance_rotation(self):
        n = instance_rotation()
        assert isinstance(n, IRFieldInput)
        assert n.field_type == "GeometryNodeInputInstanceRotation"
        assert n.output_socket == "Rotation"

    def test_instance_scale(self):
        n = instance_scale()
        assert isinstance(n, IRFieldInput)
        assert n.field_type == "GeometryNodeInputInstanceScale"
        assert n.output_socket == "Scale"

    def test_material_index(self):
        n = material_index()
        assert isinstance(n, IRFieldInput)
        assert n.field_type == "GeometryNodeInputMaterialIndex"
        assert n.output_socket == "Material Index"


class TestBatch17Compile:
    """Compiler tests for new field input nodes."""

    def test_radius_compile(self):
        src = _compile_model("rad", lambda: output(
            cube(1, 1, 1) | store_named_attribute("r", radius())
        ))
        _assert_valid_python(src)
        assert "GeometryNodeInputRadius" in src

    def test_is_edge_smooth_compile(self):
        src = _compile_model("es", lambda: output(
            cube(1, 1, 1) | store_named_attribute("smooth", is_edge_smooth(), data_type="BOOLEAN")
        ))
        _assert_valid_python(src)
        assert "GeometryNodeInputEdgeSmooth" in src

    def test_is_face_planar_compile(self):
        src = _compile_model("fp", lambda: output(
            cube(1, 1, 1) | store_named_attribute("planar", is_face_planar(threshold=0.02), data_type="BOOLEAN")
        ))
        _assert_valid_python(src)
        assert "GeometryNodeInputMeshFaceIsPlanar" in src
        assert "Threshold" in src

    def test_is_face_smooth_compile(self):
        src = _compile_model("fs", lambda: output(
            cube(1, 1, 1) | store_named_attribute("smooth", is_face_smooth(), data_type="BOOLEAN")
        ))
        _assert_valid_python(src)
        assert "GeometryNodeInputShadeSmooth" in src

    def test_curve_tangent_compile(self):
        src = _compile_model("ct", lambda: output(
            curve_circle() | store_named_attribute("tang", curve_tangent(), data_type="FLOAT_VECTOR")
        ))
        _assert_valid_python(src)
        assert "GeometryNodeInputTangent" in src

    def test_curve_tilt_compile(self):
        src = _compile_model("ctilt", lambda: output(
            curve_circle() | store_named_attribute("tilt", curve_tilt())
        ))
        _assert_valid_python(src)
        assert "GeometryNodeInputCurveTilt" in src

    def test_is_spline_cyclic_compile(self):
        src = _compile_model("cyc", lambda: output(
            curve_circle() | store_named_attribute("cyclic", is_spline_cyclic(), data_type="BOOLEAN")
        ))
        _assert_valid_python(src)
        assert "GeometryNodeInputSplineCyclic" in src

    def test_spline_resolution_compile(self):
        src = _compile_model("sres", lambda: output(
            curve_circle() | store_named_attribute("res", spline_resolution(), data_type="INT")
        ))
        _assert_valid_python(src)
        assert "GeometryNodeInputSplineResolution" in src

    def test_curve_handle_positions_compile(self):
        src = _compile_model("chp", lambda: output(
            curve_circle() | store_named_attribute(
                "left_handle", curve_handle_positions(relative=True, output="Left"),
                data_type="FLOAT_VECTOR",
            )
        ))
        _assert_valid_python(src)
        assert "GeometryNodeInputCurveHandlePositions" in src
        assert "Relative" in src

    def test_endpoint_selection_compile(self):
        src = _compile_model("ep", lambda: output(
            curve_circle() | store_named_attribute(
                "ends", endpoint_selection(start_size=2, end_size=2),
                data_type="BOOLEAN",
            )
        ))
        _assert_valid_python(src)
        assert "GeometryNodeCurveEndpointSelection" in src
        assert "Start Size" in src

    def test_handle_type_selection_compile(self):
        src = _compile_model("hts", lambda: output(
            curve_circle() | store_named_attribute(
                "sel", handle_type_selection(handle_type="AUTO"),
                data_type="BOOLEAN",
            )
        ))
        _assert_valid_python(src)
        assert "GeometryNodeCurveHandleTypeSelection" in src
        assert "handle_type" in src

    def test_spline_length_compile(self):
        src = _compile_model("sl", lambda: output(
            curve_circle() | store_named_attribute("len", spline_length())
        ))
        _assert_valid_python(src)
        assert "GeometryNodeSplineLength" in src

    def test_spline_parameter_compile(self):
        src = _compile_model("sp", lambda: output(
            curve_circle() | store_named_attribute("fac", spline_parameter())
        ))
        _assert_valid_python(src)
        assert "GeometryNodeSplineParameter" in src

    def test_curve_of_point_compile(self):
        src = _compile_model("cop", lambda: output(
            curve_circle() | store_named_attribute("ci", curve_of_point(), data_type="INT")
        ))
        _assert_valid_python(src)
        assert "GeometryNodeCurveOfPoint" in src

    def test_offset_point_in_curve_compile(self):
        src = _compile_model("opic", lambda: output(
            curve_circle() | store_named_attribute(
                "opi", offset_point_in_curve(offset=1, output="Point Index"),
                data_type="INT",
            )
        ))
        _assert_valid_python(src)
        assert "GeometryNodeOffsetPointInCurve" in src
        assert "Offset" in src

    def test_points_of_curve_compile(self):
        src = _compile_model("poc", lambda: output(
            curve_circle() | store_named_attribute(
                "poc", points_of_curve(curve_index=0),
                data_type="INT",
            )
        ))
        _assert_valid_python(src)
        assert "GeometryNodePointsOfCurve" in src

    def test_shortest_edge_paths_compile(self):
        src = _compile_model("sep_b17", lambda: output(
            cube(1, 1, 1) | store_named_attribute(
                "cost", shortest_edge_paths(end_vertex=True, edge_cost=1.5, output="Total Cost"),
            )
        ))
        _assert_valid_python(src)
        assert "GeometryNodeInputShortestEdgePaths" in src
        assert "Edge Cost" in src

    def test_instance_rotation_compile(self):
        src = _compile_model("ir_b17", lambda: output(
            cube(1, 1, 1) | store_named_attribute(
                "rot", instance_rotation(), data_type="FLOAT_VECTOR",
            )
        ))
        _assert_valid_python(src)
        assert "GeometryNodeInputInstanceRotation" in src

    def test_instance_scale_compile(self):
        src = _compile_model("is_b17", lambda: output(
            cube(1, 1, 1) | store_named_attribute(
                "scl", instance_scale(), data_type="FLOAT_VECTOR",
            )
        ))
        _assert_valid_python(src)
        assert "GeometryNodeInputInstanceScale" in src

    def test_material_index_compile(self):
        src = _compile_model("mi", lambda: output(
            cube(1, 1, 1) | store_named_attribute(
                "mat_idx", material_index(), data_type="INT",
            )
        ))
        _assert_valid_python(src)
        assert "GeometryNodeInputMaterialIndex" in src

    def test_input_defaults_in_output(self):
        """Verify that input_defaults generate default_value assignments."""
        src = _compile_model("id_test", lambda: output(
            cube(1, 1, 1) | store_named_attribute(
                "planar", is_face_planar(threshold=0.05), data_type="BOOLEAN",
            )
        ))
        _assert_valid_python(src)
        assert "default_value = 0.05" in src


# ===========================================================================
# Batch 18 — Topology, Scene, Instance, Material, Selection field nodes
# ===========================================================================


from tanuki.dsl import (
    material_selection,
    input_material,
    scene_time,
    active_camera,
    self_object,
    is_viewport,
    instance_bounds,
    named_layer_selection,
    face_group_boundaries,
    corners_of_edge,
    corners_of_face,
    corners_of_vertex,
    edges_of_corner,
    edges_of_vertex,
    face_of_corner,
    vertex_of_corner,
    offset_corner_in_face,
    index_of_nearest,
    edge_paths_to_selection,
    edges_to_face_groups,
)


class TestBatch18FieldInputIR:
    """IR-level tests for batch 18 field input nodes."""

    def test_scene_time_default(self):
        n = scene_time()
        assert isinstance(n, IRFieldInput)
        assert n.field_type == "GeometryNodeInputSceneTime"
        assert n.output_socket == "Seconds"

    def test_scene_time_frame(self):
        n = scene_time(output="Frame")
        assert n.output_socket == "Frame"

    def test_active_camera(self):
        n = active_camera()
        assert isinstance(n, IRFieldInput)
        assert n.field_type == "GeometryNodeInputActiveCamera"
        assert n.output_socket == "Active Camera"

    def test_self_object(self):
        n = self_object()
        assert isinstance(n, IRFieldInput)
        assert n.field_type == "GeometryNodeSelfObject"
        assert n.output_socket == "Self Object"

    def test_is_viewport(self):
        n = is_viewport()
        assert isinstance(n, IRFieldInput)
        assert n.field_type == "GeometryNodeIsViewport"
        assert n.output_socket == "Is Viewport"

    def test_instance_bounds_default(self):
        n = instance_bounds()
        assert isinstance(n, IRFieldInput)
        assert n.field_type == "GeometryNodeInputInstanceBounds"
        assert n.output_socket == "Min"
        assert n.input_defaults == {"Use Radius": True}

    def test_instance_bounds_max(self):
        n = instance_bounds(use_radius=False, output="Max")
        assert n.output_socket == "Max"
        assert n.input_defaults == {"Use Radius": False}

    def test_named_layer_selection(self):
        n = named_layer_selection(name="Layer_1")
        assert isinstance(n, IRFieldInput)
        assert n.field_type == "GeometryNodeInputNamedLayerSelection"
        assert n.input_defaults == {"Name": "Layer_1"}

    def test_face_group_boundaries(self):
        n = face_group_boundaries(face_group_id=5)
        assert isinstance(n, IRFieldInput)
        assert n.field_type == "GeometryNodeMeshFaceSetBoundaries"
        assert n.output_socket == "Boundary Edges"
        assert n.input_defaults == {"Face Set": 5}

    def test_material_selection(self):
        n = material_selection(material="Wood")
        assert isinstance(n, IRFieldInput)
        assert n.field_type == "GeometryNodeMaterialSelection"
        assert n.output_socket == "Selection"
        assert n.input_defaults == {"Material": ("MATERIAL", "Wood")}

    def test_input_material(self):
        n = input_material(material="Metal")
        assert isinstance(n, IRFieldInput)
        assert n.field_type == "GeometryNodeInputMaterial"
        assert n.properties == {"material": ("MATERIAL", "Metal")}

    def test_corners_of_edge(self):
        n = corners_of_edge(edge_index=3, output="Total")
        assert isinstance(n, IRFieldInput)
        assert n.field_type == "GeometryNodeCornersOfEdge"
        assert n.output_socket == "Total"
        assert n.input_defaults["Edge Index"] == 3

    def test_corners_of_face(self):
        n = corners_of_face(face_index=1, output="Total")
        assert isinstance(n, IRFieldInput)
        assert n.field_type == "GeometryNodeCornersOfFace"
        assert n.output_socket == "Total"
        assert n.input_defaults["Face Index"] == 1

    def test_corners_of_vertex(self):
        n = corners_of_vertex(vertex_index=2, weights=1.0)
        assert isinstance(n, IRFieldInput)
        assert n.field_type == "GeometryNodeCornersOfVertex"
        assert n.input_defaults["Vertex Index"] == 2
        assert n.input_defaults["Weights"] == 1.0

    def test_edges_of_corner(self):
        n = edges_of_corner(corner_index=0, output="Previous Edge Index")
        assert isinstance(n, IRFieldInput)
        assert n.field_type == "GeometryNodeEdgesOfCorner"
        assert n.output_socket == "Previous Edge Index"

    def test_edges_of_vertex(self):
        n = edges_of_vertex(vertex_index=4, output="Total")
        assert isinstance(n, IRFieldInput)
        assert n.field_type == "GeometryNodeEdgesOfVertex"
        assert n.output_socket == "Total"

    def test_face_of_corner(self):
        n = face_of_corner(corner_index=1, output="Index in Face")
        assert isinstance(n, IRFieldInput)
        assert n.field_type == "GeometryNodeFaceOfCorner"
        assert n.output_socket == "Index in Face"

    def test_vertex_of_corner(self):
        n = vertex_of_corner(corner_index=3)
        assert isinstance(n, IRFieldInput)
        assert n.field_type == "GeometryNodeVertexOfCorner"
        assert n.output_socket == "Vertex Index"
        assert n.input_defaults == {"Corner Index": 3}

    def test_offset_corner_in_face(self):
        n = offset_corner_in_face(corner_index=0, offset=2)
        assert isinstance(n, IRFieldInput)
        assert n.field_type == "GeometryNodeOffsetCornerInFace"
        assert n.input_defaults == {"Corner Index": 0, "Offset": 2}

    def test_index_of_nearest(self):
        n = index_of_nearest()
        assert isinstance(n, IRFieldInput)
        assert n.field_type == "GeometryNodeIndexOfNearest"
        assert n.output_socket == "Index"

    def test_index_of_nearest_has_neighbor(self):
        n = index_of_nearest(output="Has Neighbor")
        assert n.output_socket == "Has Neighbor"

    def test_edge_paths_to_selection(self):
        n = edge_paths_to_selection(start_vertices=False, next_vertex_index=5)
        assert isinstance(n, IRFieldInput)
        assert n.field_type == "GeometryNodeEdgePathsToSelection"
        assert n.output_socket == "Selection"
        assert n.input_defaults == {"Start Vertices": False, "Next Vertex Index": 5}

    def test_edges_to_face_groups(self):
        n = edges_to_face_groups(boundary_edges=False)
        assert isinstance(n, IRFieldInput)
        assert n.field_type == "GeometryNodeEdgesToFaceGroups"
        assert n.output_socket == "Face Group ID"
        assert n.input_defaults == {"Boundary Edges": False}


class TestBatch18Compile:
    """Compiler tests for batch 18 field input nodes."""

    def test_scene_time_compile(self):
        src = _compile_model("st", lambda: output(
            cube(1, 1, 1) | store_named_attribute("t", scene_time())
        ))
        _assert_valid_python(src)
        assert "GeometryNodeInputSceneTime" in src

    def test_active_camera_compile(self):
        src = _compile_model("ac", lambda: output(
            cube(1, 1, 1) | store_named_attribute("cam", active_camera())
        ))
        _assert_valid_python(src)
        assert "GeometryNodeInputActiveCamera" in src

    def test_self_object_compile(self):
        src = _compile_model("so", lambda: output(
            cube(1, 1, 1) | store_named_attribute("self", self_object())
        ))
        _assert_valid_python(src)
        assert "GeometryNodeSelfObject" in src

    def test_is_viewport_compile(self):
        src = _compile_model("vp", lambda: output(
            cube(1, 1, 1) | store_named_attribute("vp", is_viewport(), data_type="BOOLEAN")
        ))
        _assert_valid_python(src)
        assert "GeometryNodeIsViewport" in src

    def test_instance_bounds_compile(self):
        src = _compile_model("ib", lambda: output(
            cube(1, 1, 1) | store_named_attribute(
                "bmin", instance_bounds(output="Min"), data_type="FLOAT_VECTOR",
            )
        ))
        _assert_valid_python(src)
        assert "GeometryNodeInputInstanceBounds" in src

    def test_named_layer_selection_compile(self):
        src = _compile_model("nls", lambda: output(
            cube(1, 1, 1) | store_named_attribute(
                "sel", named_layer_selection(name="Outline"), data_type="BOOLEAN",
            )
        ))
        _assert_valid_python(src)
        assert "GeometryNodeInputNamedLayerSelection" in src
        assert "Outline" in src

    def test_face_group_boundaries_compile(self):
        src = _compile_model("fgb", lambda: output(
            cube(1, 1, 1) | store_named_attribute(
                "bnd", face_group_boundaries(face_group_id=1), data_type="BOOLEAN",
            )
        ))
        _assert_valid_python(src)
        assert "GeometryNodeMeshFaceSetBoundaries" in src

    def test_material_selection_compile(self):
        src = _compile_model("ms", lambda: output(
            cube(1, 1, 1) | store_named_attribute(
                "sel", material_selection(material="Wood"), data_type="BOOLEAN",
            )
        ))
        _assert_valid_python(src)
        assert "GeometryNodeMaterialSelection" in src
        assert "bpy.data.materials.get" in src
        assert "'Wood'" in src

    def test_input_material_compile(self):
        src = _compile_model("im", lambda: output(
            cube(1, 1, 1) | store_named_attribute(
                "mat", input_material(material="Metal"),
            )
        ))
        _assert_valid_python(src)
        assert "GeometryNodeInputMaterial" in src
        assert "bpy.data.materials.get" in src
        assert "'Metal'" in src

    def test_corners_of_edge_compile(self):
        src = _compile_model("coe", lambda: output(
            cube(1, 1, 1) | store_named_attribute(
                "ci", corners_of_edge(), data_type="INT",
            )
        ))
        _assert_valid_python(src)
        assert "GeometryNodeCornersOfEdge" in src

    def test_corners_of_face_compile(self):
        src = _compile_model("cof", lambda: output(
            cube(1, 1, 1) | store_named_attribute(
                "ci", corners_of_face(), data_type="INT",
            )
        ))
        _assert_valid_python(src)
        assert "GeometryNodeCornersOfFace" in src

    def test_corners_of_vertex_compile(self):
        src = _compile_model("cov", lambda: output(
            cube(1, 1, 1) | store_named_attribute(
                "ci", corners_of_vertex(), data_type="INT",
            )
        ))
        _assert_valid_python(src)
        assert "GeometryNodeCornersOfVertex" in src

    def test_edges_of_corner_compile(self):
        src = _compile_model("eoc", lambda: output(
            cube(1, 1, 1) | store_named_attribute(
                "ei", edges_of_corner(), data_type="INT",
            )
        ))
        _assert_valid_python(src)
        assert "GeometryNodeEdgesOfCorner" in src

    def test_edges_of_vertex_compile(self):
        src = _compile_model("eov", lambda: output(
            cube(1, 1, 1) | store_named_attribute(
                "ei", edges_of_vertex(), data_type="INT",
            )
        ))
        _assert_valid_python(src)
        assert "GeometryNodeEdgesOfVertex" in src

    def test_face_of_corner_compile(self):
        src = _compile_model("foc", lambda: output(
            cube(1, 1, 1) | store_named_attribute(
                "fi", face_of_corner(), data_type="INT",
            )
        ))
        _assert_valid_python(src)
        assert "GeometryNodeFaceOfCorner" in src

    def test_vertex_of_corner_compile(self):
        src = _compile_model("voc", lambda: output(
            cube(1, 1, 1) | store_named_attribute(
                "vi", vertex_of_corner(), data_type="INT",
            )
        ))
        _assert_valid_python(src)
        assert "GeometryNodeVertexOfCorner" in src

    def test_offset_corner_in_face_compile(self):
        src = _compile_model("ocif", lambda: output(
            cube(1, 1, 1) | store_named_attribute(
                "ci", offset_corner_in_face(offset=1), data_type="INT",
            )
        ))
        _assert_valid_python(src)
        assert "GeometryNodeOffsetCornerInFace" in src

    def test_index_of_nearest_compile(self):
        src = _compile_model("ion", lambda: output(
            cube(1, 1, 1) | store_named_attribute(
                "ni", index_of_nearest(), data_type="INT",
            )
        ))
        _assert_valid_python(src)
        assert "GeometryNodeIndexOfNearest" in src

    def test_edge_paths_to_selection_compile(self):
        src = _compile_model("epts", lambda: output(
            cube(1, 1, 1) | store_named_attribute(
                "sel", edge_paths_to_selection(), data_type="BOOLEAN",
            )
        ))
        _assert_valid_python(src)
        assert "GeometryNodeEdgePathsToSelection" in src

    def test_edges_to_face_groups_compile(self):
        src = _compile_model("etfg", lambda: output(
            cube(1, 1, 1) | store_named_attribute(
                "gid", edges_to_face_groups(), data_type="INT",
            )
        ))
        _assert_valid_python(src)
        assert "GeometryNodeEdgesToFaceGroups" in src


# ===========================================================================
# Batch 19 — Instance, Viewport, Tool, Reference, Stats, UV, Utility nodes
# ===========================================================================


from tanuki.dsl import (
    instance_transform,
    viewport_transform,
    tool_selection,
    tool_face_set,
    tool_mouse_position,
    tool_3d_cursor,
    tool_active_element,
    input_collection,
    input_image,
    input_object,
    camera_info,
    image_texture,
    image_info,
    field_average,
    field_min_max,
    field_variance,
    uv_pack_islands,
    uv_unwrap,
    join_strings,
    import_text,
)


class TestBatch19FieldInputIR:
    """IR-level tests for batch 19 field input nodes."""

    # --- Simple field inputs (no inputs) ---

    def test_instance_transform(self):
        n = instance_transform()
        assert isinstance(n, IRFieldInput)
        assert n.field_type == "GeometryNodeInstanceTransform"
        assert n.output_socket == "Transform"

    def test_viewport_transform_default(self):
        n = viewport_transform()
        assert n.field_type == "GeometryNodeViewportTransform"
        assert n.output_socket == "Projection"

    def test_viewport_transform_view(self):
        n = viewport_transform(output="View")
        assert n.output_socket == "View"

    def test_tool_selection_default(self):
        n = tool_selection()
        assert n.field_type == "GeometryNodeToolSelection"
        assert n.output_socket == "Boolean"

    def test_tool_selection_float(self):
        n = tool_selection(output="Float")
        assert n.output_socket == "Float"

    def test_tool_face_set(self):
        n = tool_face_set()
        assert n.field_type == "GeometryNodeToolFaceSet"
        assert n.output_socket == "Face Set"

    def test_tool_face_set_exists(self):
        n = tool_face_set(output="Exists")
        assert n.output_socket == "Exists"

    def test_tool_mouse_position(self):
        n = tool_mouse_position()
        assert n.field_type == "GeometryNodeToolMousePosition"
        assert n.output_socket == "Mouse X"

    def test_tool_mouse_position_region(self):
        n = tool_mouse_position(output="Region Width")
        assert n.output_socket == "Region Width"

    def test_tool_3d_cursor(self):
        n = tool_3d_cursor()
        assert n.field_type == "GeometryNodeTool3DCursor"
        assert n.output_socket == "Location"

    def test_tool_3d_cursor_rotation(self):
        n = tool_3d_cursor(output="Rotation")
        assert n.output_socket == "Rotation"

    def test_tool_active_element(self):
        n = tool_active_element(domain="FACE", output="Exists")
        assert n.field_type == "GeometryNodeToolActiveElement"
        assert n.output_socket == "Exists"
        assert n.properties == {"domain": "FACE"}

    # --- Reference input nodes ---

    def test_input_collection(self):
        n = input_collection(collection="MyCol")
        assert n.field_type == "GeometryNodeInputCollection"
        assert n.output_socket == "Collection"
        assert n.properties == {"collection": ("COLLECTION", "MyCol")}

    def test_input_collection_empty(self):
        n = input_collection()
        assert n.properties == {}

    def test_input_image(self):
        n = input_image(image="tex.png")
        assert n.field_type == "GeometryNodeInputImage"
        assert n.properties == {"image": ("IMAGE", "tex.png")}

    def test_input_object(self):
        n = input_object(object_name="Cube")
        assert n.field_type == "GeometryNodeInputObject"
        assert n.properties == {"object": ("OBJECT", "Cube")}

    # --- Nodes with inputs + properties ---

    def test_camera_info_default(self):
        n = camera_info()
        assert n.field_type == "GeometryNodeCameraInfo"
        assert n.output_socket == "Focal Length"
        assert n.input_defaults == {}

    def test_camera_info_with_camera(self):
        n = camera_info(camera="Camera", output="Sensor")
        assert n.output_socket == "Sensor"
        assert n.input_defaults == {"Camera": ("OBJECT", "Camera")}

    def test_image_texture_default(self):
        n = image_texture()
        assert n.field_type == "GeometryNodeImageTexture"
        assert n.output_socket == "Color"
        assert n.properties == {"interpolation": "Linear", "extension": "REPEAT"}

    def test_image_texture_with_image(self):
        n = image_texture(image="photo.png", output="Alpha")
        assert n.output_socket == "Alpha"
        assert n.input_defaults == {"Image": ("IMAGE", "photo.png")}

    def test_image_info(self):
        n = image_info(image="tex.png", frame=5, output="Height")
        assert n.field_type == "GeometryNodeImageInfo"
        assert n.output_socket == "Height"
        assert n.input_defaults["Frame"] == 5
        assert n.input_defaults["Image"] == ("IMAGE", "tex.png")

    # --- Field statistics ---

    def test_field_average(self):
        n = field_average(group_id=1, data_type="INT", domain="FACE", output="Median")
        assert n.field_type == "GeometryNodeFieldAverage"
        assert n.output_socket == "Median"
        assert n.properties == {"data_type": "INT", "domain": "FACE"}
        assert n.input_defaults == {"Group ID": 1}

    def test_field_min_max(self):
        n = field_min_max(output="Max")
        assert n.field_type == "GeometryNodeFieldMinAndMax"
        assert n.output_socket == "Max"

    def test_field_variance(self):
        n = field_variance(output="Variance")
        assert n.field_type == "GeometryNodeFieldVariance"
        assert n.output_socket == "Variance"

    # --- UV ---

    def test_uv_pack_islands(self):
        n = uv_pack_islands(margin=0.01, rotate=False)
        assert n.field_type == "GeometryNodeUVPackIslands"
        assert n.output_socket == "UV"
        assert n.input_defaults == {"Margin": 0.01, "Rotate": False}

    def test_uv_unwrap(self):
        n = uv_unwrap(method="CONFORMAL", margin=0.005)
        assert n.field_type == "GeometryNodeUVUnwrap"
        assert n.properties == {"method": "CONFORMAL"}
        assert n.input_defaults["Margin"] == 0.005

    # --- String / utility ---

    def test_join_strings(self):
        n = join_strings(delimiter=", ")
        assert n.field_type == "GeometryNodeStringJoin"
        assert n.output_socket == "String"
        assert n.input_defaults == {"Delimiter": ", "}

    def test_import_text(self):
        n = import_text(path="/tmp/data.txt")
        assert n.field_type == "GeometryNodeImportText"
        assert n.input_defaults == {"Path": "/tmp/data.txt"}


class TestBatch19Compile:
    """Compiler tests for batch 19 field input nodes."""

    def test_instance_transform_compile(self):
        src = _compile_model("it", lambda: output(
            cube(1, 1, 1) | store_named_attribute("t", instance_transform())
        ))
        _assert_valid_python(src)
        assert "GeometryNodeInstanceTransform" in src

    def test_viewport_transform_compile(self):
        src = _compile_model("vt", lambda: output(
            cube(1, 1, 1) | store_named_attribute(
                "proj", viewport_transform(), data_type="FLOAT_VECTOR",
            )
        ))
        _assert_valid_python(src)
        assert "GeometryNodeViewportTransform" in src

    def test_tool_selection_compile(self):
        src = _compile_model("ts", lambda: output(
            cube(1, 1, 1) | store_named_attribute(
                "sel", tool_selection(), data_type="BOOLEAN",
            )
        ))
        _assert_valid_python(src)
        assert "GeometryNodeToolSelection" in src

    def test_tool_face_set_compile(self):
        src = _compile_model("tfs", lambda: output(
            cube(1, 1, 1) | store_named_attribute(
                "fs", tool_face_set(), data_type="INT",
            )
        ))
        _assert_valid_python(src)
        assert "GeometryNodeToolFaceSet" in src

    def test_tool_mouse_position_compile(self):
        src = _compile_model("tmp", lambda: output(
            cube(1, 1, 1) | store_named_attribute(
                "mx", tool_mouse_position(), data_type="INT",
            )
        ))
        _assert_valid_python(src)
        assert "GeometryNodeToolMousePosition" in src

    def test_tool_3d_cursor_compile(self):
        src = _compile_model("tc", lambda: output(
            cube(1, 1, 1) | store_named_attribute(
                "loc", tool_3d_cursor(), data_type="FLOAT_VECTOR",
            )
        ))
        _assert_valid_python(src)
        assert "GeometryNodeTool3DCursor" in src

    def test_tool_active_element_compile(self):
        src = _compile_model("tae", lambda: output(
            cube(1, 1, 1) | store_named_attribute(
                "idx", tool_active_element(domain="EDGE"), data_type="INT",
            )
        ))
        _assert_valid_python(src)
        assert "GeometryNodeToolActiveElement" in src
        assert '"EDGE"' in src

    def test_input_collection_compile(self):
        src = _compile_model("ic", lambda: output(
            cube(1, 1, 1) | store_named_attribute(
                "col", input_collection(collection="Env"),
            )
        ))
        _assert_valid_python(src)
        assert "GeometryNodeInputCollection" in src
        assert "bpy.data.collections.get" in src
        assert "'Env'" in src

    def test_input_image_compile(self):
        src = _compile_model("ii", lambda: output(
            cube(1, 1, 1) | store_named_attribute(
                "img", input_image(image="photo.png"),
            )
        ))
        _assert_valid_python(src)
        assert "GeometryNodeInputImage" in src
        assert "bpy.data.images.get" in src
        assert "'photo.png'" in src

    def test_input_object_compile(self):
        src = _compile_model("io", lambda: output(
            cube(1, 1, 1) | store_named_attribute(
                "obj", input_object(object_name="Empty"),
            )
        ))
        _assert_valid_python(src)
        assert "GeometryNodeInputObject" in src
        assert "bpy.data.objects.get" in src
        assert "'Empty'" in src

    def test_camera_info_compile(self):
        src = _compile_model("ci", lambda: output(
            cube(1, 1, 1) | store_named_attribute(
                "fl", camera_info(camera="Camera"),
            )
        ))
        _assert_valid_python(src)
        assert "GeometryNodeCameraInfo" in src
        assert "bpy.data.objects.get" in src

    def test_image_texture_compile(self):
        src = _compile_model("it2", lambda: output(
            cube(1, 1, 1) | store_named_attribute(
                "col", image_texture(image="tex.png"),
            )
        ))
        _assert_valid_python(src)
        assert "GeometryNodeImageTexture" in src
        assert "bpy.data.images.get" in src

    def test_image_info_compile(self):
        src = _compile_model("imi", lambda: output(
            cube(1, 1, 1) | store_named_attribute(
                "w", image_info(image="tex.png"), data_type="INT",
            )
        ))
        _assert_valid_python(src)
        assert "GeometryNodeImageInfo" in src
        assert "bpy.data.images.get" in src

    def test_field_average_compile(self):
        src = _compile_model("fa", lambda: output(
            cube(1, 1, 1) | store_named_attribute(
                "avg", field_average(),
            )
        ))
        _assert_valid_python(src)
        assert "GeometryNodeFieldAverage" in src

    def test_field_min_max_compile(self):
        src = _compile_model("fmm", lambda: output(
            cube(1, 1, 1) | store_named_attribute(
                "mn", field_min_max(),
            )
        ))
        _assert_valid_python(src)
        assert "GeometryNodeFieldMinAndMax" in src

    def test_field_variance_compile(self):
        src = _compile_model("fv", lambda: output(
            cube(1, 1, 1) | store_named_attribute(
                "sd", field_variance(),
            )
        ))
        _assert_valid_python(src)
        assert "GeometryNodeFieldVariance" in src

    def test_uv_pack_islands_compile(self):
        src = _compile_model("upi", lambda: output(
            cube(1, 1, 1) | store_named_attribute(
                "uv", uv_pack_islands(), data_type="FLOAT_VECTOR",
            )
        ))
        _assert_valid_python(src)
        assert "GeometryNodeUVPackIslands" in src

    def test_uv_unwrap_compile(self):
        src = _compile_model("uu", lambda: output(
            cube(1, 1, 1) | store_named_attribute(
                "uv", uv_unwrap(method="CONFORMAL"), data_type="FLOAT_VECTOR",
            )
        ))
        _assert_valid_python(src)
        assert "GeometryNodeUVUnwrap" in src
        assert '"CONFORMAL"' in src

    def test_join_strings_compile(self):
        src = _compile_model("js", lambda: output(
            cube(1, 1, 1) | store_named_attribute(
                "s", join_strings(delimiter="-"),
            )
        ))
        _assert_valid_python(src)
        assert "GeometryNodeStringJoin" in src

    def test_import_text_compile(self):
        src = _compile_model("imt", lambda: output(
            cube(1, 1, 1) | store_named_attribute(
                "txt", import_text(path="/tmp/data.txt"),
            )
        ))
        _assert_valid_python(src)
        assert "GeometryNodeImportText" in src
        assert "/tmp/data.txt" in src


# ===========================================================================
# Batch 20 — field processors, grid ops, gizmos, warning, set_instance_transform
# ===========================================================================

from tanuki.dsl import (
    blur_attribute,
    accumulate_field,
    evaluate_at_index,
    evaluate_on_domain,
    grid_info,
    sample_grid,
    sample_grid_index,
    sdf_grid_boolean,
    warning_node,
    gizmo_dial,
    gizmo_linear,
    gizmo_transform,
    distribute_points_in_grid,
    grid_to_mesh,
    points_to_sdf_grid,
    set_instance_transform,
)


class TestBatch20FieldInputIR:
    """IR-level tests for batch 20 field input nodes."""

    def test_blur_attribute_default(self):
        n = blur_attribute()
        assert isinstance(n, IRFieldInput)
        assert n.field_type == "GeometryNodeBlurAttribute"
        assert n.output_socket == "Value"
        assert n.input_defaults["Iterations"] == 1

    def test_blur_attribute_custom(self):
        n = blur_attribute(value=1.0, iterations=5, weight=0.5, data_type="FLOAT_VECTOR")
        assert n.properties["data_type"] == "FLOAT_VECTOR"
        assert n.input_defaults["Value"] == 1.0
        assert n.input_defaults["Iterations"] == 5
        assert n.input_defaults["Weight"] == 0.5

    def test_accumulate_field_default(self):
        n = accumulate_field()
        assert isinstance(n, IRFieldInput)
        assert n.field_type == "GeometryNodeAccumulateField"
        assert n.output_socket == "Leading"

    def test_accumulate_field_trailing(self):
        n = accumulate_field(output="Trailing", domain="FACE")
        assert n.output_socket == "Trailing"
        assert n.properties["domain"] == "FACE"

    def test_accumulate_field_total(self):
        n = accumulate_field(output="Total", data_type="INT")
        assert n.output_socket == "Total"
        assert n.properties["data_type"] == "INT"

    def test_evaluate_at_index_default(self):
        n = evaluate_at_index()
        assert isinstance(n, IRFieldInput)
        assert n.field_type == "GeometryNodeFieldAtIndex"
        assert n.output_socket == "Value"
        assert n.input_defaults["Index"] == 0

    def test_evaluate_at_index_custom(self):
        n = evaluate_at_index(value=2.5, index=10, domain="FACE", data_type="FLOAT_VECTOR")
        assert n.properties["domain"] == "FACE"
        assert n.properties["data_type"] == "FLOAT_VECTOR"
        assert n.input_defaults["Index"] == 10

    def test_evaluate_on_domain_default(self):
        n = evaluate_on_domain()
        assert isinstance(n, IRFieldInput)
        assert n.field_type == "GeometryNodeFieldOnDomain"
        assert n.output_socket == "Value"

    def test_evaluate_on_domain_custom(self):
        n = evaluate_on_domain(domain="EDGE", data_type="INT")
        assert n.properties["domain"] == "EDGE"
        assert n.properties["data_type"] == "INT"

    def test_grid_info_default(self):
        n = grid_info()
        assert isinstance(n, IRFieldInput)
        assert n.field_type == "GeometryNodeGridInfo"
        assert n.output_socket == "Transform"

    def test_grid_info_background(self):
        n = grid_info(output="Background Value")
        assert n.output_socket == "Background Value"

    def test_sample_grid_default(self):
        n = sample_grid()
        assert isinstance(n, IRFieldInput)
        assert n.field_type == "GeometryNodeSampleGrid"
        assert n.properties["interpolation_mode"] == "TRILINEAR"

    def test_sample_grid_nearest(self):
        n = sample_grid(interpolation_mode="NEAREST", data_type="INT")
        assert n.properties["interpolation_mode"] == "NEAREST"
        assert n.properties["data_type"] == "INT"

    def test_sample_grid_index_default(self):
        n = sample_grid_index()
        assert isinstance(n, IRFieldInput)
        assert n.field_type == "GeometryNodeSampleGridIndex"
        assert n.input_defaults["X"] == 0

    def test_sample_grid_index_custom(self):
        n = sample_grid_index(x=3, y=4, z=5, data_type="BOOLEAN")
        assert n.input_defaults["X"] == 3
        assert n.input_defaults["Y"] == 4
        assert n.input_defaults["Z"] == 5

    def test_sdf_grid_boolean_default(self):
        n = sdf_grid_boolean()
        assert isinstance(n, IRFieldInput)
        assert n.field_type == "GeometryNodeSDFGridBoolean"
        assert n.properties["operation"] == "DIFFERENCE"

    def test_sdf_grid_boolean_union(self):
        n = sdf_grid_boolean(operation="UNION")
        assert n.properties["operation"] == "UNION"

    def test_warning_node_default(self):
        n = warning_node()
        assert isinstance(n, IRFieldInput)
        assert n.field_type == "GeometryNodeWarning"
        assert n.properties["warning_type"] == "ERROR"
        assert n.input_defaults["Show"] is True

    def test_warning_node_custom(self):
        n = warning_node(show=False, message="test", warning_type="INFO")
        assert n.properties["warning_type"] == "INFO"
        assert n.input_defaults["Message"] == "test"
        assert n.input_defaults["Show"] is False

    def test_gizmo_dial_default(self):
        n = gizmo_dial()
        assert isinstance(n, IRFieldInput)
        assert n.field_type == "GeometryNodeGizmoDial"
        assert n.output_socket == "Transform"
        assert n.properties["color_id"] == "PRIMARY"

    def test_gizmo_dial_custom(self):
        n = gizmo_dial(color_id="X", radius=2.0, value=1.5)
        assert n.properties["color_id"] == "X"
        assert n.input_defaults["Radius"] == 2.0
        assert n.input_defaults["Value"] == 1.5

    def test_gizmo_linear_default(self):
        n = gizmo_linear()
        assert isinstance(n, IRFieldInput)
        assert n.field_type == "GeometryNodeGizmoLinear"
        assert n.properties["draw_style"] == "ARROW"

    def test_gizmo_linear_custom(self):
        n = gizmo_linear(color_id="Y", draw_style="CROSS")
        assert n.properties["color_id"] == "Y"
        assert n.properties["draw_style"] == "CROSS"

    def test_gizmo_transform_default(self):
        n = gizmo_transform()
        assert isinstance(n, IRFieldInput)
        assert n.field_type == "GeometryNodeGizmoTransform"
        assert n.output_socket == "Transform"
        assert n.properties["use_translation_x"] is False

    def test_gizmo_transform_custom(self):
        n = gizmo_transform(
            use_translation_x=True, use_translation_y=True, use_translation_z=True,
            use_rotation_x=True,
        )
        assert n.properties["use_translation_x"] is True
        assert n.properties["use_rotation_x"] is True
        assert n.properties["use_scale_x"] is False


class TestBatch20GeometryOpIR:
    """IR-level tests for batch 20 geometry op nodes."""

    def test_distribute_points_in_grid(self):
        op = distribute_points_in_grid()
        node = op(cube(1, 1, 1))
        assert isinstance(node, IRGeometryOp)
        assert node.op_type == "GeometryNodeDistributePointsInGrid"
        assert node.properties["mode"] == "DENSITY_RANDOM"

    def test_distribute_points_in_grid_custom(self):
        op = distribute_points_in_grid(density=2.0, seed=42, mode="DENSITY_GRID")
        node = op(cube(1, 1, 1))
        assert node.properties["density"] == 2.0
        assert node.properties["seed"] == 42
        assert node.properties["mode"] == "DENSITY_GRID"

    def test_grid_to_mesh(self):
        op = grid_to_mesh()
        node = op(cube(1, 1, 1))
        assert isinstance(node, IRGeometryOp)
        assert node.op_type == "GeometryNodeGridToMesh"
        assert node.properties["threshold"] == 0.1

    def test_grid_to_mesh_custom(self):
        op = grid_to_mesh(threshold=0.5, adaptivity=1.0)
        node = op(cube(1, 1, 1))
        assert node.properties["threshold"] == 0.5
        assert node.properties["adaptivity"] == 1.0

    def test_points_to_sdf_grid(self):
        op = points_to_sdf_grid()
        node = op(cube(1, 1, 1))
        assert isinstance(node, IRGeometryOp)
        assert node.op_type == "GeometryNodePointsToSDFGrid"
        assert node.properties["radius"] == 0.5

    def test_points_to_sdf_grid_custom(self):
        op = points_to_sdf_grid(radius=1.0, voxel_size=0.5)
        node = op(cube(1, 1, 1))
        assert node.properties["radius"] == 1.0
        assert node.properties["voxel_size"] == 0.5

    def test_set_instance_transform(self):
        op = set_instance_transform()
        node = op(cube(1, 1, 1))
        assert isinstance(node, IRGeometryOp)
        assert node.op_type == "GeometryNodeSetInstanceTransform"


class TestBatch20Compile:
    """Compilation tests for batch 20 nodes."""

    def test_blur_attribute_compile(self):
        src = _compile_model("ba", lambda: output(
            cube(1, 1, 1) | store_named_attribute(
                "blurred", blur_attribute(iterations=3),
            )
        ))
        _assert_valid_python(src)
        assert "GeometryNodeBlurAttribute" in src

    def test_accumulate_field_compile(self):
        src = _compile_model("af", lambda: output(
            cube(1, 1, 1) | store_named_attribute(
                "acc", accumulate_field(domain="FACE", output="Total"),
            )
        ))
        _assert_valid_python(src)
        assert "GeometryNodeAccumulateField" in src
        assert '"FACE"' in src

    def test_evaluate_at_index_compile(self):
        src = _compile_model("eai", lambda: output(
            cube(1, 1, 1) | store_named_attribute(
                "val", evaluate_at_index(index=5),
            )
        ))
        _assert_valid_python(src)
        assert "GeometryNodeFieldAtIndex" in src

    def test_evaluate_on_domain_compile(self):
        src = _compile_model("eod", lambda: output(
            cube(1, 1, 1) | store_named_attribute(
                "val", evaluate_on_domain(domain="EDGE"),
            )
        ))
        _assert_valid_python(src)
        assert "GeometryNodeFieldOnDomain" in src
        assert '"EDGE"' in src

    def test_grid_info_compile(self):
        src = _compile_model("gi", lambda: output(
            cube(1, 1, 1) | store_named_attribute(
                "info", grid_info(),
            )
        ))
        _assert_valid_python(src)
        assert "GeometryNodeGridInfo" in src

    def test_sample_grid_compile(self):
        src = _compile_model("sg", lambda: output(
            cube(1, 1, 1) | store_named_attribute(
                "val", sample_grid(interpolation_mode="NEAREST"),
            )
        ))
        _assert_valid_python(src)
        assert "GeometryNodeSampleGrid" in src
        assert '"NEAREST"' in src

    def test_sample_grid_index_compile(self):
        src = _compile_model("sgi", lambda: output(
            cube(1, 1, 1) | store_named_attribute(
                "val", sample_grid_index(x=1, y=2, z=3),
            )
        ))
        _assert_valid_python(src)
        assert "GeometryNodeSampleGridIndex" in src

    def test_sdf_grid_boolean_compile(self):
        src = _compile_model("sgb", lambda: output(
            cube(1, 1, 1) | store_named_attribute(
                "grid", sdf_grid_boolean(operation="UNION"),
            )
        ))
        _assert_valid_python(src)
        assert "GeometryNodeSDFGridBoolean" in src
        assert '"UNION"' in src

    def test_warning_node_compile(self):
        src = _compile_model("w", lambda: output(
            cube(1, 1, 1) | store_named_attribute(
                "warn", warning_node(message="oops", warning_type="WARNING"),
            )
        ))
        _assert_valid_python(src)
        assert "GeometryNodeWarning" in src
        assert '"WARNING"' in src

    def test_gizmo_dial_compile(self):
        src = _compile_model("gd", lambda: output(
            cube(1, 1, 1) | store_named_attribute(
                "g", gizmo_dial(color_id="X"),
            )
        ))
        _assert_valid_python(src)
        assert "GeometryNodeGizmoDial" in src

    def test_gizmo_linear_compile(self):
        src = _compile_model("gl", lambda: output(
            cube(1, 1, 1) | store_named_attribute(
                "g", gizmo_linear(draw_style="CROSS"),
            )
        ))
        _assert_valid_python(src)
        assert "GeometryNodeGizmoLinear" in src

    def test_gizmo_transform_compile(self):
        src = _compile_model("gt", lambda: output(
            cube(1, 1, 1) | store_named_attribute(
                "g", gizmo_transform(use_translation_x=True),
            )
        ))
        _assert_valid_python(src)
        assert "GeometryNodeGizmoTransform" in src

    def test_distribute_points_in_grid_compile(self):
        src = _compile_model("dpig", lambda: output(
            cube(1, 1, 1) | mesh_to_sdf_grid() | distribute_points_in_grid(density=2.0)
        ))
        _assert_valid_python(src)
        assert "GeometryNodeDistributePointsInGrid" in src

    def test_grid_to_mesh_compile(self):
        src = _compile_model("gtm", lambda: output(
            cube(1, 1, 1) | mesh_to_sdf_grid() | grid_to_mesh(threshold=0.2)
        ))
        _assert_valid_python(src)
        assert "GeometryNodeGridToMesh" in src

    def test_points_to_sdf_grid_compile(self):
        src = _compile_model("psdf", lambda: output(
            cube(1, 1, 1) | mesh_to_points() | points_to_sdf_grid(radius=0.5)
        ))
        _assert_valid_python(src)
        assert "GeometryNodePointsToSDFGrid" in src

    def test_set_instance_transform_compile(self):
        src = _compile_model("sit", lambda: output(
            cube(1, 1, 1) | geometry_to_instance() | set_instance_transform()
        ))
        _assert_valid_python(src)
        assert "GeometryNodeSetInstanceTransform" in src
