---
id: operations
title: Operations
sidebar_position: 3
---

# Operations

**Module:** `tanuki.dsl.operations`

## Boolean operations

### `union(nodes: list[IRNode]) → IRBoolean`

Merge all geometries into a single shape.

```python
parts = [cube(1,1,1), sphere(0.8) | translate(1,0,0)]
merged = union(parts)
```

### `difference(base: IRNode, cutters: list[IRNode]) → IRBoolean`

Subtract `cutters` from `base`.

```python
shell = difference(
    sphere(2.0, "outer"),
    [sphere(1.8, "inner")],
)
```

### `intersect(nodes: list[IRNode]) → IRBoolean`

Keep only the volume shared by all nodes.

```python
lens = intersect([sphere(1.5) | translate(-0.5, 0, 0),
                  sphere(1.5) | translate( 0.5, 0, 0)])
```

## Join

### `join(nodes: list[IRNode]) → IRJoin`

Combine geometries without performing a boolean operation. The shapes remain as separate elements inside a single node. Useful for efficient instancing.

```python
assembly = join([body, leg_l, leg_r, top])
```

:::tip Boolean vs Join
Use `union()` when you need a watertight merged solid. Use `join()` to group shapes that don't need to be merged (e.g. for visual assembly, or before instancing). `join()` is always cheaper to compute.
:::

## Geometry ops (mesh_ops / other_ops)

These are more advanced operations exposed through the `mesh_ops` and `other_ops` modules. They produce an `IRGeometryOp` node.

```python
from tanuki.dsl.mesh_ops import extrude, subdivide, triangulate, convex_hull
from tanuki.dsl.other_ops import bounding_box, delete_geometry

solid = extrude(circle(radius=2), offset_scale=3.0)
fine  = subdivide(solid, level=2)
hull  = convex_hull(cluster_of_points)
```

See [Mesh Ops Reference](./primitives) and [Other Ops Reference](./primitives) for the full list.
