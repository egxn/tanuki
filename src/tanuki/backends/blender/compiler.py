"""Blender Geometry Nodes compiler — IR graph → Python bpy script.

Pure functions that translate an IR tree into a self-contained Python script
that, when executed inside Blender, builds the geometry node graph.

The generated script is standalone: it imports bpy, sets up the object, creates
all nodes, links them, and assigns an output.
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
# Mapping tables (IR types → Blender node type strings)
# ---------------------------------------------------------------------------

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
    PrimitiveType.CURVE_BEZIER_SEGMENT: "GeometryNodeCurvePrimitiveBezierSegment",
    PrimitiveType.CURVE_QUADRATIC_BEZIER: "GeometryNodeCurveQuadraticBezier",
    PrimitiveType.VOLUME_CUBE: "GeometryNodeVolumeCube",
    PrimitiveType.IMPORT_OBJ: "GeometryNodeImportOBJ",
    PrimitiveType.IMPORT_STL: "GeometryNodeImportSTL",
    PrimitiveType.IMPORT_PLY: "GeometryNodeImportPLY",
    PrimitiveType.IMPORT_CSV: "GeometryNodeImportCSV",
    PrimitiveType.IMPORT_VDB: "GeometryNodeImportVDB",
    PrimitiveType.COLLECTION_INFO: "GeometryNodeCollectionInfo",
    PrimitiveType.OBJECT_INFO: "GeometryNodeObjectInfo",
}

_BOOLEAN_OP_STR: dict[BooleanOp, str] = {
    BooleanOp.UNION: "UNION",
    BooleanOp.DIFFERENCE: "DIFFERENCE",
    BooleanOp.INTERSECT: "INTERSECT",
}

# Which output socket name carries geometry for each primitive type
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
    PrimitiveType.CURVE_BEZIER_SEGMENT: "Curve",
    PrimitiveType.CURVE_QUADRATIC_BEZIER: "Curve",
    PrimitiveType.VOLUME_CUBE: "Volume",
    PrimitiveType.IMPORT_OBJ: "Instances",
    PrimitiveType.IMPORT_STL: "Mesh",
    PrimitiveType.IMPORT_PLY: "Mesh",
    PrimitiveType.IMPORT_CSV: "Point Cloud",
    PrimitiveType.IMPORT_VDB: "Volume",
    PrimitiveType.COLLECTION_INFO: "Instances",
    PrimitiveType.OBJECT_INFO: "Geometry",
}

# Geometry op → which input socket receives the main child geometry
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
    # Instance ops (batch 4)
    "GeometryNodeGeometryToInstance": "Geometry",
    "GeometryNodeInstancesToPoints": "Instances",
    "GeometryNodeSplitToInstances": "Geometry",
    # Material ops
    "GeometryNodeSetMaterial": "Geometry",
    "GeometryNodeReplaceMaterial": "Geometry",
    "GeometryNodeSetMaterialIndex": "Geometry",
    # Volume ops
    "GeometryNodeDistributePointsInVolume": "Volume",
    "GeometryNodePointsToVolume": "Points",
    # Other ops (batch 7)
    "GeometryNodeConvexHull": "Geometry",
    "GeometryNodeDeleteGeometry": "Geometry",
    "GeometryNodeDistributePointsOnFaces": "Mesh",
    "GeometryNodeDuplicateElements": "Geometry",
    "GeometryNodeFlipFaces": "Mesh",
    "GeometryNodeScaleElements": "Geometry",
    "GeometryNodeSplitEdges": "Mesh",
    "GeometryNodeTriangulate": "Mesh",
    # Other ops (batch 8)
    "GeometryNodeBoundBox": "Geometry",
    "GeometryNodeSeparateGeometry": "Geometry",
    "GeometryNodeSetID": "Geometry",
    "GeometryNodeSetPointRadius": "Points",
    "GeometryNodeSortElements": "Geometry",
    # Attribute ops (batch 9)
    "GeometryNodeStoreNamedAttribute": "Geometry",
    "GeometryNodeRemoveAttribute": "Geometry",
    # Other ops (batch 10)
    "GeometryNodePointsToVertices": "Points",
    "GeometryNodeSetGeometryName": "Geometry",
    "GeometryNodeToolSetFaceSet": "Mesh",
    "GeometryNodeToolSetSelection": "Geometry",
    "GeometryNodeMergeLayers": "Grease Pencil",
    "GeometryNodeSetGreasePencilDepth": "Grease Pencil",
    "GeometryNodeSetGreasePencilSoftness": "Grease Pencil",
    # Other ops (batch 12)
    "GeometryNodeSwitch": "False",
    "GeometryNodeGetNamedGrid": "Volume",
    "GeometryNodeStoreNamedGrid": "Volume",
    "GeometryNodeSetGreasePencilColor": "Grease Pencil",
    "GeometryNodeViewer": "Geometry",
    # Curve operations
    "GeometryNodeFillCurve": "Curve",
    "GeometryNodeFilletCurve": "Curve",
    "GeometryNodeResampleCurve": "Curve",
    "GeometryNodeReverseCurve": "Curve",
    "GeometryNodeSubdivideCurve": "Curve",
    "GeometryNodeTrimCurve": "Curve",
    "GeometryNodeCurveToPoints": "Curve",
    "GeometryNodeDeformCurvesOnSurface": "Curves",
    "GeometryNodeSampleCurve": "Curves",
    # Curve attribute setters
    "GeometryNodeSetCurveNormal": "Curve",
    "GeometryNodeSetCurveRadius": "Curve",
    "GeometryNodeSetCurveTilt": "Curve",
    "GeometryNodeSetCurveHandlePositions": "Curve",
    "GeometryNodeCurveSetHandles": "Curve",
    "GeometryNodeSetSplineCyclic": "Geometry",
    "GeometryNodeSetSplineResolution": "Geometry",
    "GeometryNodeCurveSplineType": "Curve",
    # Batch 3 — remaining curve ops
    "GeometryNodeEdgePathsToCurves": "Mesh",
    "GeometryNodeInterpolateCurves": "Guide Curves",
    "GeometryNodePointsToCurves": "Points",
    "GeometryNodeCurvesToGreasePencil": "Curves",
    "GeometryNodeGreasePencilToCurves": "Grease Pencil",
    "GeometryNodeStringToCurves": "Geometry",
    # Batch 14 — info/query nodes
    "GeometryNodeCurveLength": "Curve",
    "GeometryNodeAttributeDomainSize": "Geometry",
    "GeometryNodeProximity": "Geometry",
    "GeometryNodeSampleNearest": "Geometry",
    "GeometryNodeSampleIndex": "Geometry",
    "GeometryNodeAttributeStatistic": "Geometry",
    # Batch 15 — sampling + grid conversion
    "GeometryNodeRaycast": "Target Geometry",
    "GeometryNodeSampleNearestSurface": "Mesh",
    "GeometryNodeSampleUVSurface": "Mesh",
    "GeometryNodeMeshToSDFGrid": "Mesh",
    "GeometryNodeMeshToDensityGrid": "Mesh",
    # Batch 20 — grid ops, instance transform
    "GeometryNodeDistributePointsInGrid": "Grid",
    "GeometryNodeGridToMesh": "Grid",
    "GeometryNodePointsToSDFGrid": "Points",
    "GeometryNodeSetInstanceTransform": "Instances",
}

# Geometry op → which output socket carries the result geometry
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
    # Instance ops (batch 4)
    "GeometryNodeGeometryToInstance": "Instances",
    "GeometryNodeInstancesToPoints": "Points",
    "GeometryNodeSplitToInstances": "Instances",
    # Material ops
    "GeometryNodeSetMaterial": "Geometry",
    "GeometryNodeReplaceMaterial": "Geometry",
    "GeometryNodeSetMaterialIndex": "Geometry",
    # Volume ops
    "GeometryNodeDistributePointsInVolume": "Points",
    "GeometryNodePointsToVolume": "Volume",
    # Other ops (batch 7)
    "GeometryNodeConvexHull": "Convex Hull",
    "GeometryNodeDeleteGeometry": "Geometry",
    "GeometryNodeDistributePointsOnFaces": "Points",
    "GeometryNodeDuplicateElements": "Geometry",
    "GeometryNodeFlipFaces": "Mesh",
    "GeometryNodeScaleElements": "Geometry",
    "GeometryNodeSplitEdges": "Mesh",
    "GeometryNodeTriangulate": "Mesh",
    # Other ops (batch 8)
    "GeometryNodeBoundBox": "Bounding Box",
    "GeometryNodeSeparateGeometry": "Selection",
    "GeometryNodeSetID": "Geometry",
    "GeometryNodeSetPointRadius": "Points",
    "GeometryNodeSortElements": "Geometry",
    # Attribute ops (batch 9)
    "GeometryNodeStoreNamedAttribute": "Geometry",
    "GeometryNodeRemoveAttribute": "Geometry",
    # Other ops (batch 10)
    "GeometryNodePointsToVertices": "Mesh",
    "GeometryNodeSetGeometryName": "Geometry",
    "GeometryNodeToolSetFaceSet": "Mesh",
    "GeometryNodeToolSetSelection": "Geometry",
    "GeometryNodeMergeLayers": "Grease Pencil",
    "GeometryNodeSetGreasePencilDepth": "Grease Pencil",
    "GeometryNodeSetGreasePencilSoftness": "Grease Pencil",
    # Other ops (batch 12)
    "GeometryNodeSwitch": "Output",
    "GeometryNodeGetNamedGrid": "Volume",
    "GeometryNodeStoreNamedGrid": "Volume",
    "GeometryNodeSetGreasePencilColor": "Grease Pencil",
    # Curve operations
    "GeometryNodeFillCurve": "Mesh",
    "GeometryNodeFilletCurve": "Curve",
    "GeometryNodeResampleCurve": "Curve",
    "GeometryNodeReverseCurve": "Curve",
    "GeometryNodeSubdivideCurve": "Curve",
    "GeometryNodeTrimCurve": "Curve",
    "GeometryNodeCurveToPoints": "Points",
    "GeometryNodeDeformCurvesOnSurface": "Curves",
    "GeometryNodeSampleCurve": "Position",
    # Curve attribute setters
    "GeometryNodeSetCurveNormal": "Curve",
    "GeometryNodeSetCurveRadius": "Curve",
    "GeometryNodeSetCurveTilt": "Curve",
    "GeometryNodeSetCurveHandlePositions": "Curve",
    "GeometryNodeCurveSetHandles": "Curve",
    "GeometryNodeSetSplineCyclic": "Geometry",
    "GeometryNodeSetSplineResolution": "Geometry",
    "GeometryNodeCurveSplineType": "Curve",
    # Batch 3 — remaining curve ops
    "GeometryNodeEdgePathsToCurves": "Curves",
    "GeometryNodeInterpolateCurves": "Curves",
    "GeometryNodePointsToCurves": "Curves",
    "GeometryNodeCurvesToGreasePencil": "Grease Pencil",
    "GeometryNodeGreasePencilToCurves": "Curves",
    "GeometryNodeStringToCurves": "Curve Instances",
    # Batch 14 — info/query nodes
    "GeometryNodeCurveLength": "Length",
    "GeometryNodeAttributeDomainSize": "Point Count",
    "GeometryNodeProximity": "Distance",
    "GeometryNodeSampleNearest": "Index",
    "GeometryNodeSampleIndex": "Value",
    "GeometryNodeAttributeStatistic": "Mean",
    # Batch 15 — sampling + grid conversion
    "GeometryNodeRaycast": "Is Hit",
    "GeometryNodeSampleNearestSurface": "Value",
    "GeometryNodeSampleUVSurface": "Value",
    "GeometryNodeMeshToSDFGrid": "SDF Grid",
    "GeometryNodeMeshToDensityGrid": "Density Grid",
    # Batch 20 — grid ops, instance transform
    "GeometryNodeDistributePointsInGrid": "Points",
    "GeometryNodeGridToMesh": "Mesh",
    "GeometryNodePointsToSDFGrid": "SDF Grid",
    "GeometryNodeSetInstanceTransform": "Instances",
}

# Scalar property key → Blender input socket name
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
    # Curve ops
    "start": "Start",
    "end": "End",
    "factor": "Factor",
    "count": "Count",
    "cuts": "Cuts",
    "group_id": "Group ID",
    "curve_index": "Curve Index",
    # Curve attribute setters
    "tilt": "Tilt",
    "resolution": "Resolution",
    # Batch 3
    "next_vertex_index": "Next Vertex Index",
    "guide_group_id": "Guide Group ID",
    "point_group_id": "Point Group ID",
    "max_neighbors": "Max Neighbors",
    "curve_group_id": "Curve Group ID",
    "weight": "Weight",
    "size": "Size",
    "character_spacing": "Character Spacing",
    "word_spacing": "Word Spacing",
    "line_spacing": "Line Spacing",
    "text_box_width": "Text Box Width",
    "text_box_height": "Text Box Height",
    # Material ops
    "material_index": "Material Index",
    # Volume ops
    "seed": "Seed",
    "background": "Background",
    # Other ops (batch 7)
    "density_max": "Density Max",
    "density_factor": "Density Factor",
    "distance_min": "Distance Min",
    "amount": "Amount",
    "element_scale": "Scale",
    # Other ops (batch 8)
    "id_value": "ID",
    "sort_weight": "Sort Weight",
    # Attribute ops (batch 9)
    "value": "Value",
    # Other ops (batch 10)
    "face_set": "Face Set",
    "softness": "Softness",
    # Other ops (batch 12)
    "grid_value": "Grid",
    "opacity": "Opacity",
    # Batch 14 — info/query
    "attribute": "Attribute",
    "sample_group_id": "Sample Group ID",
    "index": "Index",
    # Batch 15 — sampling + grids
    "ray_length": "Ray Length",
    "gradient_width": "Gradient Width",
    "band_width": "Band Width",
}

# Boolean property key → Blender input socket name
_GEOM_OP_BOOL: dict[str, str] = {
    "shade_smooth": "Shade Smooth",
    "keep_boundaries": "Keep Boundaries",
    "fill_caps": "Fill Caps",
    "remove_custom": "Remove Custom",
    "edge_sharpness": "Edge Sharpness",
    "face_sharpness": "Face Sharpness",
    # Curve ops
    "limit_radius": "Limit Radius",
    # Curve attribute setters
    "cyclic": "Cyclic",
    # Batch 3
    "start_vertices": "Start Vertices",
    "instances_as_layers": "Instances as Layers",
    "layers_as_instances": "Layers as Instances",
    # Other ops (batch 8)
    "use_radius": "Use Radius",
    # Other ops (batch 12)
    "switch": "Switch",
    "remove": "Remove",
    # Batch 14
    "clamp": "Clamp",
}


# ---------------------------------------------------------------------------
# Code emitter — accumulates lines of Python source
# ---------------------------------------------------------------------------


class _Emitter:
    """Stateful code accumulator. Tracks variable names and node layout.

    Layout model — the main geometry chain flows left-to-right at y=0.
    Helper/input nodes for each main node are stacked above it at y > 0.

    Example for ``cube | translate | output``:
    ::
        y=280: [vec_size]  [vec_translation]
        y=0:   [  cube  ] → [ transform ] → [ output ]
    """

    def __init__(self) -> None:
        self._lines: list[str] = []
        self._var_counter = 0
        # _main_x: pixel x of the *next* group's main node (advances per group).
        self._main_x: int = 0
        # _group_main_x: pixel x reserved for the *current* group's main node.
        self._group_main_x: int = 0
        # _helper_count: number of helpers placed in the current group.
        self._helper_count: int = 0
        self._node_width: int = 300
        self._node_height: int = 280

    def line(self, text: str) -> None:
        self._lines.append(text)

    def blank(self) -> None:
        self._lines.append("")

    def new_var(self, prefix: str = "n") -> str:
        self._var_counter += 1
        return f"{prefix}_{self._var_counter}"

    def start_group(self) -> None:
        """Reserve a column slot for the next main node and reset helpers."""
        self._group_main_x = self._main_x
        self._main_x += self._node_width
        self._helper_count = 0

    def next_helper_location(self) -> tuple[int, int]:
        """Location for a helper node stacked above the current group's main node."""
        loc = (self._group_main_x, (self._helper_count + 1) * self._node_height)
        self._helper_count += 1
        return loc

    def next_main_location(self) -> tuple[int, int]:
        """Location for the current group's main node (on the main chain, y=0)."""
        return (self._group_main_x, 0)

    def source(self) -> str:
        return "\n".join(self._lines) + "\n"


