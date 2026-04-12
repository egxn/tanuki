"""JSCAD compiler — IR graph → JSCAD JavaScript source.

Translates an IR tree into a self-contained JSCAD module that exports a
``main()`` function compatible with the @jscad/modeling API::

    const { primitives, booleans, transforms } = require('@jscad/modeling')

The generated file can be loaded directly in the JSCAD web viewer or
executed with the JSCAD CLI::

    npx @jscad/cli output.jscad -o output.stl
"""

from __future__ import annotations

import math
from pathlib import Path

from ...ir.graph import IRGraph
from ...ir.nodes import (
    BooleanOp,
    IRBoolean,
    IRFieldInput,
    IRGeometryOp,
    IRInstanceOnPoints,
    IRJoin,
    IRMathOp,
    IRNode,
    IROutput,
    IRPrimitive,
    IRSeparateComponents,
    IRSetPosition,
    IRTransform,
    IRValue,
    IRVector,
    PrimitiveType,
)


# ---------------------------------------------------------------------------
# Code emitter
# ---------------------------------------------------------------------------


class _Emitter:
    """Accumulates lines of JavaScript source."""

    def __init__(self) -> None:
        self._lines: list[str] = []
        self._var_counter = 0

    def line(self, text: str) -> None:
        self._lines.append(text)

    def blank(self) -> None:
        self._lines.append("")

    def comment(self, text: str) -> None:
        self._lines.append(f"// {text}")

    def new_var(self, prefix: str = "s") -> str:
        self._var_counter += 1
        return f"{prefix}_{self._var_counter}"

    def source(self) -> str:
        return "\n".join(self._lines) + "\n"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _fmt(v: float) -> str:
    if v == int(v):
        return str(int(v))
    return f"{v:.6g}"


def _vec3(v: tuple[float, float, float]) -> str:
    return f"[{_fmt(v[0])}, {_fmt(v[1])}, {_fmt(v[2])}]"


def _deg2rad(deg: float) -> float:
    return deg * math.pi / 180.0


# ---------------------------------------------------------------------------
# Compile functions — one per IR node type
# ---------------------------------------------------------------------------


def _compile_node(node: IRNode, em: _Emitter) -> str:
    """Dispatch compilation. Returns the JS variable name holding the geometry."""
    if isinstance(node, IROutput):
        return _compile_output(node, em)
    if isinstance(node, IRPrimitive):
        return _compile_primitive(node, em)
    if isinstance(node, IRBoolean):
        return _compile_boolean(node, em)
    if isinstance(node, IRTransform):
        return _compile_transform(node, em)
    if isinstance(node, IRSetPosition):
        return _compile_set_position(node, em)
    if isinstance(node, IRJoin):
        return _compile_join(node, em)
    if isinstance(node, IRInstanceOnPoints):
        return _compile_instance_on_points(node, em)
    if isinstance(node, IRGeometryOp):
        return _compile_geometry_op(node, em)
    if isinstance(node, IRSeparateComponents):
        return _compile_separate_components(node, em)
    if isinstance(node, IRFieldInput):
        em.comment(f"Field input ({node.field_type}) — not applicable in JSCAD")
        var = em.new_var("val")
        em.line(f"const {var} = 0;")
        return var
    if isinstance(node, IRMathOp):
        em.comment(f"Math op ({node.operation}) — not applicable in JSCAD")
        var = em.new_var("val")
        em.line(f"const {var} = 0;")
        return var
    if isinstance(node, IRValue):
        var = em.new_var("val")
        em.line(f"const {var} = {_fmt(node.value)};")
        return var
    if isinstance(node, IRVector):
        var = em.new_var("vec")
        em.line(f"const {var} = {_vec3(node.value)};")
        return var
    raise TypeError(f"Unknown IR node type: {type(node).__name__}")


def _compile_output(node: IROutput, em: _Emitter) -> str:
    if node.child:
        return _compile_node(node.child, em)
    var = em.new_var("shape")
    em.line(f"const {var} = primitives.cube();")
    return var


