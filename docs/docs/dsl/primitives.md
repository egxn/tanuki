---
id: primitives
title: Primitives
sidebar_position: 2
---

# Primitives

**Module:** `tanuki.dsl.primitives`

All primitive functions return an `IRPrimitive` node.

## 3D Solid Primitives

### `cube(x, y, z, label=None, **kwargs)`

Box centered at the origin.

```python
cube(10, 5, 3)
cube(10, 5, 3, "base_plate")
```

### `sphere(r, label=None, segments=32, rings=16, **kwargs)`

UV sphere.

```python
sphere(1.5)
sphere(2.0, "ball", segments=64)
```

### `cylinder(r, depth, label=None, vertices=32, **kwargs)`

Cylinder centered at the origin, axis along Z.

```python
cylinder(3, 12)
cylinder(1.5, 8, "post", vertices=16)
```

### `cone(r_top, r_bottom, depth, label=None, vertices=32, **kwargs)`

Cone or truncated cone.

```python
cone(0.0, 2.0, 5.0)         # sharp cone
cone(0.5, 2.0, 5.0, "tip")  # truncated cone
```

### `ico_sphere(radius=1.0, subdivisions=2, label=None)`

Icosphere (better topology than UV sphere).

```python
ico_sphere(1.5)
ico_sphere(2.0, subdivisions=3)
```

## 2D Primitives

### `circle(vertices=32, radius=1.0, fill_type="NONE", label=None)`

Mesh circle. `fill_type` can be `"NONE"`, `"NGON"`, or `"TRIANGLE_FAN"`.

```python
circle(radius=2.0)
circle(vertices=6, radius=1.0, fill_type="NGON")  # hexagon
```

### `grid(size_x=1, size_y=1, vertices_x=2, vertices_y=2, label=None)`

Flat rectangular grid in the XY plane.

```python
grid(10, 10, vertices_x=5, vertices_y=5)
```

### `line(count=2, start=(0,0,0), end=(0,0,1), label=None)`

Mesh line (series of connected verts along a straight path).

```python
line(count=10, start=(0,0,-1), end=(0,0,1))
```

## Points

### `point(x=0, y=0, z=0, label=None)`

Single point geometry.

```python
point(0, 0, 5)
```

## Example — all primitives side by side

```python
from tanuki.dsl import *
from tanuki.backends import render

def showcase():
    with model("showcase") as ctx:
        spacing = 3.0
        parts = [
            cube(2, 2, 2, "cube"),
            sphere(1.0, "sphere")          | translate(spacing, 0, 0),
            cylinder(0.8, 2.0, "cylinder") | translate(spacing * 2, 0, 0),
            cone(0.0, 1.0, 2.0, "cone")   | translate(spacing * 3, 0, 0),
            ico_sphere(1.0, "iso")         | translate(spacing * 4, 0, 0),
            circle(radius=1.0, label="c")  | translate(spacing * 5, 0, 0),
            grid(2, 2, label="g")          | translate(spacing * 6, 0, 0),
            line(10, (0,0,-1), (0,0,1))    | translate(spacing * 7, 0, 0),
        ]
        output(join(parts))
    return ctx.graph

render(showcase(), target="blender", output_path="showcase.py")
```
