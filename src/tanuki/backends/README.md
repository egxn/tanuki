# Tanuki Backends — Support Matrix

Tanuki compiles IR graphs to different targets via the `render()` function:

```python
from tanuki.backends import render
render(ctx.graph, target="<backend>")                          # → source code string
render(ctx.graph, target="<backend>", output_path="file.ext") # → written Path
```

Available targets: `"blender"`, `"opencascade"`, `"openscad"`, `"jscad"`.

---

## Blender (`target="blender"`)

Generates Python (`bpy`) scripts that create a **Geometry Nodes** modifier in Blender.  
The generated file can be run directly in the Blender console or loaded as a script.

**Output extension:** `.py`  
**Additional mode:** `mode="direct"` executes the graph inside a running Blender instance via `bpy`.

### Primitives ✅ (full support)

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

### Operations ✅ (full support)

- **Booleans:** `union`, `difference`, `intersect` (`GeometryNodeMeshBoolean`)
- **Transforms:** `translate`, `rotate`, `scale_by`, `transform`, `set_position`
- **Join:** `GeometryNodeJoinGeometry`
- **Instance on points:** `GeometryNodeInstanceOnPoints`
- **~200 geometry ops** out of 223 total Blender nodes (~90%), including:
  - Mesh: extrude, subdivide, triangulate, dual mesh, flip faces, merge by distance, etc.
  - Curve: fill, fillet, resample, trim, subdivide, set spline type, etc.
  - Instance: realize, rotate, scale, translate, split to instances, etc.
  - Material: set, replace, set index
  - Attribute: store, remove
  - Volume: distribute points, points to volume
  - Field inputs: position, normal, index, edge angle, curvature, etc. (~37 nodes)
  - Math ops: scalar and vector math (~40 operations)

### Not supported ❌

- Grease Pencil nodes (basic pass-through, outputs not fully supported)
- Gizmo nodes (emitted as comments)
- Does not generate GPU-executable or GLSL files

---

## OpenCascade.js (`target="opencascade"`)