# ---------------------------------------------------------------------------
# Compile functions — one per IR node type (functional dispatch)
# ---------------------------------------------------------------------------


def _compile_value(node: IRValue, em: _Emitter) -> str:
    var = em.new_var("val")
    loc = em.next_helper_location()
    em.line(f'{var} = node_tree.nodes.new("ShaderNodeValue")')
    em.line(f"{var}.location = {loc}")
    em.line(f'{var}.label = {node.label!r}')
    em.line(f"{var}.outputs[0].default_value = {node.value}")
    return var


def _compile_vector(node: IRVector, em: _Emitter) -> str:
    var = em.new_var("vec")
    loc = em.next_helper_location()
    em.line(f'{var} = node_tree.nodes.new("FunctionNodeInputVector")')
    em.line(f"{var}.location = {loc}")
    em.line(f'{var}.label = {node.label!r}')
    em.line(f"{var}.vector = {list(node.value)}")
    return var


def _compile_primitive(node: IRPrimitive, em: _Emitter) -> str:
    bpy_type = _PRIMITIVE_BPY_TYPE[node.primitive_type]
    em.start_group()
    # Reserve the variable name before emitting any helper nodes so that
    # deferred link/property lines can reference it by name.
    var = em.new_var("prim")

    props = node.properties
    # Collect link and property lines that must be emitted after the main node.
    deferred_lines: list[str] = []

    if node.primitive_type == PrimitiveType.CUBE:
        size_var = em.new_var("vec")
        size_loc = em.next_helper_location()
        em.line(f'{size_var} = node_tree.nodes.new("FunctionNodeInputVector")')
        em.line(f"{size_var}.location = {size_loc}")
        em.line(f'{size_var}.label = "{node.label} size"')
        em.line(f"{size_var}.vector = {list(props['size'])}")
        deferred_lines.append(f'node_tree.links.new({size_var}.outputs["Vector"], {var}.inputs["Size"])')

    elif node.primitive_type == PrimitiveType.CYLINDER:
        r_var = _compile_value(IRValue(value=props["radius"], label=f"{node.label} radius"), em)
        d_var = _compile_value(IRValue(value=props["depth"], label=f"{node.label} depth"), em)
        deferred_lines.append(f'node_tree.links.new({r_var}.outputs["Value"], {var}.inputs["Radius"])')
        deferred_lines.append(f'node_tree.links.new({d_var}.outputs["Value"], {var}.inputs["Depth"])')
        if "vertices" in props:
            deferred_lines.append(f'{var}.inputs["Vertices"].default_value = {props["vertices"]}')
        if "side_segments" in props:
            deferred_lines.append(f'{var}.inputs["Side Segments"].default_value = {props["side_segments"]}')

    elif node.primitive_type == PrimitiveType.CONE:
        r1_var = _compile_value(IRValue(value=props["radius_top"], label=f"{node.label} radius top"), em)
        r2_var = _compile_value(IRValue(value=props["radius_bottom"], label=f"{node.label} radius bottom"), em)
        d_var = _compile_value(IRValue(value=props["depth"], label=f"{node.label} depth"), em)
        deferred_lines.append(f'node_tree.links.new({r1_var}.outputs["Value"], {var}.inputs["Radius Top"])')
        deferred_lines.append(f'node_tree.links.new({r2_var}.outputs["Value"], {var}.inputs["Radius Bottom"])')
        deferred_lines.append(f'node_tree.links.new({d_var}.outputs["Value"], {var}.inputs["Depth"])')

    elif node.primitive_type == PrimitiveType.SPHERE:
        r_var = _compile_value(IRValue(value=props["radius"], label=f"{node.label} radius"), em)
        deferred_lines.append(f'node_tree.links.new({r_var}.outputs["Value"], {var}.inputs["Radius"])')
        if "segments" in props:
            deferred_lines.append(f'{var}.inputs["Segments"].default_value = {props["segments"]}')
        if "rings" in props:
            deferred_lines.append(f'{var}.inputs["Rings"].default_value = {props["rings"]}')

    elif node.primitive_type == PrimitiveType.POINT:
        pos = props.get("position", (0, 0, 0))
        deferred_lines.append(f'{var}.inputs["Position"].default_value = {list(pos)}')

    elif node.primitive_type == PrimitiveType.CIRCLE:
        r_var = _compile_value(IRValue(value=props["radius"], label=f"{node.label} radius"), em)
        deferred_lines.append(f'node_tree.links.new({r_var}.outputs["Value"], {var}.inputs["Radius"])')
        deferred_lines.append(f'{var}.inputs["Vertices"].default_value = {props["vertices"]}')
        deferred_lines.append(f'{var}.fill_type = "{props.get("fill_type", "NONE")}"')

    elif node.primitive_type == PrimitiveType.GRID:
        sx_var = _compile_value(IRValue(value=props["size_x"], label=f"{node.label} size_x"), em)
        sy_var = _compile_value(IRValue(value=props["size_y"], label=f"{node.label} size_y"), em)
        deferred_lines.append(f'node_tree.links.new({sx_var}.outputs["Value"], {var}.inputs["Size X"])')
        deferred_lines.append(f'node_tree.links.new({sy_var}.outputs["Value"], {var}.inputs["Size Y"])')
        deferred_lines.append(f'{var}.inputs["Vertices X"].default_value = {props["vertices_x"]}')
        deferred_lines.append(f'{var}.inputs["Vertices Y"].default_value = {props["vertices_y"]}')

    elif node.primitive_type == PrimitiveType.ICO_SPHERE:
        r_var = _compile_value(IRValue(value=props["radius"], label=f"{node.label} radius"), em)
        deferred_lines.append(f'node_tree.links.new({r_var}.outputs["Value"], {var}.inputs["Radius"])')
        deferred_lines.append(f'{var}.inputs["Subdivisions"].default_value = {props["subdivisions"]}')

    elif node.primitive_type == PrimitiveType.LINE:
        start_var = _compile_vector(IRVector(value=props["start_location"], label=f"{node.label} start"), em)
        end_var = _compile_vector(IRVector(value=props["end_location"], label=f"{node.label} end"), em)
        deferred_lines.append(f'{var}.mode = "END_POINTS"')
        deferred_lines.append(f'{var}.inputs["Count"].default_value = {props["count"]}')
        deferred_lines.append(f'node_tree.links.new({start_var}.outputs["Vector"], {var}.inputs["Start Location"])')
        deferred_lines.append(f'node_tree.links.new({end_var}.outputs["Vector"], {var}.inputs["Offset"])')

    elif node.primitive_type == PrimitiveType.CURVE_ARC:
        r_var = _compile_value(IRValue(value=props["radius"], label=f"{node.label} radius"), em)
        deferred_lines.append(f'{var}.inputs["Resolution"].default_value = {props["resolution"]}')
        deferred_lines.append(f'node_tree.links.new({r_var}.outputs["Value"], {var}.inputs["Radius"])')
        deferred_lines.append(f'{var}.inputs["Start Angle"].default_value = {math.radians(props["start_angle"])}')
        deferred_lines.append(f'{var}.inputs["Sweep Angle"].default_value = {math.radians(props["sweep_angle"])}')

    elif node.primitive_type == PrimitiveType.CURVE_CIRCLE:
        r_var = _compile_value(IRValue(value=props["radius"], label=f"{node.label} radius"), em)
        deferred_lines.append(f'{var}.inputs["Resolution"].default_value = {props["resolution"]}')
        deferred_lines.append(f'node_tree.links.new({r_var}.outputs["Value"], {var}.inputs["Radius"])')

    elif node.primitive_type == PrimitiveType.CURVE_LINE:
        start_var = _compile_vector(IRVector(value=props["start"], label=f"{node.label} start"), em)
        end_var = _compile_vector(IRVector(value=props["end"], label=f"{node.label} end"), em)
        deferred_lines.append(f'node_tree.links.new({start_var}.outputs["Vector"], {var}.inputs["Start"])')
        deferred_lines.append(f'node_tree.links.new({end_var}.outputs["Vector"], {var}.inputs["End"])')

    elif node.primitive_type == PrimitiveType.CURVE_QUADRILATERAL:
        w_var = _compile_value(IRValue(value=props["width"], label=f"{node.label} width"), em)
        h_var = _compile_value(IRValue(value=props["height"], label=f"{node.label} height"), em)
        deferred_lines.append(f'node_tree.links.new({w_var}.outputs["Value"], {var}.inputs["Width"])')
        deferred_lines.append(f'node_tree.links.new({h_var}.outputs["Value"], {var}.inputs["Height"])')

    elif node.primitive_type == PrimitiveType.CURVE_STAR:
        ir_var = _compile_value(IRValue(value=props["inner_radius"], label=f"{node.label} inner r"), em)
        or_var = _compile_value(IRValue(value=props["outer_radius"], label=f"{node.label} outer r"), em)
        deferred_lines.append(f'{var}.inputs["Points"].default_value = {props["points"]}')
        deferred_lines.append(f'node_tree.links.new({ir_var}.outputs["Value"], {var}.inputs["Inner Radius"])')
        deferred_lines.append(f'node_tree.links.new({or_var}.outputs["Value"], {var}.inputs["Outer Radius"])')

    elif node.primitive_type == PrimitiveType.CURVE_SPIRAL:
        sr_var = _compile_value(IRValue(value=props["start_radius"], label=f"{node.label} start r"), em)
        er_var = _compile_value(IRValue(value=props["end_radius"], label=f"{node.label} end r"), em)
        h_var = _compile_value(IRValue(value=props["height"], label=f"{node.label} height"), em)
        deferred_lines.append(f'{var}.inputs["Resolution"].default_value = {props["resolution"]}')
        deferred_lines.append(f'{var}.inputs["Rotations"].default_value = {props["rotations"]}')
        deferred_lines.append(f'node_tree.links.new({sr_var}.outputs["Value"], {var}.inputs["Start Radius"])')
        deferred_lines.append(f'node_tree.links.new({er_var}.outputs["Value"], {var}.inputs["End Radius"])')
        deferred_lines.append(f'node_tree.links.new({h_var}.outputs["Value"], {var}.inputs["Height"])')

    elif node.primitive_type == PrimitiveType.CURVE_BEZIER_SEGMENT:
        s_var = _compile_vector(IRVector(value=props["start"], label=f"{node.label} start"), em)
        sh_var = _compile_vector(IRVector(value=props["start_handle"], label=f"{node.label} start handle"), em)
        eh_var = _compile_vector(IRVector(value=props["end_handle"], label=f"{node.label} end handle"), em)
        e_var = _compile_vector(IRVector(value=props["end"], label=f"{node.label} end"), em)
        deferred_lines.append(f'{var}.inputs["Resolution"].default_value = {props["resolution"]}')
        deferred_lines.append(f'node_tree.links.new({s_var}.outputs["Vector"], {var}.inputs["Start"])')
        deferred_lines.append(f'node_tree.links.new({sh_var}.outputs["Vector"], {var}.inputs["Start Handle"])')
        deferred_lines.append(f'node_tree.links.new({eh_var}.outputs["Vector"], {var}.inputs["End Handle"])')
        deferred_lines.append(f'node_tree.links.new({e_var}.outputs["Vector"], {var}.inputs["End"])')

    elif node.primitive_type == PrimitiveType.CURVE_QUADRATIC_BEZIER:
        s_var = _compile_vector(IRVector(value=props["start"], label=f"{node.label} start"), em)
        m_var = _compile_vector(IRVector(value=props["middle"], label=f"{node.label} middle"), em)
        e_var = _compile_vector(IRVector(value=props["end"], label=f"{node.label} end"), em)
        deferred_lines.append(f'{var}.inputs["Resolution"].default_value = {props["resolution"]}')
        deferred_lines.append(f'node_tree.links.new({s_var}.outputs["Vector"], {var}.inputs["Start"])')
        deferred_lines.append(f'node_tree.links.new({m_var}.outputs["Vector"], {var}.inputs["Middle"])')
        deferred_lines.append(f'node_tree.links.new({e_var}.outputs["Vector"], {var}.inputs["End"])')

    elif node.primitive_type == PrimitiveType.VOLUME_CUBE:
        d_var = _compile_value(IRValue(value=props["density"], label=f"{node.label} density"), em)
        b_var = _compile_value(IRValue(value=props["background"], label=f"{node.label} background"), em)
        min_var = _compile_vector(IRVector(value=props["min"], label=f"{node.label} min"), em)
        max_var = _compile_vector(IRVector(value=props["max"], label=f"{node.label} max"), em)
        deferred_lines.append(f'node_tree.links.new({d_var}.outputs["Value"], {var}.inputs["Density"])')
        deferred_lines.append(f'node_tree.links.new({b_var}.outputs["Value"], {var}.inputs["Background"])')
        deferred_lines.append(f'node_tree.links.new({min_var}.outputs["Vector"], {var}.inputs["Min"])')
        deferred_lines.append(f'node_tree.links.new({max_var}.outputs["Vector"], {var}.inputs["Max"])')
        deferred_lines.append(f'{var}.inputs["Resolution X"].default_value = {props["resolution_x"]}')
        deferred_lines.append(f'{var}.inputs["Resolution Y"].default_value = {props["resolution_y"]}')
        deferred_lines.append(f'{var}.inputs["Resolution Z"].default_value = {props["resolution_z"]}')

    elif node.primitive_type in (
        PrimitiveType.IMPORT_OBJ,
        PrimitiveType.IMPORT_STL,
        PrimitiveType.IMPORT_PLY,
        PrimitiveType.IMPORT_VDB,
    ):
        deferred_lines.append(f'{var}.inputs["Path"].default_value = {props["path"]!r}')

    elif node.primitive_type == PrimitiveType.IMPORT_CSV:
        deferred_lines.append(f'{var}.inputs["Path"].default_value = {props["path"]!r}')
        deferred_lines.append(f'{var}.inputs["Delimiter"].default_value = {props["delimiter"]!r}')

    elif node.primitive_type == PrimitiveType.COLLECTION_INFO:
        if props.get("collection"):
            deferred_lines.append(f'{var}.inputs["Collection"].default_value = bpy.data.collections.get({props["collection"]!r})')
        if "separate_children" in props:
            deferred_lines.append(f'{var}.inputs["Separate Children"].default_value = {props["separate_children"]}')
        if "reset_children" in props:
            deferred_lines.append(f'{var}.inputs["Reset Children"].default_value = {props["reset_children"]}')
        if "transform_space" in props:
            deferred_lines.append(f'{var}.transform_space = "{props["transform_space"]}"')

    elif node.primitive_type == PrimitiveType.OBJECT_INFO:
        if props.get("object"):
            deferred_lines.append(f'{var}.inputs["Object"].default_value = bpy.data.objects.get({props["object"]!r})')
        if "as_instance" in props:
            deferred_lines.append(f'{var}.inputs["As Instance"].default_value = {props["as_instance"]}')
        if "transform_space" in props:
            deferred_lines.append(f'{var}.transform_space = "{props["transform_space"]}"')

    # Main node placed after all helpers — appears to the right in Blender.
    loc = em.next_main_location()
    em.line(f'{var} = node_tree.nodes.new("{bpy_type}")')
    em.line(f"{var}.location = {loc}")
    em.line(f'{var}.label = {node.label!r}')
    for deferred in deferred_lines:
        em.line(deferred)

    return var


