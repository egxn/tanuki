"""OpenCascade.js compiler — IR graph → JavaScript source.

Translates an IR tree into a self-contained JavaScript module that,
when executed with an opencascade.js instance, builds the BREP geometry.

The generated script exports a ``setup(oc)`` function that receives the
initialised opencascade.js module and returns a ``TopoDS_Shape``.
"""

from __future__ import annotations

import math
from pathlib import Path

from ...ir.graph import IRGraph
from ...ir.nodes import (
    BooleanOp,
    IRBoolean,
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
# Code emitter — accumulates lines of JavaScript source
# ---------------------------------------------------------------------------


class _Emitter:
    """Stateful code accumulator for JS output."""

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
# Geometry-op mapping (IR op_type → OCCT support)
# ---------------------------------------------------------------------------

# Geometry ops that have a direct OCCT equivalent
_SUPPORTED_GEOM_OPS: dict[str, str] = {
    "GeometryNodeExtrudeMesh": "BRepPrimAPI_MakePrism",
    "GeometryNodeFilletCurve": "BRepFilletAPI_MakeFillet",
    "GeometryNodeFillCurve": "BRepBuilderAPI_MakeFace",
    "GeometryNodeCurveToMesh": "BRepOffsetAPI_MakePipe",
}


# ---------------------------------------------------------------------------
# Compile functions — one per IR node type
# ---------------------------------------------------------------------------


def _compile_value(node: IRValue, em: _Emitter) -> str:
    var = em.new_var("val")
    em.line(f"const {var} = {node.value};")
    return var


def _compile_vector(node: IRVector, em: _Emitter) -> str:
    var = em.new_var("vec")
    x, y, z = node.value
    em.line(f"const {var} = new oc.gp_Vec_4({x}, {y}, {z});")
    return var


def _compile_point(value: tuple[float, float, float], em: _Emitter) -> str:
    var = em.new_var("pt")
    x, y, z = value
    em.line(f"const {var} = new oc.gp_Pnt_3({x}, {y}, {z});")
    return var


def _compile_primitive(node: IRPrimitive, em: _Emitter) -> str:
    props = node.properties
    var = em.new_var("shape")

    if node.primitive_type == PrimitiveType.CUBE:
        sx, sy, sz = props["size"]
        corner = _compile_point((-sx / 2, -sy / 2, -sz / 2), em)
        em.line(f"const {var} = new oc.BRepPrimAPI_MakeBox_2({corner}, {sx}, {sy}, {sz}).Shape();")

    elif node.primitive_type == PrimitiveType.SPHERE:
        r = props["radius"]
        em.line(f"const {var} = new oc.BRepPrimAPI_MakeSphere_1({r}).Shape();")

    elif node.primitive_type == PrimitiveType.CYLINDER:
        r = props["radius"]
        h = props["depth"]
        # OCCT cylinder starts at Z=0, center it vertically
        ax_var = em.new_var("ax")
        em.line(
            f"const {ax_var} = new oc.gp_Ax2_3("
            f"new oc.gp_Pnt_3(0, 0, {-h / 2}), new oc.gp_Dir_4(0, 0, 1));"
        )
        em.line(f"const {var} = new oc.BRepPrimAPI_MakeCylinder_2({ax_var}, {r}, {h}).Shape();")

    elif node.primitive_type == PrimitiveType.CONE:
        r1 = props.get("radius_bottom", 1.0)
        r2 = props.get("radius_top", 0.0)
        h = props["depth"]
        ax_var = em.new_var("ax")
        em.line(
            f"const {ax_var} = new oc.gp_Ax2_3("
            f"new oc.gp_Pnt_3(0, 0, {-h / 2}), new oc.gp_Dir_4(0, 0, 1));"
        )
        em.line(f"const {var} = new oc.BRepPrimAPI_MakeCone_2({ax_var}, {r1}, {r2}, {h}).Shape();")

    elif node.primitive_type == PrimitiveType.ICO_SPHERE:
        # OCCT has no ico sphere — use regular sphere
        r = props["radius"]
        em.comment("ICO_SPHERE approximated as UV sphere in OCCT")
        em.line(f"const {var} = new oc.BRepPrimAPI_MakeSphere_1({r}).Shape();")

    elif node.primitive_type == PrimitiveType.POINT:
        # Represent as a vertex (degenerate shape)
        pos = props.get("position", (0, 0, 0))
        pt_var = _compile_point(pos, em)
        em.line(f"const {var} = new oc.BRepBuilderAPI_MakeVertex({pt_var}).Shape();")

    elif node.primitive_type == PrimitiveType.CIRCLE:
        r = props["radius"]
        ax_var = em.new_var("ax")
        em.line(f"const {ax_var} = new oc.gp_Ax2_1();")
        circ_var = em.new_var("circ")
        em.line(f"const {circ_var} = new oc.gp_Circ_2({ax_var}, {r});")
        edge_var = em.new_var("edge")
        em.line(f"const {edge_var} = new oc.BRepBuilderAPI_MakeEdge_9({circ_var}).Edge();")
        wire_var = em.new_var("wire")
        em.line(f"const {wire_var} = new oc.BRepBuilderAPI_MakeWire_2({edge_var}).Wire();")
        fill = props.get("fill_type", "NONE")
        if fill != "NONE":
            em.line(f"const {var} = new oc.BRepBuilderAPI_MakeFace_15({wire_var}, true).Shape();")
        else:
            em.line(f"const {var} = oc.TopoDS.prototype.constructor.Wire_1({wire_var});")

    elif node.primitive_type == PrimitiveType.GRID:
        sx = props["size_x"]
        sy = props["size_y"]
        corner = _compile_point((-sx / 2, -sy / 2, 0), em)
        em.comment("Grid approximated as a flat box face")
        em.line(
            f"const {var} = new oc.BRepBuilderAPI_MakeFace_25("
            f"new oc.gp_Pln_1(), {corner}, "
            f"new oc.gp_Pnt_3({sx / 2}, {sy / 2}, 0), 1e-6).Shape();"
        )

    elif node.primitive_type == PrimitiveType.LINE:
        start = props.get("start_location", (0, 0, 0))
        end = props.get("end_location", (0, 0, 1))
        p1 = _compile_point(start, em)
        p2 = _compile_point(end, em)
        em.line(f"const {var} = new oc.BRepBuilderAPI_MakeEdge_3({p1}, {p2}).Shape();")

    elif node.primitive_type == PrimitiveType.CURVE_LINE:
        start = props.get("start", (0, 0, 0))
        end = props.get("end", (0, 0, 1))
        p1 = _compile_point(start, em)
        p2 = _compile_point(end, em)
        em.line(f"const {var} = new oc.BRepBuilderAPI_MakeEdge_3({p1}, {p2}).Shape();")

    elif node.primitive_type == PrimitiveType.CURVE_CIRCLE:
        r = props["radius"]
        ax_var = em.new_var("ax")
        em.line(f"const {ax_var} = new oc.gp_Ax2_1();")
        circ_var = em.new_var("circ")
        em.line(f"const {circ_var} = new oc.gp_Circ_2({ax_var}, {r});")
        em.line(f"const {var} = new oc.BRepBuilderAPI_MakeEdge_9({circ_var}).Shape();")

    elif node.primitive_type == PrimitiveType.CURVE_ARC:
        r = props["radius"]
        start_deg = props.get("start_angle", 0)
        sweep_deg = props.get("sweep_angle", 90)
        start_rad = math.radians(start_deg)
        end_rad = math.radians(start_deg + sweep_deg)
        ax_var = em.new_var("ax")
        em.line(f"const {ax_var} = new oc.gp_Ax2_1();")
        circ_var = em.new_var("circ")
        em.line(f"const {circ_var} = new oc.gp_Circ_2({ax_var}, {r});")
        em.line(
            f"const {var} = new oc.BRepBuilderAPI_MakeEdge_10("
            f"{circ_var}, {start_rad}, {end_rad}).Shape();"
        )

    elif node.primitive_type == PrimitiveType.CURVE_BEZIER_SEGMENT:
        pts = [props["start"], props["start_handle"], props["end_handle"], props["end"]]
        arr_var = em.new_var("poles")
        em.line(f"const {arr_var} = new oc.TColgp_Array1OfPnt_2(1, 4);")
        for i, pt in enumerate(pts, 1):
            em.line(f"{arr_var}.SetValue({i}, new oc.gp_Pnt_3({pt[0]}, {pt[1]}, {pt[2]}));")
        bez_var = em.new_var("bez")
        em.line(f"const {bez_var} = new oc.Geom_BezierCurve_1({arr_var});")
        handle_var = em.new_var("h")
        em.line(f"const {handle_var} = new oc.Handle_Geom_BezierCurve_2({bez_var});")
        em.line(f"const {var} = new oc.BRepBuilderAPI_MakeEdge_24({handle_var}).Shape();")

    elif node.primitive_type == PrimitiveType.CURVE_QUADRATIC_BEZIER:
        pts = [props["start"], props["middle"], props["end"]]
        arr_var = em.new_var("poles")
        em.line(f"const {arr_var} = new oc.TColgp_Array1OfPnt_2(1, 3);")
        for i, pt in enumerate(pts, 1):
            em.line(f"{arr_var}.SetValue({i}, new oc.gp_Pnt_3({pt[0]}, {pt[1]}, {pt[2]}));")
        bez_var = em.new_var("bez")
        em.line(f"const {bez_var} = new oc.Geom_BezierCurve_1({arr_var});")
        handle_var = em.new_var("h")
        em.line(f"const {handle_var} = new oc.Handle_Geom_BezierCurve_2({bez_var});")
        em.line(f"const {var} = new oc.BRepBuilderAPI_MakeEdge_24({handle_var}).Shape();")

    elif node.primitive_type == PrimitiveType.CURVE_STAR:
        n_pts = int(props.get("points", 8))
        inner_r = props.get("inner_radius", 1.0)
        outer_r = props.get("outer_radius", 2.0)
        wire_var = em.new_var("wire")
        em.line(f"const {wire_var}_b = new oc.BRepBuilderAPI_MakeWire_1();")
        total = n_pts * 2
        for i in range(total):
            angle = 2 * math.pi * i / total
            r = outer_r if i % 2 == 0 else inner_r
            x, y = r * math.cos(angle), r * math.sin(angle)
            angle_next = 2 * math.pi * ((i + 1) % total) / total
            r_next = outer_r if (i + 1) % 2 == 0 else inner_r
            xn, yn = r_next * math.cos(angle_next), r_next * math.sin(angle_next)
            e_var = em.new_var("e")
            em.line(
                f"const {e_var} = new oc.BRepBuilderAPI_MakeEdge_3("
                f"new oc.gp_Pnt_3({x}, {y}, 0), "
                f"new oc.gp_Pnt_3({xn}, {yn}, 0)).Edge();"
            )
            em.line(f"{wire_var}_b.Add_1({e_var});")
        em.line(f"const {wire_var} = {wire_var}_b.Wire();")
        em.line(f"const {var} = oc.TopoDS.prototype.constructor.Wire_1({wire_var});")

    elif node.primitive_type == PrimitiveType.CURVE_SPIRAL:
        em.comment("Spiral: not directly supported in OCCT, approximated as helix edge")
        rotations = props.get("rotations", 2)
        start_r = props.get("start_radius", 1.0)
        end_r = props.get("end_radius", 2.0)
        h = props.get("height", 2.0)
        res = int(props.get("resolution", 32))
        total_pts = int(rotations * res)
        if total_pts < 2:
            total_pts = 2
        wire_var = em.new_var("wire")
        em.line(f"const {wire_var}_b = new oc.BRepBuilderAPI_MakeWire_1();")
        for i in range(total_pts):
            t = i / (total_pts - 1)
            angle = 2 * math.pi * rotations * t
            r = start_r + (end_r - start_r) * t
            x, y, z = r * math.cos(angle), r * math.sin(angle), h * t
            t2 = (i + 1) / (total_pts - 1) if i < total_pts - 1 else 1.0
            angle2 = 2 * math.pi * rotations * t2
            r2 = start_r + (end_r - start_r) * t2
            x2, y2, z2 = r2 * math.cos(angle2), r2 * math.sin(angle2), h * t2
            if i < total_pts - 1:
                e_var = em.new_var("e")
                em.line(
                    f"const {e_var} = new oc.BRepBuilderAPI_MakeEdge_3("
                    f"new oc.gp_Pnt_3({x}, {y}, {z}), "
                    f"new oc.gp_Pnt_3({x2}, {y2}, {z2})).Edge();"
                )
                em.line(f"{wire_var}_b.Add_1({e_var});")
        em.line(f"const {wire_var} = {wire_var}_b.Wire();")
        em.line(f"const {var} = oc.TopoDS.prototype.constructor.Wire_1({wire_var});")

    elif node.primitive_type == PrimitiveType.CURVE_QUADRILATERAL:
        w = props.get("width", 2.0)
        h = props.get("height", 2.0)
        hw, hh = w / 2, h / 2
        corners = [(-hw, -hh, 0), (hw, -hh, 0), (hw, hh, 0), (-hw, hh, 0)]
        wire_var = em.new_var("wire")
        em.line(f"const {wire_var}_b = new oc.BRepBuilderAPI_MakeWire_1();")
        for i in range(4):
            p1 = corners[i]
            p2 = corners[(i + 1) % 4]
            e_var = em.new_var("e")
            em.line(
                f"const {e_var} = new oc.BRepBuilderAPI_MakeEdge_3("
                f"new oc.gp_Pnt_3({p1[0]}, {p1[1]}, {p1[2]}), "
                f"new oc.gp_Pnt_3({p2[0]}, {p2[1]}, {p2[2]})).Edge();"
            )
            em.line(f"{wire_var}_b.Add_1({e_var});")
        em.line(f"const {wire_var} = {wire_var}_b.Wire();")
        em.line(f"const {var} = oc.TopoDS.prototype.constructor.Wire_1({wire_var});")

    else:
        em.comment(f"Unsupported primitive: {node.primitive_type.name}")
        em.line(f"const {var} = new oc.TopoDS_Shape();")

    if node.label:
        em.comment(f"label: {node.label}")

    return var


def _compile_boolean(node: IRBoolean, em: _Emitter) -> str:
    child_vars = [_compile_node(c, em) for c in node.children]

    if not child_vars:
        var = em.new_var("shape")
        em.line(f"const {var} = new oc.TopoDS_Shape();")
        return var

    if len(child_vars) == 1:
        return child_vars[0]

    if node.operation == BooleanOp.UNION:
        result = child_vars[0]
        for cv in child_vars[1:]:
            var = em.new_var("fuse")
            em.line(f"const {var} = new oc.BRepAlgoAPI_Fuse_3({result}, {cv}).Shape();")
            result = var
        return result

    elif node.operation == BooleanOp.DIFFERENCE:
        result = child_vars[0]
        for cv in child_vars[1:]:
            var = em.new_var("cut")
            em.line(f"const {var} = new oc.BRepAlgoAPI_Cut_3({result}, {cv}).Shape();")
            result = var
        return result

    else:  # INTERSECT
        result = child_vars[0]
        for cv in child_vars[1:]:
            var = em.new_var("common")
            em.line(f"const {var} = new oc.BRepAlgoAPI_Common_3({result}, {cv}).Shape();")
            result = var
        return result


def _compile_transform(node: IRTransform, em: _Emitter) -> str:
    child_var = _compile_node(node.child, em) if node.child else None

    if child_var is None:
        var = em.new_var("shape")
        em.line(f"const {var} = new oc.TopoDS_Shape();")
        return var

    current = child_var

    # Apply translation
    if node.translation is not None:
        tx, ty, tz = node.translation
        if tx != 0 or ty != 0 or tz != 0:
            trsf_var = em.new_var("trsf")
            em.line(f"const {trsf_var} = new oc.gp_Trsf_1();")
            em.line(f"{trsf_var}.SetTranslation_1(new oc.gp_Vec_4({tx}, {ty}, {tz}));")
            var = em.new_var("shape")
            em.line(
                f"const {var} = new oc.BRepBuilderAPI_Transform_2("
                f"{current}, {trsf_var}, true).Shape();"
            )
            current = var

    # Apply rotation (degrees → radians, sequential X → Y → Z)
    if node.rotation is not None:
        rx, ry, rz = node.rotation
        axes = [
            (rx, "1, 0, 0"),
            (ry, "0, 1, 0"),
            (rz, "0, 0, 1"),
        ]
        for angle_deg, dir_args in axes:
            if angle_deg != 0:
                angle_rad = angle_deg * math.pi / 180.0
                trsf_var = em.new_var("trsf")
                em.line(f"const {trsf_var} = new oc.gp_Trsf_1();")
                em.line(
                    f"{trsf_var}.SetRotation_1("
                    f"new oc.gp_Ax1_2(new oc.gp_Pnt_1(), "
                    f"new oc.gp_Dir_4({dir_args})), {angle_rad});"
                )
                var = em.new_var("shape")
                em.line(
                    f"const {var} = new oc.BRepBuilderAPI_Transform_2("
                    f"{current}, {trsf_var}, true).Shape();"
                )
                current = var

    # Apply scale (uniform only in OCCT via gp_Trsf)
    if node.scale is not None:
        sx, sy, sz = node.scale
        if sx == sy == sz:
            if sx != 1.0:
                trsf_var = em.new_var("trsf")
                em.line(f"const {trsf_var} = new oc.gp_Trsf_1();")
                em.line(f"{trsf_var}.SetScaleFactor({sx});")
                var = em.new_var("shape")
                em.line(
                    f"const {var} = new oc.BRepBuilderAPI_Transform_2("
                    f"{current}, {trsf_var}, true).Shape();"
                )
                current = var
        else:
            # Non-uniform scale via gp_GTrsf
            gtrsf_var = em.new_var("gtrsf")
            em.line(f"const {gtrsf_var} = new oc.gp_GTrsf_1();")
            em.line(f"{gtrsf_var}.SetValue(1, 1, {sx});")
            em.line(f"{gtrsf_var}.SetValue(2, 2, {sy});")
            em.line(f"{gtrsf_var}.SetValue(3, 3, {sz});")
            var = em.new_var("shape")
            em.line(
                f"const {var} = new oc.BRepBuilderAPI_GTransform_2("
                f"{current}, {gtrsf_var}, true).Shape();"
            )
            current = var

    if node.label:
        em.comment(f"label: {node.label}")

    return current


def _compile_set_position(node: IRSetPosition, em: _Emitter) -> str:
    child_var = _compile_node(node.child, em) if node.child else None

    if child_var is None:
        var = em.new_var("shape")
        em.line(f"const {var} = new oc.TopoDS_Shape();")
        return var

    ox, oy, oz = node.offset
    if ox == 0 and oy == 0 and oz == 0:
        return child_var

    trsf_var = em.new_var("trsf")
    em.line(f"const {trsf_var} = new oc.gp_Trsf_1();")
    em.line(f"{trsf_var}.SetTranslation_1(new oc.gp_Vec_4({ox}, {oy}, {oz}));")
    var = em.new_var("shape")
    em.line(
        f"const {var} = new oc.BRepBuilderAPI_Transform_2("
        f"{child_var}, {trsf_var}, true).Shape();"
    )
    return var


def _compile_join(node: IRJoin, em: _Emitter) -> str:
    child_vars = [_compile_node(c, em) for c in node.children]

    if not child_vars:
        var = em.new_var("shape")
        em.line(f"const {var} = new oc.TopoDS_Shape();")
        return var

    if len(child_vars) == 1:
        return child_vars[0]

    compound_var = em.new_var("compound")
    builder_var = em.new_var("builder")
    em.line(f"const {compound_var} = new oc.TopoDS_Compound();")
    em.line(f"const {builder_var} = new oc.BRep_Builder();")
    em.line(f"{builder_var}.MakeCompound({compound_var});")
    for cv in child_vars:
        em.line(f"{builder_var}.Add({compound_var}, {cv});")

    return compound_var


def _compile_instance_on_points(node: IRInstanceOnPoints, em: _Emitter) -> str:
    """Approximation: place instance at origin of each point in points geometry."""
    instance_var = _compile_node(node.instance, em) if node.instance else None
    points_var = _compile_node(node.points, em) if node.points else None

    if instance_var is None or points_var is None:
        var = em.new_var("shape")
        em.line(f"const {var} = new oc.TopoDS_Shape();")
        return var

    em.comment("Instance on points: compound of translated copies")
    compound_var = em.new_var("compound")
    builder_var = em.new_var("builder")
    exp_var = em.new_var("exp")
    em.line(f"const {compound_var} = new oc.TopoDS_Compound();")
    em.line(f"const {builder_var} = new oc.BRep_Builder();")
    em.line(f"{builder_var}.MakeCompound({compound_var});")
    em.line(f"const {exp_var} = new oc.TopExp_Explorer_2(")
    em.line(f"  {points_var}, oc.TopAbs_ShapeEnum.TopAbs_VERTEX, oc.TopAbs_ShapeEnum.TopAbs_SHAPE);")
    loop_var = em.new_var("iter")
    em.line(f"for (let {loop_var} = {exp_var}; {loop_var}.More(); {loop_var}.Next()) {{")
    em.line(f"  const vtx = oc.TopoDS.prototype.constructor.Vertex_1({loop_var}.Current());")
    em.line(f"  const pt = oc.BRep_Tool.Pnt(vtx);")
    em.line(f"  const t = new oc.gp_Trsf_1();")
    em.line(f"  t.SetTranslation_2(new oc.gp_Pnt_1(), pt);")
    em.line(f"  const copy = new oc.BRepBuilderAPI_Transform_2({instance_var}, t, true).Shape();")
    em.line(f"  {builder_var}.Add({compound_var}, copy);")
    em.line(f"}}")

    return compound_var


def _compile_geometry_op(node: IRGeometryOp, em: _Emitter) -> str:
    child_var = _compile_node(node.child, em) if node.child else None
    props = node.properties

    # Fillet
    if node.op_type == "GeometryNodeFilletCurve" and child_var:
        radius = props.get("radius", props.get("count", 1.0))
        var = em.new_var("fillet")
        em.line(f"const {var}_mk = new oc.BRepFilletAPI_MakeFillet(")
        em.line(f"  {child_var}, oc.ChFi3d_FilletShape.ChFi3d_Rational);")
        exp_var = em.new_var("exp")
        em.line(f"const {exp_var} = new oc.TopExp_Explorer_2(")
        em.line(f"  {child_var}, oc.TopAbs_ShapeEnum.TopAbs_EDGE, oc.TopAbs_ShapeEnum.TopAbs_SHAPE);")
        em.line(f"for (; {exp_var}.More(); {exp_var}.Next()) {{")
        em.line(f"  {var}_mk.Add_2({radius}, oc.TopoDS.prototype.constructor.Edge_1({exp_var}.Current()));")
        em.line(f"}}")
        em.line(f"const {var} = {var}_mk.Shape();")
        return var

    # Extrude (prism along Z by offset_scale)
    if node.op_type == "GeometryNodeExtrudeMesh" and child_var:
        offset = props.get("offset_scale", 1.0)
        var = em.new_var("extrude")
        em.line(
            f"const {var} = new oc.BRepPrimAPI_MakePrism_1("
            f"{child_var}, new oc.gp_Vec_4(0, 0, {offset}), false, true).Shape();"
        )
        return var

    # Fill curve → make face from wire
    if node.op_type == "GeometryNodeFillCurve" and child_var:
        var = em.new_var("face")
        em.line(f"const {var}_wire = oc.TopoDS.prototype.constructor.Wire_1({child_var});")
        em.line(f"const {var} = new oc.BRepBuilderAPI_MakeFace_15({var}_wire, true).Shape();")
        return var

    # Curve to mesh (pipe/sweep)
    if node.op_type == "GeometryNodeCurveToMesh" and child_var:
        profile_node = node.extra_children.get("Profile Curve")
        if profile_node:
            profile_var = _compile_node(profile_node, em)
            var = em.new_var("pipe")
            em.line(f"const {var}_wire = oc.TopoDS.prototype.constructor.Wire_1({child_var});")
            em.line(f"const {var}_profile = oc.TopoDS.prototype.constructor.Wire_1({profile_var});")
            em.line(
                f"const {var} = new oc.BRepOffsetAPI_MakePipe_1("
                f"{var}_wire, {var}_profile).Shape();"
            )
            return var

    # Convex hull
    if node.op_type == "GeometryNodeConvexHull" and child_var:
        em.comment("Convex hull: not directly available in OCCT, passing through")

    # Generic fallback: pass through child with a comment
    if child_var:
        em.comment(f"Unsupported geometry op: {node.op_type} — passing child through")
        return child_var

    var = em.new_var("shape")
    em.line(f"const {var} = new oc.TopoDS_Shape();")
    return var


def _compile_separate_components(node: IRSeparateComponents, em: _Emitter) -> str:
    child_var = _compile_node(node.child, em) if node.child else None
    if child_var:
        em.comment(f"SeparateComponents({node.component}): passing child through")
        return child_var
    var = em.new_var("shape")
    em.line(f"const {var} = new oc.TopoDS_Shape();")
    return var


def _compile_math_op(node: IRMathOp, em: _Emitter) -> str:
    em.comment(f"Math op ({node.operation}) — not applicable in BREP context")
    var = em.new_var("val")
    em.line(f"const {var} = 0;")
    return var


def _compile_field_input(node, em: _Emitter) -> str:
    em.comment(f"Field input ({node.field_type}) — not applicable in BREP context")
    var = em.new_var("val")
    em.line(f"const {var} = 0;")
    return var


def _compile_output(node: IROutput, em: _Emitter) -> str:
    child_var = _compile_node(node.child, em) if node.child else None
    if child_var:
        return child_var
    var = em.new_var("shape")
    em.line(f"const {var} = new oc.TopoDS_Shape();")
    return var


# ---------------------------------------------------------------------------
# Dispatch
# ---------------------------------------------------------------------------


def _compile_node(node: IRNode, em: _Emitter) -> str:
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
    if isinstance(node, IRMathOp):
        return _compile_math_op(node, em)
    if isinstance(node, IRValue):
        return _compile_value(node, em)
    if isinstance(node, IRVector):
        return _compile_vector(node, em)
    # Field inputs
    from ...ir.nodes import IRFieldInput
    if isinstance(node, IRFieldInput):
        return _compile_field_input(node, em)
    raise TypeError(f"Unknown IR node type: {type(node).__name__}")


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def compile_to_source(graph: IRGraph) -> str:
    """Compile an IR graph to a standalone JavaScript/opencascade.js module."""
    em = _Emitter()

    em.comment("Auto-generated by Tanuki compiler (OpenCascade.js backend)")
    em.comment(f"Model: {graph.name}")
    em.blank()

    em.line("/**")
    em.line(f" * Build the \"{graph.name}\" model using OpenCascade.js.")
    em.line(" * @param {object} oc - Initialised opencascade.js module instance")
    em.line(" * @returns {TopoDS_Shape}")
    em.line(" */")
    em.line(f"export function setup_{graph.name.replace('-', '_')}(oc) {{")

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
        em.line("  return new oc.TopoDS_Shape();")

    em.line("}")
    em.blank()

    return em.source()


def compile_to_script(graph: IRGraph, output_path: str | Path) -> Path:
    """Compile an IR graph and write the result to a .js file."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(compile_to_source(graph))
    return path
