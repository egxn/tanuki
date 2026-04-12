---
id: overview
title: IR Overview
sidebar_position: 1
---

# IR Layer

**Module:** `tanuki.ir`

The IR (Intermediate Representation) is the immutable graph that sits between the DSL and the backends. All DSL functions ultimately produce IR nodes. All backends consume IR nodes.

Everything in the IR is a **frozen dataclass** — once created, nodes cannot be modified.

## Key types

### `IRPrimitive`

A leaf node representing a single piece of geometry.

```python
@dataclass(frozen=True)
class IRPrimitive:
    primitive_type: PrimitiveType
    label: str
    params: dict[str, Any]
```

### `IRBoolean`

A boolean combination of two or more child nodes.

```python
@dataclass(frozen=True)
class IRBoolean:
    op: BooleanOp          # UNION | DIFFERENCE | INTERSECT
    children: tuple[IRNode, ...]
    label: str
```

### `IRTransform`

Wraps a node with a spatial transform.

```python
@dataclass(frozen=True)
class IRTransform:
    child: IRNode
    translation: tuple[float, float, float] | None
    rotation: tuple[float, float, float] | None    # degrees
    scale: tuple[float, float, float] | None
    label: str
```

### `IRSetPosition`

Sets an explicit position offset (maps to a different node type in Blender).

### `IRJoin`

Groups multiple nodes without boolean merging.

```python
@dataclass(frozen=True)
class IRJoin:
    children: tuple[IRNode, ...]
    label: str
```

### `IRInstanceOnPoints`

Instances a shape at each point of a points geometry.

```python
@dataclass(frozen=True)
class IRInstanceOnPoints:
    points: IRNode
    instance: IRNode
    label: str
```

### `IRGeometryOp`

Any mesh/curve/volume operation beyond primitives and booleans.

```python
@dataclass(frozen=True)
class IRGeometryOp:
    op_type: str           # e.g. "extrude", "subdivide", "fill_curve"
    child: IRNode
    params: dict[str, Any]
    label: str
```

### `IRSeparateComponents`

Extracts a specific component type (`"MESH"`, `"CURVE"`, `"POINT_CLOUD"`, etc.) from a geometry.

### `IRFieldInput`

A field input node (position, normal, index, …).

### `IRMathOp`

A scalar or vector math operation.

### `IROutput`

The root node marking the final output of the graph.

### `IRValue` / `IRVector`

Constant scalar or 3-tuple value nodes for use as inputs to ops.

## `IRGraph`

```python
@dataclass
class IRGraph:
    name: str
    root: IRNode
```

The graph only holds a name and the root node. Because all nodes are immutable and reference their children, the entire tree is reachable from `root`.

## `PrimitiveType` enum

All primitives are identified by `PrimitiveType`:

```
CUBE, SPHERE, CYLINDER, CONE, POINT, CIRCLE, GRID, ICO_SPHERE, LINE,
CURVE_ARC, CURVE_CIRCLE, CURVE_LINE, CURVE_QUADRILATERAL, CURVE_STAR,
CURVE_SPIRAL, CURVE_BEZIER_SEGMENT, CURVE_QUADRATIC_BEZIER,
VOLUME_CUBE,
IMPORT_OBJ, IMPORT_STL, IMPORT_PLY, IMPORT_CSV, IMPORT_VDB,
COLLECTION_INFO, OBJECT_INFO
```

## `BooleanOp` enum

```
UNION, DIFFERENCE, INTERSECT
```
