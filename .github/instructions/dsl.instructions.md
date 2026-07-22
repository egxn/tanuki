# DSL Layer — Patterns and Conventions

## Import convention

Always use wildcard import from the top-level package:

```python
from tanuki.dsl import *
```

This re-exports every public DSL symbol. Individual module imports are fine for explicit narrowing.

## Model context manager

Every model must be wrapped in a `model()` context. The context implicitly registers nodes — you never pass the graph around manually.

```python
with model("my_part") as ctx:
    ...
    output(root_node)

graph = ctx.graph   # IRGraph, ready for render/export
```

- One `output()` call per `model()` block
- `model()` is thread-safe (uses Python `contextvars`)
- Nesting `model()` blocks is not supported

## Pipe operator `|`

Transform functions return an `Op` callable. Applying one to a node with `|` returns a **new** wrapped node — originals are never mutated.

```python
part = cube(10, 10, 2)
part = part | translate(0, 0, 5) | rotate(0, 0, 90) | scale_by(1, 1, 2)
```

Common pipeable ops: `translate`, `rotate`, `scale_by`, `place`, `set_material`, `set_shade_smooth`, `extrude`, `subdivide_surface`, `merge_by_distance`, `realize_instances`, `fill_curve`, `curve_to_mesh`, …

## Primitives

```python
cube(x, y, z, label="")                  # box
sphere(radius, label="")
cylinder(radius, depth, label="")        # axis = Z by default
cone(radius1, radius2, depth, label="")
circle(radius, label="")                 # 2D face
grid(x_size, y_size, x_segments, y_segments, label="")
ico_sphere(radius, subdivisions, label="")
line(count, length, label="")
point(label="")                          # single point
```

## Transforms

| Function | Signature | Notes |
|----------|-----------|-------|
| `translate` | `(x, y, z)` → Op | Curried (pipeable) |
| `rotate` | `(x, y, z)` → Op | Degrees, Euler XYZ |
| `scale_by` | `(x, y, z)` → Op | Curried (pipeable) |
| `place` | `(x, y, z)` → Op | Alias for translate; semantic "placement" |
| `transform` | `(node, x, y, z, rx, ry, rz, sx, sy, sz)` | Direct, returns node |
| `set_position` | `(node, x, y, z)` | Direct, returns node |
| `pipe` | `(node, *ops)` | Apply a sequence of ops at once |

## Boolean / join operations

```python
# All operations take a primary node and a list of cutters/others
result = difference(base, [hole1, hole2])
result = union([part_a, part_b, part_c])
result = intersect(body, [mask])
result = join([mesh_a, mesh_b])          # non-boolean merge
```

## Instancing

```python
points = [translate(x, y, 0) for x, y in positions]
instances = clones(source_node, points)
mesh = instances | realize_instances()
```

## Curves

```python
c = curve_circle(radius)
c = curve_arc(radius, start_angle, end_angle, resolution)
c = curve_line(start, end)
c = bezier_segment(start, end, handle1, handle2)
```

Curve ops (pipeable):
- `fill_curve()` — fill a closed curve into a face
- `fillet_curve(radius)` — round corners
- `resample_curve(count)` — uniform resampling
- `subdivide_curve(cuts)` — add control points
- `trim_curve(start, end)` — trim by factor
- `set_spline_cyclic(cyclic)` — close/open spline
- `curve_to_mesh(profile)` — sweep a profile along a curve

## Mesh ops (pipeable)

```python
part = circle(5) | fill_curve() | extrude(height=3) | set_shade_smooth()
part = mesh | subdivide_surface(level=2)
part = mesh | merge_by_distance(distance=0.01)
part = mesh | triangulate()
```

## Field nodes

Field nodes represent per-element data (position, index, normal, etc.). They are nodes like any other and are connected to ops that accept socket inputs.

```python
pos = position()       # per-vertex position vector
idx = index()          # per-element integer index
nm  = normal()         # per-face normal vector
```

## Math ops

```python
from tanuki.dsl import add, subtract, multiply, divide, sine, cosine, sqrt, ...

sum_val   = add(field_a, field_b)
scaled    = multiply(position(), factor_value)
```

## Store attributes

```python
geo = store_named_attribute(geo, name="density", value=some_field, data_type="FLOAT")
```

## Material assignment

```python
result = part | set_material("MyBlenderMaterial")
result = set_material_index(part, index=1)
```

## Common patterns

### Hollow cylinder (tube)
```python
outer = cylinder(r_outer, depth)
inner = cylinder(r_inner, depth)
tube  = difference(outer, [inner])
```

### Extruded 2D profile
```python
shape = circle(radius) | fill_curve() | extrude(height)
```

### Arrayed instances
```python
pts = [place(i * spacing, 0, 0) for i in range(count)]
arr = clones(source, pts) | realize_instances()
```

### Curve sweep (pipe/rail)
```python
path    = curve_line((0,0,0), (0,0,length))
profile = curve_circle(radius)
tube    = curve_to_mesh(path, profile)
```