def _get_geometry_output_socket(node: IRNode) -> str:
    """Return the output socket name that carries geometry for *node*."""
    if isinstance(node, IRPrimitive):
        return _GEOMETRY_OUTPUT.get(node.primitive_type, "Geometry")
    if isinstance(node, IRBoolean):
        return "Mesh"
    if isinstance(node, IRJoin):
        return "Geometry"
    if isinstance(node, IRInstanceOnPoints):
        return "Instances"
    if isinstance(node, IRGeometryOp):
        if node.op_type == "GeometryNodeViewer":
            return _get_geometry_output_socket(node.child)
        return _GEOM_OP_OUTPUT.get(node.op_type, "Geometry")
    if isinstance(node, IRSeparateComponents):
        return node.component
    if isinstance(node, IRFieldInput):
        if node.output_socket:
            return node.output_socket
        return _FIELD_OUTPUT.get(node.field_type, "Value")
    if isinstance(node, IRMathOp):
        if node.math_type == "ShaderNodeVectorMath" and node.operation in _VECTOR_MATH_SCALAR_OUT:
            return "Value"
        return _MATH_OUTPUT.get(node.math_type, "Value")
    return "Geometry"


def _compile_node(node: IRNode, em: _Emitter) -> str:
    """Dispatch compilation to the appropriate handler. Returns the variable name."""
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
        return _compile_field_input(node, em)
    if isinstance(node, IRMathOp):
        return _compile_math_op(node, em)
    if isinstance(node, IRValue):
        return _compile_value(node, em)
    if isinstance(node, IRVector):
        return _compile_vector(node, em)
    raise TypeError(f"Unknown IR node type: {type(node).__name__}")


