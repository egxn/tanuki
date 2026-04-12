---
id: opencascade
title: OpenCascade.js Backend
sidebar_position: 3
---

# OpenCascade.js Backend

**Target:** `"opencascade"` · **Output extension:** `.js`

Generates **JavaScript ES Modules** for the [opencascade.js](https://ocjs.org/) library. The file exports a `setup_<name>(oc)` function that receives an initialised `oc` instance and returns a `TopoDS_Shape` (BREP solid).

## Usage

```python
render(graph, target="opencascade", output_path="model.js")
```

Consume the output in a browser or Node.js environment:

```javascript
import initOpenCascade from 'opencascade.js';
import { setup_my_model } from './model.js';

initOpenCascade().then(oc => {
  const shape = setup_my_model(oc);
  // use shape with STEPExporter, visualizer, etc.
});
```

## Supported primitives

| Primitive | OCCT API |
|-----------|---------|
| `cube` | `BRepPrimAPI_MakeBox` |
| `sphere` | `BRepPrimAPI_MakeSphere` |
| `cylinder` | `BRepPrimAPI_MakeCylinder` |
| `cone` | `BRepPrimAPI_MakeCone` |
| `circle` | `gp_Circ` + `BRepBuilderAPI_MakeEdge` |
| `line` / `curve_line` | `BRepBuilderAPI_MakeEdge` |
| `curve_arc` | `gp_Circ` (angular range) |
| `bezier_segment` | `Geom_BezierCurve` + `BRepBuilderAPI_MakeEdge` |
| `quadratic_bezier` | `Geom_BezierCurve` (3 poles) |
| `curve_star` | Polygonal wire (vertex-by-vertex) |
| `curve_quadrilateral` | 4-edge wire |
| `point` | `BRepBuilderAPI_MakeVertex` |

### Approximations ⚠️

| Primitive | Note |
|-----------|------|
| `ico_sphere` | Approximated as UV sphere (`BRepPrimAPI_MakeSphere`) |
| `grid` | Approximated as a flat face (`BRepBuilderAPI_MakeFace`) |
| `curve_spiral` | Approximated as a polyline wire |
| `instance_on_points` | Iterates vertices; builds translated copies in a `TopoDS_Compound` |

## Supported operations

| IR node | OCCT API |
|---------|---------|
| `union` | `BRepAlgoAPI_Fuse` |
| `difference` | `BRepAlgoAPI_Cut` |
| `intersect` | `BRepAlgoAPI_Common` |
| `join` | `TopoDS_Compound` + `BRep_Builder` |
| `translate` | `gp_Trsf` + `BRepBuilderAPI_Transform` |
| `rotate` (X/Y/Z) | `gp_Trsf::SetRotation` per axis |
| `scale` uniform | `gp_Trsf::SetScaleFactor` |
| `scale` non-uniform | `gp_GTrsf` + `BRepBuilderAPI_GTransform` |
| `extrude` | `BRepPrimAPI_MakePrism` |
| `fillet` | `BRepFilletAPI_MakeFillet` (all edges) |
| `fill_curve` | `BRepBuilderAPI_MakeFace` from wire |
| `curve_to_mesh` | `BRepOffsetAPI_MakePipe` |

## Not supported

- `field_inputs`, `math_ops` (no BREP equivalent — emitted as comments)
- `convex_hull` (not directly available in OCCT)
- `separate_components` (pass-through)
- ~200 Blender-specific geometry ops (pass-through or ignored)
- Materials, attributes, UV maps
- File importers (OBJ/STL/PLY)
