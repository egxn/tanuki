---
id: overview
title: DSL Overview
sidebar_position: 1
---

# DSL Overview

The Tanuki DSL is a set of pure Python functions organised into modules under `tanuki.dsl`. All functions return immutable IR nodes — there is no shared state.

## Import style

The top-level `tanuki.dsl` package re-exports everything:

```python
from tanuki.dsl import *          # import all DSL symbols
```

Or import individual modules:

```python
from tanuki.dsl.context    import model, output
from tanuki.dsl.primitives import cube, sphere, cylinder
from tanuki.dsl.transforms import translate, rotate, scale_by
from tanuki.dsl.operations import union, difference, join
```

## Modules

| Module | Key exports | Description |
|--------|------------|-------------|
| `context` | `model`, `output` | Graph lifecycle |
| `primitives` | `cube`, `sphere`, `cylinder`, `cone`, `point`, `circle`, `grid`, `ico_sphere`, `line` | 3D/2D geometry primitives |
| `transforms` | `translate`, `rotate`, `scale_by`, `transform`, `set_position`, `pipe` | Positioning and scaling |
| `operations` | `union`, `difference`, `intersect`, `join` | Boolean operations |
| `curves` | `curve_arc`, `curve_circle`, `curve_line`, `curve_star`, `curve_spiral`, `bezier_segment`, `quadratic_bezier`, `curve_quadrilateral` | Curve primitives |
| `curve_ops` | `fill_curve`, `fillet_curve`, `resample_curve`, `trim_curve`, `subdivide_curve`, … | Curve modifiers |
| `mesh_ops` | `extrude`, `subdivide`, `subdivide_surface`, `triangulate`, `dual_mesh`, `merge_by_distance`, … | Mesh modifiers |
| `instancing` | `clones` | Instance geometry at a list of points |
| `instance_ops` | `realize_instances`, `rotate_instances`, `scale_instances`, `translate_instances`, … | Instance modifiers |
| `material_ops` | `set_material`, `replace_material`, `set_material_index` | Material assignment |
| `volume_ops` | `volume_cube`, `mesh_to_volume`, `volume_to_mesh`, `distribute_points_on_volume` | Volume geometry |
| `attribute_ops` | `store_named_attribute`, `remove_named_attribute` | Custom attributes |
| `other_ops` | `convex_hull`, `bounding_box`, `delete_geometry`, `separate_geometry`, `set_id`, … | Misc geometry ops |
| `importers` | `import_obj`, `import_stl`, `import_ply`, `import_csv`, `import_vdb` | File importers |
| `field_nodes` | `position_field`, `normal_field`, `index_field`, `edge_angle`, `curvature`, … | Field inputs (~37) |
| `math_ops` | `math_op`, `vector_math_op`, `mix`, `map_range`, `clamp` | Math operations (~40) |
| `custom` | `mesh_valence`, `mesh_curvature`, … | Custom composite nodes |

## The context manager

```python
with model("my_model") as ctx:
    # DSL calls inside the block are implicitly added to the current graph
    part = cube(10, 10, 10)
    output(part)

graph = ctx.graph   # IRGraph, ready for render()
```

`model()` uses Python's `contextvars` internally — it is thread-safe.

## The pipe operator `|`

Transform operations return an `Op` object (not a node). When you write `node | op`, the op wraps the node and returns a new node:

```python
a = cube(1, 1, 1)                         # IRPrimitive
b = a | translate(5, 0, 0)               # IRTransform wrapping a
c = b | rotate(0, 0, 45) | scale_by(2, 2, 2)  # chained
```

This is purely functional — `a` is never mutated.
