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
