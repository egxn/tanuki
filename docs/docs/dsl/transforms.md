---
id: transforms
title: Transforms
sidebar_position: 4
---

# Transforms

**Module:** `tanuki.dsl.transforms`

Transforms are available in two styles:

- **Curried** — return an `Op` object for use with `|`.
- **Direct** — take the node as the first argument.

## Curried (pipe-compatible)

### `translate(x=0, y=0, z=0) → Op`

Move along X, Y, Z.

```python
cube(1,1,1) | translate(5, 0, 0)
cube(1,1,1) | translate(x=5)
```

### `rotate(rx=0, ry=0, rz=0) → Op`

Rotate by degrees around each axis. Degrees are converted to radians automatically by each backend.

```python
cube(1,1,1) | rotate(0, 0, 45)
```

### `scale_by(sx=1, sy=1, sz=1) → Op`

Scale by a factor on each axis.

```python
cube(1,1,1) | scale_by(2, 2, 2)
cube(1,1,1) | scale_by(1, 1, 3)     # stretch along Z only
```

### `place(x=0, y=0, z=0) → Op`

Sets an offset position (compiles to `IRSetPosition`).

```python
cube(1,1,1) | place(0, 0, 5)
```

## Direct

### `transform(node, translation=None, rotation=None, scale=None) → IRTransform`

Full transform in a single call. All arguments are optional tuples `(x, y, z)`.

```python
part = transform(
    cube(2, 2, 2),
    translation=(5, 0, 0),
    rotation=(0, 0, 45),
    scale=(2, 2, 2),
)
```

### `set_position(node, position) → IRSetPosition`

Absolute position offset.

```python
part = set_position(cube(1,1,1), position=(0, 0, 10))
```

## Utility

### `pipe(node, *ops) → IRNode`

Apply a sequence of `Op` objects left-to-right, without `|`. Useful when building transforms programmatically.

```python
part = pipe(
    cube(1, 1, 1),
    translate(0, 5, 0),
    rotate(90, 0, 0),
    scale_by(2, 2, 2),
)
```

## Chaining example

```python
from tanuki.dsl import *
from tanuki.backends import render

with model("chain") as ctx:
    part = (
        cylinder(1.5, 8, "pillar")
        | translate(0, 0, 4)
        | rotate(0, 15, 0)
        | scale_by(1, 1, 1.5)
    )
    output(part)

print(render(ctx.graph, target="openscad"))
```
