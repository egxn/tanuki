---
id: overview
title: Backends Overview
sidebar_position: 1
---

# Backends Overview

Tanuki compiles IR graphs to different targets via the `render()` function:

```python
from tanuki.backends import render

render(ctx.graph, target="<backend>")                          # → source code string
render(ctx.graph, target="<backend>", output_path="file.ext") # → writes file, returns Path
```

Available targets: `"blender"`, `"opencascade"`, `"openscad"`, `"jscad"`.

## Comparison matrix

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
| Convex hull | ✅ | ❌ pass-through | ✅ (`hull()`) | ✅ |
| Curve to mesh | ✅ | ✅ (MakePipe) | ⚠️ approx | ⚠️ approx |
| Instance on points | ✅ | ⚠️ approx | ⚠️ naive | ⚠️ naive |
| Subdivision surface | ✅ | ❌ | ❌ | ❌ |
| Materials | ✅ | ❌ | ❌ | ❌ |
| Attributes / UV | ✅ | ❌ | ❌ | ❌ |
| Field inputs (~37) | ✅ | ❌ | ❌ | ❌ |
| Math ops (~40) | ✅ | ❌ | ❌ | ❌ |
| Import OBJ/STL/PLY | ✅ | ❌ | ❌ | ❌ |
| Output format | `.py` (bpy) | `.js` (ESM) | `.scad` | `.jscad` (CJS) |
| Direct execution mode | ✅ `mode="direct"` | ❌ | ❌ | ❌ |

**Legend:** ✅ Full support · ⚠️ Approximation / degraded · ❌ Not supported

## Multi-graph rendering

You can render multiple graphs at once:

```python
# All graphs combined into one file (if extension matches)
render([graph_a, graph_b], target="openscad", output_path="combined.scad")

# Or write each graph to a separate file inside a directory
render([graph_a, graph_b], target="openscad", output_path="out/")
```

## Choosing a backend

| Use case | Recommended backend |
|----------|-------------------|
| Blender scenes / geometry nodes | `blender` |
| Watertight BREP solids for CAD/CAM | `opencascade` |
| Parametric printable models | `openscad` |
| Browser-based 3D geometry | `jscad` |
