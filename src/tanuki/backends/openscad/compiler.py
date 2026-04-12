"""OpenSCAD compiler — IR graph → OpenSCAD source (.scad).

Translates an IR tree into a self-contained ``.scad`` file that can be
opened directly in the OpenSCAD application or rendered from the CLI with::

    openscad -o output.stl output.scad
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
    """Accumulates indented OpenSCAD source lines."""

    def __init__(self) -> None:
        self._lines: list[str] = []
        self._indent = 0

    def line(self, text: str) -> None:
        self._lines.append("  " * self._indent + text)

    def blank(self) -> None:
        self._lines.append("")

    def comment(self, text: str) -> None:
        self._lines.append("  " * self._indent + f"// {text}")

    def indent(self) -> None:
        self._indent += 1

    def dedent(self) -> None:
        self._indent = max(0, self._indent - 1)

    def source(self) -> str:
        return "\n".join(self._lines) + "\n"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _fmt(v: float) -> str:
    """Format a float, stripping trailing zeros."""
    if v == int(v):
        return str(int(v))
    return f"{v:.6g}"


def _vec3(v: tuple[float, float, float]) -> str:
    return f"[{_fmt(v[0])}, {_fmt(v[1])}, {_fmt(v[2])}]"


# ---------------------------------------------------------------------------
# Compile functions
# ---------------------------------------------------------------------------


def _compile_node(node: IRNode, em: _Emitter) -> None:
    """Dispatch to the appropriate handler."""
    if isinstance(node, IROutput):
        _compile_output(node, em)
    elif isinstance(node, IRPrimitive):
        _compile_primitive(node, em)
    elif isinstance(node, IRBoolean):
        _compile_boolean(node, em)
    elif isinstance(node, IRTransform):
        _compile_transform(node, em)
    elif isinstance(node, IRSetPosition):
        _compile_set_position(node, em)
    elif isinstance(node, IRJoin):
        _compile_join(node, em)
    elif isinstance(node, IRInstanceOnPoints):
        _compile_instance_on_points(node, em)
    elif isinstance(node, IRGeometryOp):
        _compile_geometry_op(node, em)
    elif isinstance(node, IRSeparateComponents):
        _compile_separate_components(node, em)
    elif isinstance(node, IRFieldInput):
        em.comment(f"Field input ({node.field_type}) — not applicable in OpenSCAD")
    elif isinstance(node, IRMathOp):
        em.comment(f"Math op ({node.operation}) — not applicable in OpenSCAD")
    elif isinstance(node, IRValue):
        em.comment(f"Value: {node.value}")
    elif isinstance(node, IRVector):
        em.comment(f"Vector: {_vec3(node.value)}")
    else:
        em.comment(f"Unknown node: {type(node).__name__}")


def _compile_output(node: IROutput, em: _Emitter) -> None:
    if node.child:
        _compile_node(node.child, em)


def _compile_primitive(node: IRPrimitive, em: _Emitter) -> None:
    props = node.properties
    label = node.label

    if label:
        em.comment(label)

    if node.primitive_type == PrimitiveType.CUBE:
        sx, sy, sz = props["size"]
        em.line(f"translate([{_fmt(-sx/2)}, {_fmt(-sy/2)}, {_fmt(-sz/2)}])")
        em.indent()
        em.line(f"cube([{_fmt(sx)}, {_fmt(sy)}, {_fmt(sz)}]);")
        em.dedent()

    elif node.primitive_type == PrimitiveType.SPHERE:
        r = props["radius"]
        segments = props.get("segments")
        if segments:
            em.line(f"sphere(r={_fmt(r)}, $fn={int(segments)});")
        else:
            em.line(f"sphere(r={_fmt(r)});")

    elif node.primitive_type == PrimitiveType.CYLINDER:
        r = props["radius"]
        h = props["depth"]
        verts = props.get("vertices")
        fn = f", $fn={int(verts)}" if verts else ""
        em.line(f"translate([0, 0, {_fmt(-h/2)}])")
        em.indent()
        em.line(f"cylinder(r={_fmt(r)}, h={_fmt(h)}{fn});")
        em.dedent()

    elif node.primitive_type == PrimitiveType.CONE:
        r1 = props.get("radius_bottom", 1.0)
        r2 = props.get("radius_top", 0.0)
        h = props["depth"]
        em.line(f"translate([0, 0, {_fmt(-h/2)}])")
        em.indent()
        em.line(f"cylinder(r1={_fmt(r1)}, r2={_fmt(r2)}, h={_fmt(h)});")
        em.dedent()

    elif node.primitive_type == PrimitiveType.ICO_SPHERE:
        r = props["radius"]
        em.comment("ico_sphere approximated as sphere")
        em.line(f"sphere(r={_fmt(r)});")

    elif node.primitive_type == PrimitiveType.POINT:
        pos = props.get("position", (0, 0, 0))
        em.comment(f"Point at {_vec3(pos)} (no geometry in OpenSCAD)")

    elif node.primitive_type == PrimitiveType.CIRCLE:
        r = props["radius"]
        verts = int(props.get("vertices", 32))
        fill = props.get("fill_type", "NONE")
        if fill != "NONE":
            em.line(f"circle(r={_fmt(r)}, $fn={verts});")
        else:
            em.comment("Circle wire (2D outline)")
            em.line(f"circle(r={_fmt(r)}, $fn={verts});")

    elif node.primitive_type == PrimitiveType.GRID:
        sx = props["size_x"]
        sy = props["size_y"]
        em.comment("Grid approximated as thin cube")
        em.line(f"translate([{_fmt(-sx/2)}, {_fmt(-sy/2)}, 0])")
        em.indent()
        em.line(f"cube([{_fmt(sx)}, {_fmt(sy)}, 0.001]);")
        em.dedent()

    elif node.primitive_type == PrimitiveType.LINE:
        start = props.get("start_location", (0, 0, 0))
        end = props.get("end_location", (0, 0, 1))
        em.comment(f"Line from {_vec3(start)} to {_vec3(end)}")
        # Approximate as a thin cylinder between start and end
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        dz = end[2] - start[2]
        length = math.sqrt(dx * dx + dy * dy + dz * dz)
        if length > 0:
            em.line(f"hull() {{")
            em.indent()
            em.line(f"translate({_vec3(start)}) sphere(r=0.01);")
            em.line(f"translate({_vec3(end)}) sphere(r=0.01);")
            em.dedent()
            em.line("}")

    elif node.primitive_type == PrimitiveType.CURVE_LINE:
        start = props.get("start", (0, 0, 0))
        end = props.get("end", (0, 0, 1))
        em.comment(f"Curve line from {_vec3(start)} to {_vec3(end)}")
        em.line(f"hull() {{")
        em.indent()
        em.line(f"translate({_vec3(start)}) sphere(r=0.01);")
        em.line(f"translate({_vec3(end)}) sphere(r=0.01);")
        em.dedent()
        em.line("}")

    elif node.primitive_type == PrimitiveType.CURVE_CIRCLE:
        r = props["radius"]
        res = int(props.get("resolution", 32))
        em.comment("Curve circle (2D)")
        em.line(f"circle(r={_fmt(r)}, $fn={res});")

    elif node.primitive_type == PrimitiveType.CURVE_ARC:
        r = props["radius"]
        start_deg = props.get("start_angle", 0)
        sweep_deg = props.get("sweep_angle", 90)
        res = int(props.get("resolution", 32))
        em.comment(f"Arc: r={_fmt(r)}, start={_fmt(start_deg)}°, sweep={_fmt(sweep_deg)}°")
        # Approximate with a 2D polygon arc
        steps = max(3, res)
        em.line("polygon(points=[")
        em.indent()
        em.line(f"[0, 0],")
        for i in range(steps + 1):
            a = math.radians(start_deg + sweep_deg * i / steps)
            em.line(f"[{_fmt(r * math.cos(a))}, {_fmt(r * math.sin(a))}],")
        em.dedent()
        em.line("]);")

    elif node.primitive_type == PrimitiveType.CURVE_STAR:
        n_pts = int(props.get("points", 8))
        inner_r = props.get("inner_radius", 1.0)
        outer_r = props.get("outer_radius", 2.0)
        em.comment(f"Star: {n_pts} points, inner={_fmt(inner_r)}, outer={_fmt(outer_r)}")
        total = n_pts * 2
        em.line("polygon(points=[")
        em.indent()
        for i in range(total):
            angle = 2 * math.pi * i / total
            r = outer_r if i % 2 == 0 else inner_r
            em.line(f"[{_fmt(r * math.cos(angle))}, {_fmt(r * math.sin(angle))}],")
        em.dedent()
        em.line("]);")

    elif node.primitive_type == PrimitiveType.CURVE_QUADRILATERAL:
        w = props.get("width", 2.0)
        h = props.get("height", 2.0)
        hw, hh = w / 2, h / 2
        em.line(f"square([{_fmt(w)}, {_fmt(h)}], center=true);")

    elif node.primitive_type == PrimitiveType.CURVE_BEZIER_SEGMENT:
        pts = [props["start"], props["start_handle"], props["end_handle"], props["end"]]
        em.comment("Bezier segment approximated as polyline")
        steps = int(props.get("resolution", 16))
        em.line("polygon(points=[")
        em.indent()
        for i in range(steps + 1):
            t = i / steps
            u = 1 - t
            # Cubic bezier
            x = u**3*pts[0][0] + 3*u**2*t*pts[1][0] + 3*u*t**2*pts[2][0] + t**3*pts[3][0]
            y = u**3*pts[0][1] + 3*u**2*t*pts[1][1] + 3*u*t**2*pts[2][1] + t**3*pts[3][1]
            em.line(f"[{_fmt(x)}, {_fmt(y)}],")
        em.dedent()
        em.line("]);")

    elif node.primitive_type == PrimitiveType.CURVE_QUADRATIC_BEZIER:
        pts = [props["start"], props["middle"], props["end"]]
        em.comment("Quadratic bezier approximated as polyline")
        steps = int(props.get("resolution", 16))
        em.line("polygon(points=[")
        em.indent()
        for i in range(steps + 1):
            t = i / steps
            u = 1 - t
            x = u**2*pts[0][0] + 2*u*t*pts[1][0] + t**2*pts[2][0]
            y = u**2*pts[0][1] + 2*u*t*pts[1][1] + t**2*pts[2][1]
            em.line(f"[{_fmt(x)}, {_fmt(y)}],")
        em.dedent()
        em.line("]);")

    elif node.primitive_type == PrimitiveType.CURVE_SPIRAL:
        rotations = props.get("rotations", 2)
        start_r = props.get("start_radius", 1.0)
        end_r = props.get("end_radius", 2.0)
        h = props.get("height", 2.0)
        res = int(props.get("resolution", 32))
        em.comment("Spiral approximated as polyline hull chain")
        total_pts = max(2, int(rotations * res))
        em.line("union() {")
        em.indent()
        for i in range(total_pts - 1):
            t1 = i / (total_pts - 1)
            t2 = (i + 1) / (total_pts - 1)
            a1 = 2 * math.pi * rotations * t1
            a2 = 2 * math.pi * rotations * t2
            r1 = start_r + (end_r - start_r) * t1
            r2 = start_r + (end_r - start_r) * t2
            p1 = (r1 * math.cos(a1), r1 * math.sin(a1), h * t1)
            p2 = (r2 * math.cos(a2), r2 * math.sin(a2), h * t2)
            em.line(f"hull() {{")
            em.indent()
            em.line(f"translate({_vec3(p1)}) sphere(r=0.01);")
            em.line(f"translate({_vec3(p2)}) sphere(r=0.01);")
            em.dedent()
            em.line("}")
        em.dedent()
        em.line("}")

    elif node.primitive_type == PrimitiveType.VOLUME_CUBE:
        mn = props.get("min", (-1, -1, -1))
        mx = props.get("max", (1, 1, 1))
        sx = mx[0] - mn[0]
        sy = mx[1] - mn[1]
        sz = mx[2] - mn[2]
        em.comment("Volume cube approximated as solid cube")
        em.line(f"translate({_vec3(mn)})")
        em.indent()
        em.line(f"cube([{_fmt(sx)}, {_fmt(sy)}, {_fmt(sz)}]);")
        em.dedent()

    else:
        em.comment(f"Unsupported primitive: {node.primitive_type.name}")


def _compile_boolean(node: IRBoolean, em: _Emitter) -> None:
    if not node.children:
        return

    if node.label:
        em.comment(node.label)

    op_map = {
        BooleanOp.UNION: "union",
        BooleanOp.DIFFERENCE: "difference",
        BooleanOp.INTERSECT: "intersection",
    }
    op_name = op_map[node.operation]

    em.line(f"{op_name}() {{")
    em.indent()
    for child in node.children:
        _compile_node(child, em)
    em.dedent()
    em.line("}")


def _compile_transform(node: IRTransform, em: _Emitter) -> None:
    if node.child is None:
        return

    if node.label:
        em.comment(node.label)

    # Collect wrappers in reverse order (innermost applied first)
    wrappers: list[str] = []

    if node.scale is not None:
        sx, sy, sz = node.scale
        wrappers.append(f"scale([{_fmt(sx)}, {_fmt(sy)}, {_fmt(sz)}])")

    if node.rotation is not None:
        rx, ry, rz = node.rotation
        wrappers.append(f"rotate([{_fmt(rx)}, {_fmt(ry)}, {_fmt(rz)}])")

    if node.translation is not None:
        tx, ty, tz = node.translation
        wrappers.append(f"translate([{_fmt(tx)}, {_fmt(ty)}, {_fmt(tz)}])")

    if not wrappers:
        _compile_node(node.child, em)
        return

    # Emit outermost (last in list = translation) first
    for w in wrappers:
        em.line(w)
        em.indent()
    _compile_node(node.child, em)
    for _ in wrappers:
        em.dedent()


def _compile_set_position(node: IRSetPosition, em: _Emitter) -> None:
    if node.child is None:
        return

    ox, oy, oz = node.offset
    if ox == 0 and oy == 0 and oz == 0:
        _compile_node(node.child, em)
        return

    if node.label:
        em.comment(node.label)

    em.line(f"translate([{_fmt(ox)}, {_fmt(oy)}, {_fmt(oz)}])")
    em.indent()
    _compile_node(node.child, em)
    em.dedent()


def _compile_join(node: IRJoin, em: _Emitter) -> None:
    if not node.children:
        return

    if node.label:
        em.comment(node.label)

    em.line("union() {")
    em.indent()
    for child in node.children:
        _compile_node(child, em)
    em.dedent()
    em.line("}")


def _compile_instance_on_points(node: IRInstanceOnPoints, em: _Emitter) -> None:
    if node.label:
        em.comment(node.label)

    em.comment("Instance on points: not directly supported in OpenSCAD")
    em.comment("Rendering instance and points separately as a union")
    em.line("union() {")
    em.indent()
    if node.points:
        _compile_node(node.points, em)
    if node.instance:
        _compile_node(node.instance, em)
    em.dedent()
    em.line("}")


def _compile_geometry_op(node: IRGeometryOp, em: _Emitter) -> None:
    props = node.properties

    if node.label:
        em.comment(node.label)

    # Extrude → linear_extrude
    if node.op_type == "GeometryNodeExtrudeMesh":
        offset = props.get("offset_scale", 1.0)
        em.line(f"linear_extrude(height={_fmt(abs(offset))})")
        em.indent()
        if node.child:
            _compile_node(node.child, em)
        em.dedent()
        return

    # Fill curve → just pass the 2D child (already a polygon)
    if node.op_type == "GeometryNodeFillCurve":
        if node.child:
            _compile_node(node.child, em)
        return

    # Curve to mesh (sweep) → rotate_extrude or linear_extrude with profile
    if node.op_type == "GeometryNodeCurveToMesh":
        profile_node = node.extra_children.get("Profile Curve")
        if profile_node and node.child:
            em.comment("Curve to mesh: approximated as linear_extrude of profile")
            em.line("linear_extrude(height=1)")
            em.indent()
            _compile_node(profile_node, em)
            em.dedent()
        elif node.child:
            _compile_node(node.child, em)
        return

    # Subdivide surface → just pass through (OpenSCAD has no subdivision)
    if node.op_type in (
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
    ):
        em.comment(f"{node.op_type}: pass-through (not applicable in OpenSCAD)")
        if node.child:
            _compile_node(node.child, em)
        return

    # Merge by distance → hull approximation
    if node.op_type == "GeometryNodeMergeByDistance":
        if node.child:
            _compile_node(node.child, em)
        return

    # Convex hull
    if node.op_type == "GeometryNodeConvexHull":
        em.line("hull() {")
        em.indent()
        if node.child:
            _compile_node(node.child, em)
        em.dedent()
        em.line("}")
        return

    # Dual mesh, flip faces, split edges — pass through
    if node.op_type in (
        "GeometryNodeDualMesh",
        "GeometryNodeFlipFaces",
        "GeometryNodeSplitEdges",
        "GeometryNodeTriangulate",
    ):
        em.comment(f"{node.op_type}: pass-through")
        if node.child:
            _compile_node(node.child, em)
        return

    # Scale elements
    if node.op_type == "GeometryNodeScaleElements":
        s = props.get("element_scale", 1.0)
        em.line(f"scale([{_fmt(s)}, {_fmt(s)}, {_fmt(s)}])")
        em.indent()
        if node.child:
            _compile_node(node.child, em)
        em.dedent()
        return

    # Rotate instances
    if node.op_type == "GeometryNodeRotateInstances":
        rot = props.get("rotation", (0, 0, 0))
        rx, ry, rz = (math.degrees(c) if abs(c) > 1e-6 else 0 for c in rot)
        em.line(f"rotate([{_fmt(rx)}, {_fmt(ry)}, {_fmt(rz)}])")
        em.indent()
        if node.child:
            _compile_node(node.child, em)
        em.dedent()
        return

    # Scale instances
    if node.op_type == "GeometryNodeScaleInstances":
        sc = props.get("scale", (1, 1, 1))
        em.line(f"scale({_vec3(sc)})")
        em.indent()
        if node.child:
            _compile_node(node.child, em)
        em.dedent()
        return

    # Translate instances
    if node.op_type == "GeometryNodeTranslateInstances":
        tr = props.get("translation", (0, 0, 0))
        em.line(f"translate({_vec3(tr)})")
        em.indent()
        if node.child:
            _compile_node(node.child, em)
        em.dedent()
        return

    # Fallback: pass child through with a comment
    em.comment(f"Unsupported geometry op: {node.op_type}")
    if node.child:
        _compile_node(node.child, em)


def _compile_separate_components(node: IRSeparateComponents, em: _Emitter) -> None:
    em.comment(f"SeparateComponents({node.component}): pass-through")
    if node.child:
        _compile_node(node.child, em)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def compile_to_source(graph: IRGraph) -> str:
    """Compile an IR graph to an OpenSCAD source string."""
    em = _Emitter()

    em.comment("Auto-generated by Tanuki compiler (OpenSCAD backend)")
    em.comment(f"Model: {graph.name}")
    em.blank()

    if graph.root:
        _compile_node(graph.root, em)

    return em.source()


def compile_to_script(graph: IRGraph, output_path: str | Path) -> Path:
    """Compile an IR graph and write the result to a .scad file."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(compile_to_source(graph))
    return path