def _compile_boolean(node: IRBoolean, em: _Emitter) -> str:
    child_vars = [_compile_node(c, em) for c in node.children]
    child_sockets = [_get_geometry_output_socket(c) for c in node.children]

    em.start_group()
    var = em.new_var("bool")
    loc = em.next_main_location()
    em.line(f'{var} = node_tree.nodes.new("GeometryNodeMeshBoolean")')
    em.line(f"{var}.location = {loc}")
    em.line(f'{var}.label = {node.label!r}')
    em.line(f'{var}.operation = "{_BOOLEAN_OP_STR[node.operation]}"')
    em.line(f'{var}.solver = "EXACT"')

    if node.operation == BooleanOp.DIFFERENCE:
        # First child → Mesh 1 (socket index 0), rest → Mesh 2 (socket index 1)
        em.line(f'node_tree.links.new({child_vars[0]}.outputs["{child_sockets[0]}"], {var}.inputs[0])')
        for cv, cs in zip(child_vars[1:], child_sockets[1:]):
            em.line(f'node_tree.links.new({cv}.outputs["{cs}"], {var}.inputs[1])')
    else:
        # UNION/INTERSECT: all go to Mesh 2 (socket index 1)
        for cv, cs in zip(child_vars, child_sockets):
            em.line(f'node_tree.links.new({cv}.outputs["{cs}"], {var}.inputs[1])')

    return var


