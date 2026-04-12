---
id: blender
title: Blender Backend
sidebar_position: 2
---

# Blender Backend

**Target:** `"blender"` · **Output extension:** `.py`

Generates Python (`bpy`) scripts that create a **Geometry Nodes** modifier in Blender. The script can be run from the Blender command line, pasted into the Blender Python console, or loaded as a text block.

## Usage

```python
from tanuki.backends import render

# Write a standalone .py script
render(graph, target="blender", mode="script", output_path="model.py")

# Execute directly inside a running Blender session
render(graph, target="blender", mode="direct")
```

### Running the generated script

```bash
blender --background --python model.py
# or open a .blend and run: blender scene.blend --python model.py
```

## Supported primitives (full coverage)

| Primitive | Blender node |
|-----------|-------------|
| `cube` | `GeometryNodeMeshCube` |
| `sphere` | `GeometryNodeMeshUVSphere` |
| `cylinder` | `GeometryNodeMeshCylinder` |
| `cone` | `GeometryNodeMeshCone` |
| `point` | `GeometryNodePoints` |
| `circle` | `GeometryNodeMeshCircle` |
| `grid` | `GeometryNodeMeshGrid` |
| `ico_sphere` | `GeometryNodeMeshIcoSphere` |
| `line` | `GeometryNodeMeshLine` |
| `curve_arc` | `GeometryNodeCurveArc` |
| `curve_circle` | `GeometryNodeCurvePrimitiveCircle` |
| `curve_line` | `GeometryNodeCurvePrimitiveLine` |
| `curve_quadrilateral` | `GeometryNodeCurvePrimitiveQuadrilateral` |
| `curve_star` | `GeometryNodeCurveStar` |
| `curve_spiral` | `GeometryNodeCurveSpiral` |
| `bezier_segment` | `GeometryNodeCurvePrimitiveBezierSegment` |
| `quadratic_bezier` | `GeometryNodeCurveQuadraticBezier` |
| `volume_cube` | `GeometryNodeVolumeCube` |
| `import_obj/stl/ply/csv/vdb` | `GeometryNodeImport*` |
| `collection_info` | `GeometryNodeCollectionInfo` |
| `object_info` | `GeometryNodeObjectInfo` |

## Supported operations (~200 / 223 Blender nodes, ~90%)

- **Booleans:** `union`, `difference`, `intersect` → `GeometryNodeMeshBoolean`
- **Transforms:** `translate`, `rotate`, `scale_by`, `transform`, `set_position`
- **Join:** `GeometryNodeJoinGeometry`
- **Instance on points:** `GeometryNodeInstanceOnPoints`
- **Mesh ops:** extrude, subdivide, triangulate, dual mesh, flip faces, merge by distance, separate components, split edges, bounding box, convex hull, delete, …
- **Curve ops:** fill, fillet, resample, trim, subdivide curve, reverse, set spline type, set radius/tilt, sample curve, curve to points, …
- **Instance ops:** realize, rotate, scale, translate, split to instances, …
- **Material ops:** set material, replace, set index
- **Attribute ops:** store/remove named attribute
- **Volume ops:** distribute points, points to volume, mesh to volume, volume to mesh, …
- **Field inputs:** ~37 nodes (position, normal, index, edge angle, face area, spline length, …)
- **Math ops:** ~40 scalar and vector math operations

## Not supported

- Grease Pencil nodes (basic pass-through)
- Gizmo nodes (emitted as comments)
- GPU/GLSL output

## Node coverage progress

See [DSL Progress](../../blender_docs/dsl_progress) for a full checklist of implemented Blender nodes.

To regenerate the Blender node registry (`node_map.py`):

```bash
PYTHONPATH=src python -m tanuki.codegen.generate_nodes
```
