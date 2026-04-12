---
id: instancing
title: Instancing
sidebar_position: 6
---

# Instancing

Tanuki supports efficient geometry instancing — stamping the same shape at many positions.

## `clones(node, positions) → IRInstanceOnPoints`

**Module:** `tanuki.dsl.instancing`

Instance `node` at each position in `positions`. The positions list can be a list of `(x, y, z)` tuples.

```python
from tanuki.dsl import *
from tanuki.backends import render

with model("grid_of_bolts") as ctx:
    bolt = cylinder(0.5, 3, "bolt")
    positions = [
        (x * 5, y * 5, 0)
        for x in range(4)
        for y in range(4)
    ]
    bolts = clones(bolt, positions)
    base  = cube(20, 20, 1, "base")
    output(join([base, bolts]))

render(ctx.graph, target="blender", output_path="bolts.py")
```

## Instance operations

**Module:** `tanuki.dsl.instance_ops`

After instancing you can apply per-instance transforms:

| Function | Description |
|----------|-------------|
| `realize_instances(node)` | Convert instances to real geometry |
| `rotate_instances(node, rx, ry, rz)` | Rotate each instance |
| `scale_instances(node, sx, sy, sz)` | Scale each instance |
| `translate_instances(node, x, y, z)` | Offset each instance |
| `split_to_instances(node)` | Split geometry into individual instances |

```python
from tanuki.dsl.instance_ops import rotate_instances, realize_instances

scattered = clones(sphere(0.5), [(i*2, 0, 0) for i in range(6)])
rotated   = rotate_instances(scattered, rx=0, ry=0, rz=45)
real_mesh = realize_instances(rotated)
```

## Claw example with sprocket instancing

```python
from tanuki.dsl import *

def create_claw():
    with model("claw") as ctx:
        leg_l = cube(5.5, 50, 2, "leg_l", position=(14.75, 0, 0))
        leg_r = cube(5.5, 50, 2, "leg_r", position=(-14.75, 0, 0))
        top   = cube(35, 10, 2,  "top",   position=(0, 25, 0))

        hook   = cylinder(12, 2, "hook",   position=(0, 35, 0))
        h_hook = cylinder(8,  2, "h_hook", position=(0, 35, 0))
        hook   = difference(hook, [h_hook])

        sprocket  = cube(2.5, 1.8, 3, "sprocket", position=(0, 0, 1))
        positions = [(x, y, 0) for y in range(9) for x in [14, -14]]
        sprockets = clones(sprocket, positions)

        claw = union([leg_l, leg_r, top, hook, sprockets])
        output(claw)
    return ctx.graph
```

:::note Backend support
`IRInstanceOnPoints` is natively supported in the **Blender** backend (maps to `GeometryNodeInstanceOnPoints`). Other backends approximate it by iterating the point positions explicitly.
:::