def _compile_transform(node: IRTransform, em: _Emitter) -> str:
    child_var = _compile_node(node.child, em) if node.child else None
    child_socket = _get_geometry_output_socket(node.child) if node.child else "Geometry"

    em.start_group()
    var = em.new_var("xform")
    deferred_lines: list[str] = []

    if child_var:
        deferred_lines.append(f'node_tree.links.new({child_var}.outputs["{child_socket}"], {var}.inputs["Geometry"])')

    if node.translation is not None:
        t_var = _compile_vector(IRVector(value=node.translation, label=f"{node.label} translation"), em)
        deferred_lines.append(f'node_tree.links.new({t_var}.outputs["Vector"], {var}.inputs["Translation"])')

    if node.rotation is not None:
        rads = tuple(c * math.pi / 180.0 for c in node.rotation)
        r_var = _compile_vector(IRVector(value=rads, label=f"{node.label} rotation"), em)
        deferred_lines.append(f'node_tree.links.new({r_var}.outputs["Vector"], {var}.inputs["Rotation"])')

    if node.scale is not None:
        s_var = _compile_vector(IRVector(value=node.scale, label=f"{node.label} scale"), em)
        deferred_lines.append(f'node_tree.links.new({s_var}.outputs["Vector"], {var}.inputs["Scale"])')

    loc = em.next_main_location()
    em.line(f'{var} = node_tree.nodes.new("GeometryNodeTransform")')
    em.line(f"{var}.location = {loc}")
    em.line(f'{var}.label = {node.label!r}')
    for deferred in deferred_lines:
        em.line(deferred)

    return var


