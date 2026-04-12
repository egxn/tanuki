---
id: field-nodes
title: Field Nodes
sidebar_position: 7
---

# Field Nodes

**Module:** `tanuki.dsl.field_nodes`

Field nodes produce per-element data (position, normal, index, etc.) that can be used as inputs to operations — principally in the Blender backend.

:::info Backend support
Field nodes are **only fully supported** by the Blender backend. Other backends emit them as comments and ignore the value.
:::

## ~37 available field inputs

| Function | Blender node | Description |
|----------|-------------|-------------|
| `position_field()` | `GeometryNodeInputPosition` | Per-element position vector |
| `normal_field()` | `GeometryNodeInputNormal` | Per-element normal vector |
| `index_field()` | `GeometryNodeInputIndex` | Integer element index |
| `id_field()` | `GeometryNodeInputID` | Custom integer ID |
| `radius_field()` | `GeometryNodeInputRadius` | Point/curve radius |
| `edge_angle()` | `GeometryNodeInputMeshEdgeAngle` | Angle per mesh edge |
| `edge_vertices()` | `GeometryNodeInputMeshEdgeVertices` | Vertex positions per edge |
| `face_area()` | `GeometryNodeInputMeshFaceArea` | Face area |
| `face_neighbors()` | `GeometryNodeInputMeshFaceNeighbors` | Neighbor face/edge counts |
| `face_normal()` | `GeometryNodeInputMeshFaceNormal` | Per-face normal |
| `vertex_neighbors()` | `GeometryNodeInputMeshVertexNeighbors` | Neighbor count per vertex |
| `is_edge_smooth()` | `GeometryNodeInputEdgeSmooth` | Boolean per edge |
| `is_face_smooth()` | `GeometryNodeInputShadeSmooth` | Boolean per face |
| `is_viewport()` | `GeometryNodeIsViewport` | True inside Blender viewport |
| `scene_time()` | `GeometryNodeInputSceneTime` | Scene frame/seconds |
| `spline_cyclic()` | `GeometryNodeInputSplineCyclic` | Boolean — is spline closed? |
| `spline_length()` | `GeometryNodeSplineLength` | Spline length |
| `spline_parameter()` | `GeometryNodeSplineParameter` | Parametric position along spline |
| `spline_resolution()` | `GeometryNodeInputSplineResolution` | Resolution per spline |
| `curve_tilt()` | `GeometryNodeInputCurveTilt` | Tilt per control point |
| `handle_positions()` | `GeometryNodeInputCurveHandlePositions` | Bézier handle positions |
| `curve_handle_type()` | `GeometryNodeInputCurveHandleType` | Handle type flags |
| `tangent()` | `GeometryNodeInputTangent` | Curve tangent vector |
| `named_attribute(name, type)` | `GeometryNodeInputNamedAttribute` | Look up a stored attribute |
| `active_element()` | `GeometryNodeToolActiveElement` | Active element in a tool |
| `selection()` | `GeometryNodeToolSelection` | Selection state |

## Usage example (Blender only)

```python
from tanuki.dsl import *
from tanuki.dsl.field_nodes import position_field, index_field
from tanuki.dsl.math_ops import math_op, vector_math_op
from tanuki.dsl.mesh_ops import set_point_radius
from tanuki.backends import render

with model("scattered_points") as ctx:
    pts    = ico_sphere(2.0, subdivisions=3)
    pos    = position_field()              # position of each vertex
    radius = math_op(index_field(), "MULTIPLY", 0.01)  # radius grows with index
    result = set_point_radius(pts, radius)
    output(result)

render(ctx.graph, target="blender", output_path="scattered.py")
```
