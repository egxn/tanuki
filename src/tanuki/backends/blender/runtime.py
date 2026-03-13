"""Blender runtime — execute an IR graph directly via bpy.

This module is only usable inside a running Blender instance.
It mirrors the compiler's logic but executes bpy calls directly
instead of generating source code strings.
"""

from __future__ import annotations

import math

from ...ir.graph import IRGraph
from ...ir.nodes import (
    BooleanOp,
    IRBoolean,
    IRGeometryOp,
    IRInstanceOnPoints,
    IRJoin,
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


_PRIMITIVE_BPY_TYPE: dict[PrimitiveType, str] = {
    PrimitiveType.CUBE: "GeometryNodeMeshCube",
    PrimitiveType.SPHERE: "GeometryNodeMeshUVSphere",
    PrimitiveType.CYLINDER: "GeometryNodeMeshCylinder",
    PrimitiveType.CONE: "GeometryNodeMeshCone",
    PrimitiveType.POINT: "GeometryNodePoints",
    PrimitiveType.CIRCLE: "GeometryNodeMeshCircle",
    PrimitiveType.GRID: "GeometryNodeMeshGrid",
    PrimitiveType.ICO_SPHERE: "GeometryNodeMeshIcoSphere",
    PrimitiveType.LINE: "GeometryNodeMeshLine",
    PrimitiveType.CURVE_ARC: "GeometryNodeCurveArc",
    PrimitiveType.CURVE_CIRCLE: "GeometryNodeCurvePrimitiveCircle",
    PrimitiveType.CURVE_LINE: "GeometryNodeCurvePrimitiveLine",
    PrimitiveType.CURVE_QUADRILATERAL: "GeometryNodeCurvePrimitiveQuadrilateral",
    PrimitiveType.CURVE_STAR: "GeometryNodeCurveStar",
    PrimitiveType.CURVE_SPIRAL: "GeometryNodeCurveSpiral",
}

_BOOLEAN_OP_STR: dict[BooleanOp, str] = {
    BooleanOp.UNION: "UNION",
    BooleanOp.DIFFERENCE: "DIFFERENCE",
    BooleanOp.INTERSECT: "INTERSECT",
}

_GEOMETRY_OUTPUT: dict[PrimitiveType, str] = {
    PrimitiveType.CUBE: "Mesh",
    PrimitiveType.SPHERE: "Mesh",
    PrimitiveType.CYLINDER: "Mesh",
    PrimitiveType.CONE: "Mesh",
    PrimitiveType.POINT: "Points",
    PrimitiveType.CIRCLE: "Mesh",
    PrimitiveType.GRID: "Mesh",
    PrimitiveType.ICO_SPHERE: "Mesh",
    PrimitiveType.LINE: "Mesh",
    PrimitiveType.CURVE_ARC: "Curve",
    PrimitiveType.CURVE_CIRCLE: "Curve",
    PrimitiveType.CURVE_LINE: "Curve",
    PrimitiveType.CURVE_QUADRILATERAL: "Curve",
    PrimitiveType.CURVE_STAR: "Curve",
    PrimitiveType.CURVE_SPIRAL: "Curve",
}

# Geometry op → input socket name for the main child
_GEOM_OP_INPUT: dict[str, str] = {
    "GeometryNodeExtrudeMesh": "Mesh",
    "GeometryNodeSubdivideMesh": "Mesh",
    "GeometryNodeSubdivisionSurface": "Mesh",
    "GeometryNodeSetShadeSmooth": "Mesh",
    "GeometryNodeMergeByDistance": "Mesh",
    "GeometryNodeDualMesh": "Mesh",
    "GeometryNodeMeshToCurve": "Mesh",
    "GeometryNodeMeshToPoints": "Mesh",
    "GeometryNodeMeshToVolume": "Mesh",
    "GeometryNodeSetMeshNormal": "Mesh",
    "GeometryNodeCurveToMesh": "Curve",
    "GeometryNodeVolumeToMesh": "Volume",
    "GeometryNodeRealizeInstances": "Geometry",
    "GeometryNodeRotateInstances": "Instances",
    "GeometryNodeScaleInstances": "Instances",
    "GeometryNodeTranslateInstances": "Instances",
}

# Geometry op → output socket name
_GEOM_OP_OUTPUT: dict[str, str] = {
    "GeometryNodeExtrudeMesh": "Mesh",
    "GeometryNodeSubdivideMesh": "Mesh",
    "GeometryNodeSubdivisionSurface": "Mesh",
    "GeometryNodeSetShadeSmooth": "Geometry",
    "GeometryNodeMergeByDistance": "Geometry",
    "GeometryNodeDualMesh": "Dual Mesh",
    "GeometryNodeMeshToCurve": "Curve",
    "GeometryNodeMeshToPoints": "Points",
    "GeometryNodeMeshToVolume": "Volume",
    "GeometryNodeSetMeshNormal": "Mesh",
    "GeometryNodeCurveToMesh": "Mesh",
    "GeometryNodeVolumeToMesh": "Mesh",
    "GeometryNodeRealizeInstances": "Geometry",
    "GeometryNodeRotateInstances": "Instances",
    "GeometryNodeScaleInstances": "Instances",
    "GeometryNodeTranslateInstances": "Instances",
}

_GEOM_OP_SCALAR: dict[str, str] = {
    "offset_scale": "Offset Scale",
    "level": "Level",
    "distance": "Distance",
    "radius": "Radius",
    "density": "Density",
    "voxel_size": "Voxel Size",
    "voxel_amount": "Voxel Amount",
    "interior_band_width": "Interior Band Width",
    "threshold": "Threshold",
    "adaptivity": "Adaptivity",
    "profile_scale": "Scale",
}

_GEOM_OP_BOOL: dict[str, str] = {
    "shade_smooth": "Shade Smooth",
    "keep_boundaries": "Keep Boundaries",
    "fill_caps": "Fill Caps",
    "remove_custom": "Remove Custom",
    "edge_sharpness": "Edge Sharpness",
    "face_sharpness": "Face Sharpness",
}


class _Runtime:
    """Holds the bpy node_tree and manages layout during execution."""

    def __init__(self, node_tree) -> None:
        self.node_tree = node_tree
        self._grid_x = 0
        self._grid_y = 0
        self._node_width = 180
        self._node_height = 200

    def next_location(self) -> tuple[int, int]:
        loc = (self._grid_x * self._node_width, self._grid_y * self._node_height)
        self._grid_x += 1
        return loc

    def next_row(self) -> None:
        self._grid_y += 1
        self._grid_x = 0

    def new_node(self, bpy_type: str, label: str = ""):
        node = self.node_tree.nodes.new(bpy_type)
        node.location = self.next_location()
        if label:
            node.label = label
        return node

    def link(self, from_node, from_socket, to_node, to_socket) -> None:
        out = (from_node.outputs[from_socket] if isinstance(from_socket, (int, str))
               else from_socket)
        inp = (to_node.inputs[to_socket] if isinstance(to_socket, (int, str))
               else to_socket)
        self.node_tree.links.new(out, inp)


def _get_geo_socket(node: IRNode) -> str:
    if isinstance(node, IRPrimitive):
        return _GEOMETRY_OUTPUT.get(node.primitive_type, "Geometry")
    if isinstance(node, IRBoolean):
        return "Mesh"
    if isinstance(node, IRJoin):
        return "Geometry"
    if isinstance(node, IRInstanceOnPoints):
        return "Instances"
    if isinstance(node, IRGeometryOp):
        return _GEOM_OP_OUTPUT.get(node.op_type, "Geometry")
    if isinstance(node, IRSeparateComponents):
        return node.component
    return "Geometry"


def _exec_node(node: IRNode, rt: _Runtime):
    """Dispatch execution. Returns the created bpy node."""
    if isinstance(node, IROutput):
        return _exec_output(node, rt)
    if isinstance(node, IRPrimitive):
        return _exec_primitive(node, rt)
    if isinstance(node, IRBoolean):
        return _exec_boolean(node, rt)
    if isinstance(node, IRTransform):
        return _exec_transform(node, rt)
    if isinstance(node, IRSetPosition):
        return _exec_set_position(node, rt)
    if isinstance(node, IRJoin):
        return _exec_join(node, rt)
    if isinstance(node, IRInstanceOnPoints):
        return _exec_instance(node, rt)
    if isinstance(node, IRGeometryOp):
        return _exec_geometry_op(node, rt)
    raise TypeError(f"Unknown IR node: {type(node).__name__}")


def _exec_value(value: float, label: str, rt: _Runtime):
    v = rt.new_node("ShaderNodeValue", label)
    v.outputs[0].default_value = value
    return v


def _exec_vector(vec: tuple, label: str, rt: _Runtime):
    v = rt.new_node("FunctionNodeInputVector", label)
    v.vector = vec
    return v


def _exec_primitive(node: IRPrimitive, rt: _Runtime):
    rt.next_row()
    bpy_type = _PRIMITIVE_BPY_TYPE[node.primitive_type]
    bpy_node = rt.new_node(bpy_type, node.label)
    props = node.properties

    if node.primitive_type == PrimitiveType.CUBE:
        sv = _exec_vector(props["size"], f"{node.label} size", rt)
        rt.link(sv, "Vector", bpy_node, "Size")

    elif node.primitive_type == PrimitiveType.CYLINDER:
        rv = _exec_value(props["radius"], f"{node.label} radius", rt)
        dv = _exec_value(props["depth"], f"{node.label} depth", rt)
        rt.link(rv, "Value", bpy_node, "Radius")
        rt.link(dv, "Value", bpy_node, "Depth")
        if "vertices" in props:
            bpy_node.inputs["Vertices"].default_value = props["vertices"]

    elif node.primitive_type == PrimitiveType.CONE:
        r1 = _exec_value(props["radius_top"], f"{node.label} radius top", rt)
        r2 = _exec_value(props["radius_bottom"], f"{node.label} radius bottom", rt)
        dv = _exec_value(props["depth"], f"{node.label} depth", rt)
        rt.link(r1, "Value", bpy_node, "Radius Top")
        rt.link(r2, "Value", bpy_node, "Radius Bottom")
        rt.link(dv, "Value", bpy_node, "Depth")

    elif node.primitive_type == PrimitiveType.SPHERE:
        rv = _exec_value(props["radius"], f"{node.label} radius", rt)
        rt.link(rv, "Value", bpy_node, "Radius")
        if "segments" in props:
            bpy_node.inputs["Segments"].default_value = props["segments"]
        if "rings" in props:
            bpy_node.inputs["Rings"].default_value = props["rings"]

    elif node.primitive_type == PrimitiveType.POINT:
        pos = props.get("position", (0, 0, 0))
        bpy_node.inputs["Position"].default_value = list(pos)

    elif node.primitive_type == PrimitiveType.CIRCLE:
        bpy_node.inputs["Vertices"].default_value = props.get("vertices", 32)
        rv = _exec_value(props["radius"], f"{node.label} radius", rt)
        rt.link(rv, "Value", bpy_node, "Radius")
        if "fill_type" in props:
            bpy_node.fill_type = props["fill_type"]

    elif node.primitive_type == PrimitiveType.GRID:
        bpy_node.inputs["Size X"].default_value = props.get("size_x", 1.0)
        bpy_node.inputs["Size Y"].default_value = props.get("size_y", 1.0)
        bpy_node.inputs["Vertices X"].default_value = props.get("vertices_x", 10)
        bpy_node.inputs["Vertices Y"].default_value = props.get("vertices_y", 10)

    elif node.primitive_type == PrimitiveType.ICO_SPHERE:
        rv = _exec_value(props["radius"], f"{node.label} radius", rt)
        rt.link(rv, "Value", bpy_node, "Radius")
        if "subdivisions" in props:
            bpy_node.inputs["Subdivisions"].default_value = props["subdivisions"]

    elif node.primitive_type == PrimitiveType.LINE:
        bpy_node.inputs["Count"].default_value = props.get("count", 10)
        if "start_location" in props:
            bpy_node.inputs["Start Location"].default_value = list(props["start_location"])
        if "end_location" in props:
            bpy_node.inputs["End Location"].default_value = list(props["end_location"])

    elif node.primitive_type == PrimitiveType.CURVE_ARC:
        bpy_node.inputs["Resolution"].default_value = props.get("resolution", 16)
        rv = _exec_value(props["radius"], f"{node.label} radius", rt)
        rt.link(rv, "Value", bpy_node, "Radius")
        if "start_angle" in props:
            bpy_node.inputs["Start Angle"].default_value = props["start_angle"]
        if "sweep_angle" in props:
            bpy_node.inputs["Sweep Angle"].default_value = props["sweep_angle"]

    elif node.primitive_type == PrimitiveType.CURVE_CIRCLE:
        bpy_node.inputs["Resolution"].default_value = props.get("resolution", 32)
        rv = _exec_value(props["radius"], f"{node.label} radius", rt)
        rt.link(rv, "Value", bpy_node, "Radius")

    elif node.primitive_type == PrimitiveType.CURVE_LINE:
        if "start" in props:
            bpy_node.inputs["Start"].default_value = list(props["start"])
        if "end" in props:
            bpy_node.inputs["End"].default_value = list(props["end"])

    elif node.primitive_type == PrimitiveType.CURVE_QUADRILATERAL:
        bpy_node.inputs["Width"].default_value = props.get("width", 1.0)
        bpy_node.inputs["Height"].default_value = props.get("height", 1.0)

    elif node.primitive_type == PrimitiveType.CURVE_STAR:
        bpy_node.inputs["Points"].default_value = props.get("points", 8)
        bpy_node.inputs["Inner Radius"].default_value = props.get("inner_radius", 0.5)
        bpy_node.inputs["Outer Radius"].default_value = props.get("outer_radius", 1.0)

    elif node.primitive_type == PrimitiveType.CURVE_SPIRAL:
        bpy_node.inputs["Resolution"].default_value = props.get("resolution", 128)
        bpy_node.inputs["Rotations"].default_value = props.get("rotations", 2.0)
        bpy_node.inputs["Start Radius"].default_value = props.get("start_radius", 0.5)
        bpy_node.inputs["End Radius"].default_value = props.get("end_radius", 1.5)
        bpy_node.inputs["Height"].default_value = props.get("height", 2.0)

    return bpy_node


def _exec_boolean(node: IRBoolean, rt: _Runtime):
    child_bpy = [(c, _exec_node(c, rt)) for c in node.children]
    rt.next_row()
    bpy_node = rt.new_node("GeometryNodeMeshBoolean", node.label)
    bpy_node.operation = _BOOLEAN_OP_STR[node.operation]
    bpy_node.solver = "EXACT"

    if node.operation == BooleanOp.DIFFERENCE:
        ir_c, bpy_c = child_bpy[0]
        rt.link(bpy_c, _get_geo_socket(ir_c), bpy_node, 0)
        for ir_c, bpy_c in child_bpy[1:]:
            rt.link(bpy_c, _get_geo_socket(ir_c), bpy_node, 1)
    else:
        for ir_c, bpy_c in child_bpy:
            rt.link(bpy_c, _get_geo_socket(ir_c), bpy_node, 1)

    return bpy_node


def _exec_transform(node: IRTransform, rt: _Runtime):
    child_bpy = _exec_node(node.child, rt) if node.child else None
    child_sock = _get_geo_socket(node.child) if node.child else "Geometry"
    rt.next_row()
    bpy_node = rt.new_node("GeometryNodeTransform", node.label)

    if child_bpy:
        rt.link(child_bpy, child_sock, bpy_node, "Geometry")
    if node.translation:
        tv = _exec_vector(node.translation, f"{node.label} translation", rt)
        rt.link(tv, "Vector", bpy_node, "Translation")
    if node.rotation:
        rads = tuple(c * math.pi / 180.0 for c in node.rotation)
        rv = _exec_vector(rads, f"{node.label} rotation", rt)
        rt.link(rv, "Vector", bpy_node, "Rotation")
    if node.scale:
        sv = _exec_vector(node.scale, f"{node.label} scale", rt)
        rt.link(sv, "Vector", bpy_node, "Scale")

    return bpy_node


def _exec_set_position(node: IRSetPosition, rt: _Runtime):
    child_bpy = _exec_node(node.child, rt) if node.child else None
    child_sock = _get_geo_socket(node.child) if node.child else "Geometry"
    rt.next_row()
    bpy_node = rt.new_node("GeometryNodeSetPosition", node.label)

    if child_bpy:
        rt.link(child_bpy, child_sock, bpy_node, "Geometry")
    ov = _exec_vector(node.offset, f"{node.label} offset", rt)
    rt.link(ov, "Vector", bpy_node, "Offset")

    return bpy_node


def _exec_join(node: IRJoin, rt: _Runtime):
    child_bpy = [(c, _exec_node(c, rt)) for c in node.children]
    rt.next_row()
    bpy_node = rt.new_node("GeometryNodeJoinGeometry", node.label)
    for ir_c, bpy_c in child_bpy:
        rt.link(bpy_c, _get_geo_socket(ir_c), bpy_node, "Geometry")
    return bpy_node


def _exec_instance(node: IRInstanceOnPoints, rt: _Runtime):
    pts_bpy = _exec_node(node.points, rt) if node.points else None
    pts_sock = _get_geo_socket(node.points) if node.points else "Geometry"
    inst_bpy = _exec_node(node.instance, rt) if node.instance else None
    inst_sock = _get_geo_socket(node.instance) if node.instance else "Geometry"
    rt.next_row()
    bpy_node = rt.new_node("GeometryNodeInstanceOnPoints", node.label)
    if pts_bpy:
        rt.link(pts_bpy, pts_sock, bpy_node, "Points")
    if inst_bpy:
        rt.link(inst_bpy, inst_sock, bpy_node, "Instance")
    return bpy_node


def _exec_geometry_op(node: IRGeometryOp, rt: _Runtime):
    child_bpy = _exec_node(node.child, rt) if node.child else None
    child_sock = _get_geo_socket(node.child) if node.child else "Geometry"

    # Compile extra children (e.g. Profile Curve for Curve to Mesh)
    extra_bpy: dict[str, tuple] = {}
    for socket_name, extra_node in node.extra_children.items():
        eb = _exec_node(extra_node, rt)
        es = _get_geo_socket(extra_node)
        extra_bpy[socket_name] = (eb, es)

    rt.next_row()
    bpy_node = rt.new_node(node.op_type, node.label)

    # Enum/mode property
    if "mode" in node.properties:
        bpy_node.domain = node.properties["mode"]

    # Main geometry input
    input_sock = _GEOM_OP_INPUT.get(node.op_type, "Geometry")
    if child_bpy:
        rt.link(child_bpy, child_sock, bpy_node, input_sock)

    # Extra geometry inputs
    for socket_name, (eb, es) in extra_bpy.items():
        rt.link(eb, es, bpy_node, socket_name)

    # Scalar inputs
    for key, inp_name in _GEOM_OP_SCALAR.items():
        if key in node.properties:
            bpy_node.inputs[inp_name].default_value = node.properties[key]

    # Boolean inputs
    for key, inp_name in _GEOM_OP_BOOL.items():
        if key in node.properties:
            bpy_node.inputs[inp_name].default_value = node.properties[key]

    # Vector inputs
    _VECTOR = {"rotation": "Rotation", "scale": "Scale", "translation": "Translation"}
    for key, inp_name in _VECTOR.items():
        if key in node.properties:
            bpy_node.inputs[inp_name].default_value = node.properties[key]

    return bpy_node


def _exec_output(node: IROutput, rt: _Runtime):
    child_bpy = _exec_node(node.child, rt) if node.child else None
    rt.next_row()
    bpy_node = rt.new_node("NodeGroupOutput", "output")
    if child_bpy:
        rt.node_tree.links.new(child_bpy.outputs[0], bpy_node.inputs[0])
    return bpy_node


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def execute(graph: IRGraph) -> None:
    """Execute an IR graph directly inside Blender.

    Creates a mesh object with a Geometry Nodes modifier and builds
    the node graph by calling bpy directly.

    Must be called from within a running Blender instance.
    """
    import bpy

    name = graph.name or "TanukiModel"

    # Clean up existing object
    if name in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects[name], do_unlink=True)

    # Create base mesh
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 0))
    bpy.context.active_object.name = name
    plane = bpy.context.active_object
    modifier = plane.modifiers.new(name="GeometryNodes", type="NODES")
    bpy.ops.node.new_geometry_node_group_assign()
    node_tree = modifier.node_group

    # Clear default nodes
    for node in list(node_tree.nodes):
        node_tree.nodes.remove(node)

    # Build graph
    if graph.root:
        rt = _Runtime(node_tree)
        _exec_node(graph.root, rt)