def _compile_set_position(node: IRSetPosition, em: _Emitter) -> str:
    child_var = _compile_node(node.child, em) if node.child else None
    child_socket = _get_geometry_output_socket(node.child) if node.child else "Geometry"

    em.start_group()
    var = em.new_var("setpos")
    deferred_lines: list[str] = []

    if child_var:
        deferred_lines.append(f'node_tree.links.new({child_var}.outputs["{child_socket}"], {var}.inputs["Geometry"])')

    off_var = _compile_vector(IRVector(value=node.offset, label=f"{node.label} offset"), em)
    deferred_lines.append(f'node_tree.links.new({off_var}.outputs["Vector"], {var}.inputs["Offset"])')

    loc = em.next_main_location()
    em.line(f'{var} = node_tree.nodes.new("GeometryNodeSetPosition")')
    em.line(f"{var}.location = {loc}")
    em.line(f'{var}.label = {node.label!r}')
    for deferred in deferred_lines:
        em.line(deferred)

    return var


def _compile_join(node: IRJoin, em: _Emitter) -> str:
    child_vars = [_compile_node(c, em) for c in node.children]
    child_sockets = [_get_geometry_output_socket(c) for c in node.children]

    em.start_group()
    var = em.new_var("join")
    loc = em.next_main_location()
    em.line(f'{var} = node_tree.nodes.new("GeometryNodeJoinGeometry")')
    em.line(f"{var}.location = {loc}")
    em.line(f'{var}.label = {node.label!r}')

    for cv, cs in zip(child_vars, child_sockets):
        em.line(f'node_tree.links.new({cv}.outputs["{cs}"], {var}.inputs["Geometry"])')

    return var


def _compile_instance_on_points(node: IRInstanceOnPoints, em: _Emitter) -> str:
    points_var = _compile_node(node.points, em) if node.points else None
    points_socket = _get_geometry_output_socket(node.points) if node.points else "Geometry"
    instance_var = _compile_node(node.instance, em) if node.instance else None
    instance_socket = _get_geometry_output_socket(node.instance) if node.instance else "Geometry"

    em.start_group()
    var = em.new_var("inst")
    loc = em.next_main_location()
    em.line(f'{var} = node_tree.nodes.new("GeometryNodeInstanceOnPoints")')
    em.line(f"{var}.location = {loc}")
    em.line(f'{var}.label = {node.label!r}')

    if points_var:
        em.line(f'node_tree.links.new({points_var}.outputs["{points_socket}"], {var}.inputs["Points"])')
    if instance_var:
        em.line(f'node_tree.links.new({instance_var}.outputs["{instance_socket}"], {var}.inputs["Instance"])')

    return var


def _compile_geometry_op(node: IRGeometryOp, em: _Emitter) -> str:
    child_var = _compile_node(node.child, em) if node.child else None
    child_socket = _get_geometry_output_socket(node.child) if node.child else "Geometry"

    # Compile extra children (e.g. Profile Curve for Curve to Mesh)
    extra_vars: dict[str, tuple[str, str]] = {}
    for socket_name, extra_node in node.extra_children.items():
        ev = _compile_node(extra_node, em)
        es = _get_field_output_socket(extra_node)
        extra_vars[socket_name] = (ev, es)

    em.start_group()
    var = em.new_var("geom_op")

    props = node.properties
    # Deferred lines: links and node properties emitted after the main node.
    deferred_lines: list[str] = []

    # Main geometry input link
    input_sock = _GEOM_OP_INPUT.get(node.op_type, "Geometry")
    if child_var:
        deferred_lines.append(f'node_tree.links.new({child_var}.outputs["{child_socket}"], {var}.inputs["{input_sock}"])')

    # Extra geometry input links
    for socket_name, (ev, es) in extra_vars.items():
        deferred_lines.append(f'node_tree.links.new({ev}.outputs["{es}"], {var}.inputs["{socket_name}"])')

    # Scalar inputs — emit Value helper nodes above the main node
    for key, input_name in _GEOM_OP_SCALAR.items():
        if key in props:
            v_var = _compile_value(IRValue(value=props[key], label=f"{node.label} {key}"), em)
            deferred_lines.append(f'node_tree.links.new({v_var}.outputs["Value"], {var}.inputs["{input_name}"])')

    # Vector inputs — emit Vector helper nodes above the main node
    for key, input_name in [
        ("rotation", "Rotation"),
        ("scale", "Scale"),
        ("translation", "Translation"),
        ("normal", "Normal"),
        ("position", "Position"),
        ("offset", "Offset"),
        ("guide_up", "Guide Up"),
        ("point_up", "Point Up"),
        ("spacing", "Spacing"),
        ("center", "Center"),
        ("axis", "Axis"),
        ("sample_position", "Sample Position"),
        ("source_position", "Source Position"),
        ("ray_direction", "Ray Direction"),
        ("uv_map", "UV Map"),
        ("sample_uv", "Sample UV"),
    ]:
        if key in props:
            v_var = _compile_vector(
                IRVector(value=props[key], label=f"{node.label} {key}"), em
            )
            deferred_lines.append(f'node_tree.links.new({v_var}.outputs["Vector"], {var}.inputs["{input_name}"])')

    # Main node placed after all helper nodes.
    loc = em.next_main_location()
    em.line(f'{var} = node_tree.nodes.new("{node.op_type}")')
    em.line(f"{var}.location = {loc}")
    em.line(f'{var}.label = {node.label!r}')

    # Enum/mode properties (set directly on the node after creation)
    if "mode" in props:
        em.line(f'{var}.mode = "{props["mode"]}"')
    if "handle_type" in props:
        em.line(f'{var}.handle_type = "{props["handle_type"]}"')
    if "spline_type" in props:
        em.line(f'{var}.spline_type = "{props["spline_type"]}"')
    if "domain" in props:
        em.line(f'{var}.domain = "{props["domain"]}"')
    if "distribute_method" in props:
        em.line(f'{var}.distribute_method = "{props["distribute_method"]}"')
    if "scale_mode" in props:
        em.line(f'{var}.scale_mode = "{props["scale_mode"]}"')
    if "quad_method" in props:
        em.line(f'{var}.quad_method = "{props["quad_method"]}"')
    if "ngon_method" in props:
        em.line(f'{var}.ngon_method = "{props["ngon_method"]}"')
    if "data_type" in props:
        em.line(f'{var}.data_type = "{props["data_type"]}"')
    if "selection_type" in props:
        em.line(f'{var}.selection_type = "{props["selection_type"]}"')
    if "depth_order" in props:
        em.line(f'{var}.depth_order = "{props["depth_order"]}"')
    if "input_type" in props:
        em.line(f'{var}.input_type = "{props["input_type"]}"')
    if "target_element" in props:
        em.line(f'{var}.target_element = "{props["target_element"]}"')

    # Boolean inputs (set as default_value)
    for key, input_name in _GEOM_OP_BOOL.items():
        if key in props:
            em.line(f'{var}.inputs["{input_name}"].default_value = {props[key]}')

    # String inputs (set as default_value)
    if "string" in props:
        em.line(f'{var}.inputs["String"].default_value = {props["string"]!r}')
    if "name" in props:
        em.line(f'{var}.inputs["Name"].default_value = {props["name"]!r}')

    # Color inputs (set as default_value RGBA tuple)
    if "color" in props:
        em.line(f'{var}.inputs["Color"].default_value = {list(props["color"])}')

    # Material inputs (referenced by name via bpy.data.materials)
    for key, input_name in [
        ("material", "Material"),
        ("material_old", "Old"),
        ("material_new", "New"),
    ]:
        if key in props and props[key]:
            em.line(f'{var}.inputs["{input_name}"].default_value = bpy.data.materials.get({props[key]!r})')

    # Emit deferred links after the main node is defined
    for deferred in deferred_lines:
        em.line(deferred)

    # Viewer is a terminal (no output); pass through the child
    if node.op_type == "GeometryNodeViewer":
        return child_var

    return var