def _compile_primitive(node: IRPrimitive, em: _Emitter) -> str:
    props = node.properties
    var = em.new_var("shape")

    if node.primitive_type == PrimitiveType.CUBE:
        sx, sy, sz = props["size"]
        em.line(f"const {var} = primitives.cuboid({{ size: [{_fmt(sx)}, {_fmt(sy)}, {_fmt(sz)}] }});")

    elif node.primitive_type == PrimitiveType.SPHERE:
        r = props["radius"]
        seg = int(props.get("segments", 32))
        em.line(f"const {var} = primitives.sphere({{ radius: {_fmt(r)}, segments: {seg} }});")

    elif node.primitive_type == PrimitiveType.CYLINDER:
        r = props["radius"]
        h = props["depth"]
        seg = int(props.get("vertices", 32))
        em.line(
            f"const {var} = primitives.cylinder({{ "
            f"radius: {_fmt(r)}, height: {_fmt(h)}, segments: {seg} }});"
        )

    elif node.primitive_type == PrimitiveType.CONE:
        r1 = props.get("radius_bottom", 1.0)
        r2 = props.get("radius_top", 0.0)
        h = props["depth"]
        em.line(
            f"const {var} = primitives.cylinderElliptic({{ "
            f"startRadius: [{_fmt(r1)}, {_fmt(r1)}], "
            f"endRadius: [{_fmt(r2)}, {_fmt(r2)}], "
            f"height: {_fmt(h)} }});"
        )

    elif node.primitive_type == PrimitiveType.ICO_SPHERE:
        r = props["radius"]
        em.line(f"const {var} = primitives.geodesicSphere({{ radius: {_fmt(r)} }});")

    elif node.primitive_type == PrimitiveType.POINT:
        pos = props.get("position", (0, 0, 0))
        em.comment(f"Point at {_vec3(pos)}")
        em.line(
            f"const {var} = transforms.translate({_vec3(pos)}, "
            f"primitives.cuboid({{ size: [0.001, 0.001, 0.001] }}));"
        )

    elif node.primitive_type == PrimitiveType.CIRCLE:
        r = props["radius"]
        verts = int(props.get("vertices", 32))
        em.line(f"const {var} = primitives.circle({{ radius: {_fmt(r)}, segments: {verts} }});")

    elif node.primitive_type == PrimitiveType.GRID:
        sx = props["size_x"]
        sy = props["size_y"]
        em.line(f"const {var} = primitives.rectangle({{ size: [{_fmt(sx)}, {_fmt(sy)}] }});")

    elif node.primitive_type == PrimitiveType.LINE:
        start = props.get("start_location", (0, 0, 0))
        end = props.get("end_location", (0, 0, 1))
        em.line(
            f"const {var} = primitives.line("
            f"[{_vec3(start)}, {_vec3(end)}]);"
        )

    elif node.primitive_type == PrimitiveType.CURVE_LINE:
        start = props.get("start", (0, 0, 0))
        end = props.get("end", (0, 0, 1))
        em.line(
            f"const {var} = primitives.line("
            f"[{_vec3(start)}, {_vec3(end)}]);"
        )

    elif node.primitive_type == PrimitiveType.CURVE_CIRCLE:
        r = props["radius"]
        res = int(props.get("resolution", 32))
        em.line(f"const {var} = primitives.circle({{ radius: {_fmt(r)}, segments: {res} }});")

    elif node.primitive_type == PrimitiveType.CURVE_ARC:
        r = props["radius"]
        start_deg = props.get("start_angle", 0)
        sweep_deg = props.get("sweep_angle", 90)
        res = int(props.get("resolution", 32))
        em.line(
            f"const {var} = primitives.arc({{ "
            f"radius: {_fmt(r)}, "
            f"startAngle: {_fmt(_deg2rad(start_deg))}, "
            f"endAngle: {_fmt(_deg2rad(start_deg + sweep_deg))}, "
            f"segments: {res} }});"
        )

    elif node.primitive_type == PrimitiveType.CURVE_STAR:
        n_pts = int(props.get("points", 8))
        inner_r = props.get("inner_radius", 1.0)
        outer_r = props.get("outer_radius", 2.0)
        em.line(
            f"const {var} = primitives.star({{ "
            f"vertices: {n_pts}, "
            f"innerRadius: {_fmt(inner_r)}, "
            f"outerRadius: {_fmt(outer_r)} }});"
        )

    elif node.primitive_type == PrimitiveType.CURVE_QUADRILATERAL:
        w = props.get("width", 2.0)
        h = props.get("height", 2.0)
        em.line(f"const {var} = primitives.rectangle({{ size: [{_fmt(w)}, {_fmt(h)}] }});")

    elif node.primitive_type == PrimitiveType.CURVE_BEZIER_SEGMENT:
        pts = [props["start"], props["start_handle"], props["end_handle"], props["end"]]
        res = int(props.get("resolution", 16))
        em.comment("Cubic bezier segment")
        points = []
        for i in range(res + 1):
            t = i / res
            u = 1 - t
            x = u**3*pts[0][0] + 3*u**2*t*pts[1][0] + 3*u*t**2*pts[2][0] + t**3*pts[3][0]
            y = u**3*pts[0][1] + 3*u**2*t*pts[1][1] + 3*u*t**2*pts[2][1] + t**3*pts[3][1]
            points.append(f"[{_fmt(x)}, {_fmt(y)}]")
        pts_str = ", ".join(points)
        em.line(f"const {var} = primitives.line([{pts_str}]);")

    elif node.primitive_type == PrimitiveType.CURVE_QUADRATIC_BEZIER:
        pts = [props["start"], props["middle"], props["end"]]
        res = int(props.get("resolution", 16))
        em.comment("Quadratic bezier")
        points = []
        for i in range(res + 1):
            t = i / res
            u = 1 - t
            x = u**2*pts[0][0] + 2*u*t*pts[1][0] + t**2*pts[2][0]
            y = u**2*pts[0][1] + 2*u*t*pts[1][1] + t**2*pts[2][1]
            points.append(f"[{_fmt(x)}, {_fmt(y)}]")
        pts_str = ", ".join(points)
        em.line(f"const {var} = primitives.line([{pts_str}]);")

    elif node.primitive_type == PrimitiveType.CURVE_SPIRAL:
        rotations = props.get("rotations", 2)
        start_r = props.get("start_radius", 1.0)
        end_r = props.get("end_radius", 2.0)
        h = props.get("height", 2.0)
        res = int(props.get("resolution", 32))
        total_pts = max(2, int(rotations * res))
        em.comment("Spiral approximated as polyline")
        points = []
        for i in range(total_pts):
            t = i / (total_pts - 1)
            angle = 2 * math.pi * rotations * t
            r = start_r + (end_r - start_r) * t
            x = r * math.cos(angle)
            y = r * math.sin(angle)
            z = h * t
            points.append(f"[{_fmt(x)}, {_fmt(y)}, {_fmt(z)}]")
        pts_str = ", ".join(points)
        em.line(f"const {var} = primitives.line([{pts_str}]);")

    elif node.primitive_type == PrimitiveType.VOLUME_CUBE:
        mn = props.get("min", (-1, -1, -1))
        mx = props.get("max", (1, 1, 1))
        sx = mx[0] - mn[0]
        sy = mx[1] - mn[1]
        sz = mx[2] - mn[2]
        cx = (mn[0] + mx[0]) / 2
        cy = (mn[1] + mx[1]) / 2
        cz = (mn[2] + mx[2]) / 2
        em.line(
            f"const {var} = transforms.translate("
            f"[{_fmt(cx)}, {_fmt(cy)}, {_fmt(cz)}], "
            f"primitives.cuboid({{ size: [{_fmt(sx)}, {_fmt(sy)}, {_fmt(sz)}] }}));"
        )

    else:
        em.comment(f"Unsupported primitive: {node.primitive_type.name}")
        em.line(f"const {var} = primitives.cuboid();")

    if node.label:
        em.comment(f"label: {node.label}")

    return var


