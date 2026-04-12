---
id: curves
title: Curves
sidebar_position: 5
---

# Curves

**Module:** `tanuki.dsl.curves`

Curve primitives return `IRPrimitive` nodes with a curve-specific `PrimitiveType`. They are 2D or parametric wire objects and are typically converted to mesh using `curve_to_mesh()` or filled with `fill_curve()`.

## Primitives

### `curve_arc(start_angle, sweep_angle, radius=1.0, resolution=16, label=None)`

A circular arc from `start_angle` to `start_angle + sweep_angle` (degrees).

```python
curve_arc(start_angle=0, sweep_angle=120, radius=2.0)
```

### `curve_circle(radius=1.0, resolution=32, label=None)`

A full circle wire.

```python
curve_circle(radius=1.5)
```

### `curve_line(start=(0,0,0), end=(0,0,1), label=None)`

Straight curve segment between two points.

```python
curve_line(start=(0,0,0), end=(5,0,0))
```

### `curve_quadrilateral(width=2.0, height=2.0, label=None)`

Rectangular wire.

```python
curve_quadrilateral(width=4.0, height=2.0)
```

### `curve_star(points=5, inner_radius=0.5, outer_radius=1.0, label=None)`

Star-shaped wire.

```python
curve_star(points=6, inner_radius=0.4, outer_radius=1.0)
```

### `curve_spiral(rotations=2, start_radius=0.2, end_radius=2.0, height=0.0, label=None)`

Archimedean spiral.

```python
curve_spiral(rotations=4, start_radius=0.1, end_radius=3.0)
```

### `bezier_segment(start, end, start_handle, end_handle, label=None)`

Cubic Bézier curve segment.

```python
bezier_segment(
    start=(0, 0, 0), end=(4, 0, 0),
    start_handle=(1, 2, 0), end_handle=(3, 2, 0),
)
```

### `quadratic_bezier(start, end, middle, label=None)`

Quadratic Bézier curve (3 control points).

```python
quadratic_bezier(start=(0,0,0), middle=(2,3,0), end=(4,0,0))
```

## Curve Operations

**Module:** `tanuki.dsl.curve_ops`

| Function | Description |
|----------|-------------|
| `fill_curve(node)` | Fill a closed curve into a face |
| `fillet_curve(node, count, radius, limit_radius)` | Round curve corners |
| `resample_curve(node, count)` | Resample to N points |
| `trim_curve(node, start, end)` | Keep a parametric range |
| `subdivide_curve(node, cuts)` | Add control points |
| `reverse_curve(node)` | Reverse direction |
| `set_spline_cyclic(node, cyclic)` | Close/open a spline |
| `set_spline_type(node, spline_type)` | Change spline type |
| `curve_to_points(node, count)` | Sample points along curve |

## Example

```python
from tanuki.dsl import *
from tanuki.dsl.curve_ops import fill_curve
from tanuki.dsl.mesh_ops import extrude, curve_to_mesh
from tanuki.backends import render

with model("coin") as ctx:
    outline = curve_circle(radius=1.5)
    face    = fill_curve(outline)
    coin    = extrude(face, offset_scale=0.2)
    output(coin)

render(ctx.graph, target="blender", output_path="coin.py")
```