def _compile_separate_components(node: IRSeparateComponents, em: _Emitter) -> str:
    child_var = _compile_node(node.child, em) if node.child else None
    child_socket = _get_geometry_output_socket(node.child) if node.child else "Geometry"

    em.start_group()
    var = em.new_var("sep")
    loc = em.next_main_location()
    em.line(f'{var} = node_tree.nodes.new("GeometryNodeSeparateComponents")')
    em.line(f"{var}.location = {loc}")
    em.line(f'{var}.label = {node.label!r}')

    if child_var:
        em.line(f'node_tree.links.new({child_var}.outputs["{child_socket}"], {var}.inputs["Geometry"])')

    return var


def _compile_field_input(node: IRFieldInput, em: _Emitter) -> str:
    em.start_group()
    var = em.new_var("field")
    loc = em.next_main_location()
    em.line(f'{var} = node_tree.nodes.new("{node.field_type}")')
    em.line(f"{var}.location = {loc}")
    em.line(f'{var}.label = {node.label!r}')

    # Mapping from reference tag to bpy.data collection name
    _REF_COLLECTIONS = {
        "MATERIAL": "materials",
        "OBJECT": "objects",
        "COLLECTION": "collections",
        "IMAGE": "images",
    }

    # Enum/mode properties on the node itself
    for key, value in node.properties.items():
        if isinstance(value, tuple) and len(value) == 2 and value[0] in _REF_COLLECTIONS:
            coll = _REF_COLLECTIONS[value[0]]
            ref_name = value[1]
            if ref_name:
                em.line(f'{var}.{key} = bpy.data.{coll}.get({ref_name!r})')
        elif isinstance(value, str):
            em.line(f'{var}.{key} = "{value}"')
        else:
            em.line(f'{var}.{key} = {value}')

    # Default values on input sockets
    for socket_name, value in node.input_defaults.items():
        if isinstance(value, tuple) and len(value) == 2 and value[0] in _REF_COLLECTIONS:
            coll = _REF_COLLECTIONS[value[0]]
            ref_name = value[1]
            if ref_name:
                em.line(f'{var}.inputs["{socket_name}"].default_value = bpy.data.{coll}.get({ref_name!r})')
        elif isinstance(value, str):
            em.line(f'{var}.inputs["{socket_name}"].default_value = "{value}"')
        elif isinstance(value, bool):
            em.line(f'{var}.inputs["{socket_name}"].default_value = {value}')
        else:
            em.line(f'{var}.inputs["{socket_name}"].default_value = {value}')

    return var


# Output socket name for field input nodes
_FIELD_OUTPUT: dict[str, str] = {
    "GeometryNodeInputPosition": "Position",
    "GeometryNodeInputNormal": "Normal",
    "GeometryNodeInputIndex": "Index",
    "GeometryNodeInputMeshEdgeVertices": "Position 1",
    "GeometryNodeInputMeshEdgeAngle": "Unsigned Angle",
    "GeometryNodeInputMeshVertexNeighbors": "Vertex Count",
    "GeometryNodeInputMeshFaceNeighbors": "Vertex Count",
    "GeometryNodeInputMeshEdgeNeighbors": "Face Count",
    "GeometryNodeInputMeshFaceArea": "Area",
    "GeometryNodeInputMeshIsland": "Island Index",
    "GeometryNodeInputID": "ID",
    "GeometryNodeInputNamedAttribute": "Attribute",
    # Batch 17 — additional field inputs
    "GeometryNodeInputRadius": "Radius",
    "GeometryNodeInputEdgeSmooth": "Smooth",
    "GeometryNodeInputShadeSmooth": "Smooth",
    "GeometryNodeInputMeshFaceIsPlanar": "Planar",
    "GeometryNodeInputTangent": "Tangent",
    "GeometryNodeInputCurveTilt": "Tilt",
    "GeometryNodeInputSplineCyclic": "Cyclic",
    "GeometryNodeInputSplineResolution": "Resolution",
    "GeometryNodeInputCurveHandlePositions": "Left",
    "GeometryNodeCurveEndpointSelection": "Selection",
    "GeometryNodeCurveHandleTypeSelection": "Selection",
    "GeometryNodeSplineLength": "Length",
    "GeometryNodeSplineParameter": "Factor",
    "GeometryNodeCurveOfPoint": "Curve Index",
    "GeometryNodeOffsetPointInCurve": "Is Valid Offset",
    "GeometryNodePointsOfCurve": "Point Index",
    "GeometryNodeInputShortestEdgePaths": "Next Vertex Index",
    "GeometryNodeInputInstanceRotation": "Rotation",
    "GeometryNodeInputInstanceScale": "Scale",
    "GeometryNodeInputMaterialIndex": "Material Index",
    # Batch 18 — scene, instance, topology, material, selection
    "GeometryNodeInputSceneTime": "Seconds",
    "GeometryNodeInputActiveCamera": "Active Camera",
    "GeometryNodeSelfObject": "Self Object",
    "GeometryNodeIsViewport": "Is Viewport",
    "GeometryNodeInputInstanceBounds": "Min",
    "GeometryNodeInputNamedLayerSelection": "Selection",
    "GeometryNodeMeshFaceSetBoundaries": "Boundary Edges",
    "GeometryNodeMaterialSelection": "Selection",
    "GeometryNodeInputMaterial": "Material",
    "GeometryNodeCornersOfEdge": "Corner Index",
    "GeometryNodeCornersOfFace": "Corner Index",
    "GeometryNodeCornersOfVertex": "Corner Index",
    "GeometryNodeEdgesOfCorner": "Next Edge Index",
    "GeometryNodeEdgesOfVertex": "Edge Index",
    "GeometryNodeFaceOfCorner": "Face Index",
    "GeometryNodeVertexOfCorner": "Vertex Index",
    "GeometryNodeOffsetCornerInFace": "Corner Index",
    "GeometryNodeIndexOfNearest": "Index",
    "GeometryNodeEdgePathsToSelection": "Selection",
    "GeometryNodeEdgesToFaceGroups": "Face Group ID",
    # Batch 19 — instance, viewport, tool, ref, stats, UV, utility
    "GeometryNodeInstanceTransform": "Transform",
    "GeometryNodeViewportTransform": "Projection",
    "GeometryNodeToolSelection": "Boolean",
    "GeometryNodeToolFaceSet": "Face Set",
    "GeometryNodeToolMousePosition": "Mouse X",
    "GeometryNodeTool3DCursor": "Location",
    "GeometryNodeToolActiveElement": "Index",
    "GeometryNodeInputCollection": "Collection",
    "GeometryNodeInputImage": "Image",
    "GeometryNodeInputObject": "Object",
    "GeometryNodeCameraInfo": "Focal Length",
    "GeometryNodeImageTexture": "Color",
    "GeometryNodeImageInfo": "Width",
    "GeometryNodeFieldAverage": "Mean",
    "GeometryNodeFieldMinAndMax": "Min",
    "GeometryNodeFieldVariance": "Standard Deviation",
    "GeometryNodeUVPackIslands": "UV",
    "GeometryNodeUVUnwrap": "UV",
    "GeometryNodeStringJoin": "String",
    "GeometryNodeImportText": "String",
    # Batch 20 — field processors, grid, gizmo, warning
    "GeometryNodeBlurAttribute": "Value",
    "GeometryNodeAccumulateField": "Leading",
    "GeometryNodeFieldAtIndex": "Value",
    "GeometryNodeFieldOnDomain": "Value",
    "GeometryNodeGridInfo": "Transform",
    "GeometryNodeSampleGrid": "Value",
    "GeometryNodeSampleGridIndex": "Value",
    "GeometryNodeSDFGridBoolean": "Grid",
    "GeometryNodeWarning": "Show",
    "GeometryNodeGizmoDial": "Transform",
    "GeometryNodeGizmoLinear": "Transform",
    "GeometryNodeGizmoTransform": "Transform",
}