def _compile_boolean(node: IRBoolean, em: _Emitter) -> str:
    child_vars = [_compile_node(c, em) for c in node.children]

    if not child_vars:
        var = em.new_var("shape")
        em.line(f"const {var} = primitives.cuboid();")
        return var

    if len(child_vars) == 1:
        return child_vars[0]

    args = ", ".join(child_vars)
    var = em.new_var("shape")

    if node.operation == BooleanOp.UNION:
        em.line(f"const {var} = booleans.union({args});")
    elif node.operation == BooleanOp.DIFFERENCE:
        em.line(f"const {var} = booleans.subtract({args});")
    else:  # INTERSECT
        em.line(f"const {var} = booleans.intersect({args});")

    if node.label:
        em.comment(f"label: {node.label}")

    return var


def _compile_transform(node: IRTransform, em: _Emitter) -> str:
    child_var = _compile_node(node.child, em) if node.child else None

    if child_var is None:
        var = em.new_var("shape")
        em.line(f"const {var} = primitives.cuboid();")
        return var

    current = child_var

    # Scale
    if node.scale is not None:
        sx, sy, sz = node.scale
        if sx != 1 or sy != 1 or sz != 1:
            var = em.new_var("shape")
            em.line(f"const {var} = transforms.scale([{_fmt(sx)}, {_fmt(sy)}, {_fmt(sz)}], {current});")
            current = var

    # Rotation (degrees → radians)
    if node.rotation is not None:
        rx, ry, rz = node.rotation
        if rx != 0 or ry != 0 or rz != 0:
            var = em.new_var("shape")
            em.line(
                f"const {var} = transforms.rotate("
                f"[{_fmt(_deg2rad(rx))}, {_fmt(_deg2rad(ry))}, {_fmt(_deg2rad(rz))}], "
                f"{current});"
            )
            current = var

    # Translation
    if node.translation is not None:
        tx, ty, tz = node.translation
        if tx != 0 or ty != 0 or tz != 0:
            var = em.new_var("shape")
            em.line(f"const {var} = transforms.translate([{_fmt(tx)}, {_fmt(ty)}, {_fmt(tz)}], {current});")
            current = var

    if node.label:
        em.comment(f"label: {node.label}")

    return current