Generates **JavaScript ES Modules** for the [opencascade.js](https://ocjs.org/) library.  
The file exports a `setup_<name>(oc)` function that receives an initialised `oc` instance and returns a `TopoDS_Shape` (BREP).

**Output extension:** `.js`

### Primitives ✅

| Primitive | OCCT API |
|-----------|---------|
| `cube` | `BRepPrimAPI_MakeBox` |
| `sphere` | `BRepPrimAPI_MakeSphere` |
| `cylinder` | `BRepPrimAPI_MakeCylinder` |
| `cone` | `BRepPrimAPI_MakeCone` |
| `circle` | `gp_Circ` + `BRepBuilderAPI_MakeEdge` |
| `line` / `curve_line` | `BRepBuilderAPI_MakeEdge` |
| `curve_circle` | `gp_Circ` + `BRepBuilderAPI_MakeEdge` |
| `curve_arc` | `gp_Circ` + `BRepBuilderAPI_MakeEdge` with angular range |
| `bezier_segment` | `Geom_BezierCurve` + `BRepBuilderAPI_MakeEdge` |
| `quadratic_bezier` | `Geom_BezierCurve` (3 poles) |
| `curve_star` | Polygonal wire built vertex-by-vertex |
| `curve_spiral` | Polyline wire (approximation) |
| `curve_quadrilateral` | 4-edge wire |
| `point` | `BRepBuilderAPI_MakeVertex` |

### Approximations ⚠️

| Primitive | Note |
|-----------|------|
| `ico_sphere` | Approximated as UV sphere (`BRepPrimAPI_MakeSphere`) |
| `grid` | Approximated as a flat face (`BRepBuilderAPI_MakeFace`) |
| `curve_spiral` | Approximated as a polyline wire |
| `instance_on_points` | Iterates vertices of the points shape; builds transformed copies in a Compound |

### Operations ✅

| IR | OCCT API |
|----|---------|
| `union` | `BRepAlgoAPI_Fuse` |
| `difference` | `BRepAlgoAPI_Cut` |
| `intersect` | `BRepAlgoAPI_Common` |
| `translate` | `gp_Trsf` + `BRepBuilderAPI_Transform` |
| `rotate` (X/Y/Z) | `gp_Trsf::SetRotation` per axis |
| `scale` uniform | `gp_Trsf::SetScaleFactor` |
| `scale` non-uniform | `gp_GTrsf` + `BRepBuilderAPI_GTransform` |
| `join` | `TopoDS_Compound` + `BRep_Builder` |
| `extrude` | `BRepPrimAPI_MakePrism` |
| `fillet` | `BRepFilletAPI_MakeFillet` (all edges) |
| `fill_curve` | `BRepBuilderAPI_MakeFace` from wire |
| `curve_to_mesh` | `BRepOffsetAPI_MakePipe` |

### Not supported ❌

- `field_inputs`, `math_ops` (no BREP equivalent)
- `separate_components` (pass-through)
- `convex_hull` (not directly available in OCCT; pass-through)
- ~200 Blender geometry ops with no OCCT mapping (pass-through or ignored)
- Materials, attributes, UV, complex instancing

---

## OpenSCAD (`target="openscad"`)

Generates `.scad` files that can be run directly in [OpenSCAD](https://openscad.org/) or via CLI:

```bash
openscad -o output.stl output.scad
```

The generated code uses OpenSCAD's declarative language with nested indentation.

**Output extension:** `.scad`

### Primitives ✅

| Primitive | OpenSCAD |
|-----------|---------|
| `cube` | `cube([x,y,z])` centered |
| `sphere` | `sphere(r=...)` |
| `cylinder` | `cylinder(r=..., h=...)` centered |
| `cone` | `cylinder(r1=..., r2=..., h=...)` centered |
| `circle` | `circle(r=...)` (2D) |
| `grid` | `square([x,y])` (2D) / thin cube |
| `curve_circle` | `circle(r=...)` (2D) |
| `curve_quadrilateral` | `square([w,h], center=true)` (2D) |
| `curve_star` | `polygon(points=[...])` (2D) |
| `curve_arc` | `polygon(points=[...])` (angular approximation) |
| `bezier_segment` | `polygon(points=[...])` (polyline) |
| `quadratic_bezier` | `polygon(points=[...])` (polyline) |
| `line` / `curve_line` | `hull()` between two tiny spheres |
| `curve_spiral` | `union()` of `hull()` segments |

### Approximations ⚠️

| Primitive | Note |
|-----------|------|
| `ico_sphere` | Approximated as `sphere()` |
| `grid` | Very thin cube (`h=0.001`) |
| `volume_cube` | Solid `cube()` with the same bounding box |
| `line`, `curve_line` | `hull()` between two `sphere(r=0.01)` |
| `curve_spiral` | Chain of `hull()` between consecutive points |
| Bezier curves | Polyline with N segments |

### Operations ✅

| IR | OpenSCAD |
|----|---------|
| `union` | `union()` |
| `difference` | `difference()` |
| `intersect` | `intersection()` |
| `join` | `union()` |
| `translate` | `translate([x,y,z])` |
| `rotate` | `rotate([rx,ry,rz])` |
| `scale_by` | `scale([sx,sy,sz])` |
| `set_position` | `translate([ox,oy,oz])` |
| `extrude` | `linear_extrude(height=...)` |
| `fill_curve` | pass-through (the 2D shape is used directly) |
| `curve_to_mesh` | `linear_extrude(height=1)` of the profile |
| `convex_hull` | `hull()` |
| `scale_elements` | `scale([s,s,s])` |
| `rotate_instances` | `rotate(...)` |
| `scale_instances` | `scale(...)` |
| `translate_instances` | `translate(...)` |

### Not supported ❌

- `field_inputs`, `math_ops` (ignored, emitted as comments)
- `point` (no visible geometry; emitted as a comment)
- `instance_on_points` (naive union of instance shape + points)
- `separate_components` (pass-through)
- Subdivision surface, shade smooth, materials, attributes, UV — pass-through (geometry is preserved but the operation is ignored)

---

## JSCAD (`target="jscad"`)

Generates **CommonJS modules** for the [@jscad/modeling](https://github.com/jscad/OpenJSCAD.org) library.  
The file exports `{ main }` — `main()` is the standard JSCAD entry point.

```bash
npx @jscad/cli output.jscad -o output.stl
```

**Output extension:** `.jscad`

### Primitives ✅

| Primitive | JSCAD API |
|-----------|----------|
| `cube` | `primitives.cuboid({ size })` |
| `sphere` | `primitives.sphere({ radius, segments })` |
| `cylinder` | `primitives.cylinder({ radius, height, segments })` |
| `cone` | `primitives.cylinderElliptic({ startRadius, endRadius, height })` |
| `ico_sphere` | `primitives.geodesicSphere({ radius })` |
| `circle` | `primitives.circle({ radius, segments })` |
| `grid` | `primitives.rectangle({ size })` |
| `line` / `curve_line` | `primitives.line([p1, p2])` |
| `curve_circle` | `primitives.circle({ radius, segments })` |
| `curve_arc` | `primitives.arc({ radius, startAngle, endAngle, segments })` |
| `curve_star` | `primitives.star({ vertices, innerRadius, outerRadius })` |
| `curve_quadrilateral` | `primitives.rectangle({ size })` |
| `bezier_segment` | `primitives.line([...points])` (polyline) |
| `quadratic_bezier` | `primitives.line([...points])` (polyline) |
| `curve_spiral` | `primitives.line([...points])` (3D polyline) |
| `volume_cube` | `primitives.cuboid` centered on bounding box |
| `point` | `primitives.cuboid` of size 0.001 at the position |

### Operations ✅

| IR | JSCAD API |
|----|----------|
| `union` | `booleans.union(a, b, ...)` |
| `difference` | `booleans.subtract(a, b, ...)` |
| `intersect` | `booleans.intersect(a, b, ...)` |
| `join` | `booleans.union(a, b, ...)` |
| `translate` | `transforms.translate([x,y,z], shape)` |
| `rotate` | `transforms.rotate([rx,ry,rz], shape)` (radians) |
| `scale_by` | `transforms.scale([sx,sy,sz], shape)` |
| `set_position` | `transforms.translate(offset, shape)` |
| `extrude` | `extrusions.extrudeLinear({ height }, shape)` |
| `fill_curve` | pass-through (the 2D shape is used directly) |
| `curve_to_mesh` | `extrusions.extrudeLinear({ height: 1 }, profile)` |
| `convex_hull` | `hulls.hull(shape)` |
| `scale_elements` | `transforms.scale([s,s,s], shape)` |
| `rotate_instances` | `transforms.rotate(rot, shape)` |
| `scale_instances` | `transforms.scale(sc, shape)` |
| `translate_instances` | `transforms.translate(tr, shape)` |

### Not supported ❌

- `field_inputs`, `math_ops` (ignored, emitted as comments)
- `instance_on_points` (naive union of instance + points)
- `separate_components` (pass-through)
- Subdivision, shade smooth, materials, attributes, UV — pass-through or ignored

---

## Comparison summary

| Feature | Blender | OpenCascade.js | OpenSCAD | JSCAD |
|---------|:-------:|:--------------:|:--------:|:-----:|
| 3D primitives (cube/sphere/cyl/cone) | ✅ | ✅ | ✅ | ✅ |
| Curve primitives | ✅ | ✅ | ✅ (2D) | ✅ (2D) |
| Volume primitives | ✅ | ❌ | ⚠️ approx | ⚠️ approx |
| Boolean union/diff/intersect | ✅ | ✅ | ✅ | ✅ |
| Translate / Rotate / Scale | ✅ | ✅ | ✅ | ✅ |
| Join geometry | ✅ | ✅ (Compound) | ✅ | ✅ |
| Extrude | ✅ | ✅ (MakePrism) | ✅ | ✅ |
| Fillet | ✅ | ✅ | ❌ | ❌ |
| Convex hull | ✅ | ❌ (pass-through) | ✅ (`hull()`) | ✅ |
| Curve to mesh | ✅ | ✅ (MakePipe) | ⚠️ approx | ⚠️ approx |
| Instance on points | ✅ | ⚠️ approx | ⚠️ naive | ⚠️ naive |
| Subdivision | ✅ | ❌ | ❌ | ❌ |
| Materials | ✅ | ❌ | ❌ | ❌ |
| Attributes / UV | ✅ | ❌ | ❌ | ❌ |
| Field inputs (~37) | ✅ | ❌ | ❌ | ❌ |
| Math ops (~40) | ✅ | ❌ | ❌ | ❌ |
| Import OBJ/STL/PLY | ✅ | ❌ | ❌ | ❌ |
| Output format | `.py` (bpy) | `.js` (ES Module) | `.scad` | `.jscad` (CJS) |
| Direct mode | ✅ (`mode="direct"`) | ❌ | ❌ | ❌ |

**Legend:** ✅ Full support · ⚠️ Approximation / degraded · ❌ Not supported