# Math node output socket names
_MATH_OUTPUT: dict[str, str] = {
    "ShaderNodeMath": "Value",
    "ShaderNodeVectorMath": "Vector",
}

# VectorMath ops that output a scalar instead of a vector
_VECTOR_MATH_SCALAR_OUT = {"DOT_PRODUCT", "DISTANCE", "LENGTH"}


def _compile_math_op(node: IRMathOp, em: _Emitter) -> str:
    # Compile input nodes first
    input_vars: dict[str, tuple[str, str]] = {}
    for socket_key, input_node in node.inputs.items():
        iv = _compile_node(input_node, em)
        is_ = _get_field_output_socket(input_node)
        input_vars[socket_key] = (iv, is_)

    em.start_group()
    var = em.new_var("math")
    loc = em.next_main_location()
    em.line(f'{var} = node_tree.nodes.new("{node.math_type}")')
    em.line(f"{var}.location = {loc}")
    em.line(f'{var}.label = {node.label!r}')
    em.line(f'{var}.operation = "{node.operation}"')

    if node.math_type == "ShaderNodeMath" and node.clamp:
        em.line(f"{var}.use_clamp = True")

    # Link inputs
    for socket_key, (iv, is_) in input_vars.items():
        em.line(f'node_tree.links.new({iv}.outputs["{is_}"], {var}.inputs["{socket_key}"])')

    return var


def _get_field_output_socket(node: IRNode) -> str:
    """Resolve the output socket name for any node type."""
    if isinstance(node, IRFieldInput):
        if node.output_socket:
            return node.output_socket
        return _FIELD_OUTPUT.get(node.field_type, "Value")
    if isinstance(node, IRMathOp):
        if node.math_type == "ShaderNodeVectorMath" and node.operation in _VECTOR_MATH_SCALAR_OUT:
            return "Value"
        return _MATH_OUTPUT.get(node.math_type, "Value")
    if isinstance(node, IRValue):
        return "Value"
    if isinstance(node, IRVector):
        return "Vector"
    # Fallback to geometry output socket
    return _get_geometry_output_socket(node)


def _compile_output(node: IROutput, em: _Emitter) -> str:
    child_var = _compile_node(node.child, em) if node.child else None
    child_socket = _get_geometry_output_socket(node.child) if node.child else "Geometry"

    em.start_group()
    var = em.new_var("out")
    loc = em.next_main_location()
    em.line(f'{var} = node_tree.nodes.new("NodeGroupOutput")')
    em.line(f"{var}.location = {loc}")
    em.line(f'{var}.label = "output"')

    if child_var:
        em.line(f"node_tree.links.new({child_var}.outputs[0], {var}.inputs[0])")

    return var


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def compile_to_source(graph: IRGraph) -> str:
    """Compile an IR graph to a standalone Python/bpy script string."""
    em = _Emitter()

    # Preamble
    em.line("import bpy")
    em.blank()
    em.blank()

    # Setup function
    em.line(f"def setup(object_name={graph.name!r}):")
    em.line(f'    """Auto-generated by Tanuki compiler."""')
    em.line(f"    # Delete existing object if present")
    em.line(f"    if object_name in bpy.data.objects:")
    em.line(f"        obj = bpy.data.objects[object_name]")
    em.line(f"        bpy.data.objects.remove(obj, do_unlink=True)")
    em.blank()
    em.line(f"    # Create base mesh + geometry nodes modifier")
    em.line(f'    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 0))')
    em.line(f"    bpy.context.active_object.name = object_name")
    em.line(f"    plane = bpy.context.active_object")
    em.line(f'    modifier = plane.modifiers.new(name="GeometryNodes", type="NODES")')
    em.line(f"    bpy.ops.node.new_geometry_node_group_assign()")
    em.line(f"    node_tree = modifier.node_group")
    em.blank()
    em.line(f"    # Clear default nodes")
    em.line(f"    for node in list(node_tree.nodes):")
    em.line(f"        node_tree.nodes.remove(node)")
    em.blank()

    # Compile the graph
    if graph.root:
        # Save current emitter state and use indented lines
        inner = _Emitter()
        _compile_node(graph.root, inner)
        for raw_line in inner.source().splitlines():
            if raw_line:
                em.line(f"    {raw_line}")
            else:
                em.blank()

    em.blank()
    em.line(f"    return node_tree")
    em.blank()
    em.blank()
    em.line(f"# Execute")
    em.line(f"setup()")
    em.blank()

    return em.source()


def compile_to_script(graph: IRGraph, output_path: str | Path) -> Path:
    """Compile an IR graph and write the result to a .py file.

    Returns the path written to.
    """
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(compile_to_source(graph))
    return path