def _compile_set_position(node: IRSetPosition, em: _Emitter) -> str:
    child_var = _compile_node(node.child, em) if node.child else None

    if child_var is None:
        var = em.new_var("shape")
        em.line(f"const {var} = primitives.cuboid();")
        return var

    ox, oy, oz = node.offset
    if ox == 0 and oy == 0 and oz == 0:
        return child_var

    var = em.new_var("shape")
    em.line(f"const {var} = transforms.translate([{_fmt(ox)}, {_fmt(oy)}, {_fmt(oz)}], {child_var});")
    return var


def _compile_join(node: IRJoin, em: _Emitter) -> str:
    child_vars = [_compile_node(c, em) for c in node.children]

    if not child_vars:
        var = em.new_var("shape")
        em.line(f"const {var} = primitives.cuboid();")
        return var

    if len(child_vars) == 1:
        return child_vars[0]

    args = ", ".join(child_vars)
    var = em.new_var("shape")
    em.line(f"const {var} = booleans.union({args});")
    return var


def _compile_instance_on_points(node: IRInstanceOnPoints, em: _Emitter) -> str:
    instance_var = _compile_node(node.instance, em) if node.instance else None
    points_var = _compile_node(node.points, em) if node.points else None

    em.comment("Instance on points: not directly supported, union of instance + points")
    var = em.new_var("shape")
    if instance_var and points_var:
        em.line(f"const {var} = booleans.union({points_var}, {instance_var});")
    elif instance_var:
        em.line(f"const {var} = {instance_var};")
    elif points_var:
        em.line(f"const {var} = {points_var};")
    else:
        em.line(f"const {var} = primitives.cuboid();")

    return var


def _compile_geometry_op(node: IRGeometryOp, em: _Emitter) -> str:
    child_var = _compile_node(node.child, em) if node.child else None
    props = node.properties

    if node.label:
        em.comment(node.label)

    # Extrude → extrusions.extrudeLinear
    if node.op_type == "GeometryNodeExtrudeMesh":
        offset = props.get("offset_scale", 1.0)
        if child_var:
            var = em.new_var("shape")
            em.line(
                f"const {var} = extrusions.extrudeLinear("
                f"{{ height: {_fmt(abs(offset))} }}, {child_var});"
            )
            return var

    # Fill curve → pass through (2D shape already)
    if node.op_type == "GeometryNodeFillCurve":
        if child_var:
            return child_var

    # Curve to mesh → extrudeLinear on profile
    if node.op_type == "GeometryNodeCurveToMesh":
        profile_node = node.extra_children.get("Profile Curve")
        if profile_node and child_var:
            profile_var = _compile_node(profile_node, em)
            var = em.new_var("shape")
            em.line(
                f"const {var} = extrusions.extrudeLinear("
                f"{{ height: 1 }}, {profile_var});"
            )
            return var
        if child_var:
            return child_var

    # Convex hull → hulls.hull
    if node.op_type == "GeometryNodeConvexHull":
        if child_var:
            var = em.new_var("shape")
            em.line(f"const {var} = hulls.hull({child_var});")
            return var

    # Scale elements
    if node.op_type == "GeometryNodeScaleElements":
        s = props.get("element_scale", 1.0)
        if child_var:
            var = em.new_var("shape")
            em.line(f"const {var} = transforms.scale([{_fmt(s)}, {_fmt(s)}, {_fmt(s)}], {child_var});")
            return var

    # Rotate instances
    if node.op_type == "GeometryNodeRotateInstances":
        rot = props.get("rotation", (0, 0, 0))
        if child_var:
            var = em.new_var("shape")
            em.line(
                f"const {var} = transforms.rotate("
                f"[{_fmt(rot[0])}, {_fmt(rot[1])}, {_fmt(rot[2])}], {child_var});"
            )
            return var

    # Scale instances
    if node.op_type == "GeometryNodeScaleInstances":
        sc = props.get("scale", (1, 1, 1))
        if child_var:
            var = em.new_var("shape")
            em.line(f"const {var} = transforms.scale({_vec3(sc)}, {child_var});")
            return var

    # Translate instances
    if node.op_type == "GeometryNodeTranslateInstances":
        tr = props.get("translation", (0, 0, 0))
        if child_var:
            var = em.new_var("shape")
            em.line(f"const {var} = transforms.translate({_vec3(tr)}, {child_var});")
            return var

    # Pass-through ops (no JSCAD equivalent)
    _passthrough_ops = {
        "GeometryNodeSubdivideMesh",
        "GeometryNodeSubdivisionSurface",
        "GeometryNodeSetShadeSmooth",
        "GeometryNodeSetMeshNormal",
        "GeometryNodeRealizeInstances",
        "GeometryNodeSetMaterial",
        "GeometryNodeReplaceMaterial",
        "GeometryNodeSetMaterialIndex",
        "GeometryNodeStoreNamedAttribute",
        "GeometryNodeRemoveAttribute",
        "GeometryNodeSetGeometryName",
        "GeometryNodeMergeByDistance",
        "GeometryNodeDualMesh",
        "GeometryNodeFlipFaces",
        "GeometryNodeSplitEdges",
        "GeometryNodeTriangulate",
    }
    if node.op_type in _passthrough_ops:
        em.comment(f"{node.op_type}: pass-through (not applicable in JSCAD)")
        if child_var:
            return child_var

    # Fallback
    if child_var:
        em.comment(f"Unsupported geometry op: {node.op_type}")
        return child_var

    var = em.new_var("shape")
    em.line(f"const {var} = primitives.cuboid();")
    return var


def _compile_separate_components(node: IRSeparateComponents, em: _Emitter) -> str:
    em.comment(f"SeparateComponents({node.component}): pass-through")
    if node.child:
        return _compile_node(node.child, em)
    var = em.new_var("shape")
    em.line(f"const {var} = primitives.cuboid();")
    return var


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def compile_to_source(graph: IRGraph) -> str:
    """Compile an IR graph to a JSCAD module string."""
    em = _Emitter()

    em.comment("Auto-generated by Tanuki compiler (JSCAD backend)")
    em.comment(f"Model: {graph.name}")
    em.blank()
    em.line("const jscad = require('@jscad/modeling');")
    em.line("const { primitives, booleans, transforms, extrusions, hulls } = jscad;")
    em.blank()

    safe_name = graph.name.replace("-", "_")
    em.line(f"const main = () => {{")

    if graph.root:
        inner = _Emitter()
        result_var = _compile_node(graph.root, inner)
        for raw_line in inner.source().splitlines():
            if raw_line:
                em.line(f"  {raw_line}")
            else:
                em.blank()
        em.line(f"  return {result_var};")
    else:
        em.line("  return primitives.cuboid();")

    em.line("};")
    em.blank()
    em.line("module.exports = { main };")
    em.blank()

    return em.source()


def compile_to_script(graph: IRGraph, output_path: str | Path) -> Path:
    """Compile an IR graph and write the result to a .jscad file."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(compile_to_source(graph))
    return path
