---
id: math-ops
title: Math Ops
sidebar_position: 8
---

# Math Ops

**Module:** `tanuki.dsl.math_ops`

Math operations let you build computed values inside geometry graphs — principally for the Blender backend.

:::info Backend support
Math ops are **only fully supported** by the Blender backend. Other backends emit them as comments.
:::

## Scalar math

### `math_op(a, operation, b=None, use_clamp=False) → IRMathOp`

Applies a scalar math operation. `a` and `b` can be IR nodes or plain floats.

```python
from tanuki.dsl.math_ops import math_op, vector_math_op

doubled  = math_op(index_field(), "MULTIPLY", 2.0)
clamped  = math_op(my_value, "MAXIMUM", 0.0, use_clamp=True)
```

### Supported scalar operations (~20)

`ADD`, `SUBTRACT`, `MULTIPLY`, `DIVIDE`, `MULTIPLY_ADD`, `POWER`, `LOGARITHM`, `SQRT`, `INVERSE_SQRT`, `ABSOLUTE`, `EXPONENT`, `MINIMUM`, `MAXIMUM`, `LESS_THAN`, `GREATER_THAN`, `SIGN`, `COMPARE`, `SMOOTH_MIN`, `SMOOTH_MAX`, `ROUND`, `FLOOR`, `CEIL`, `TRUNCATE`, `FRACTION`, `MODULO`, `WRAP`, `SNAP`, `PINGPONG`, `SINE`, `COSINE`, `TANGENT`, `ARCSINE`, `ARCCOSINE`, `ARCTANGENT`, `ARCTAN2`, `SINH`, `COSH`, `TANH`, `RADIANS`, `DEGREES`

## Vector math

### `vector_math_op(a, operation, b=None, scale=None) → IRMathOp`

Vector-specialised math.

```python
length = vector_math_op(position_field(), "LENGTH")
scaled = vector_math_op(position_field(), "SCALE", scale=2.0)
dot    = vector_math_op(normal_field(), "DOT_PRODUCT", position_field())
```

### Supported vector operations (~15)

`ADD`, `SUBTRACT`, `MULTIPLY`, `DIVIDE`, `MULTIPLY_ADD`, `CROSS_PRODUCT`, `PROJECT`, `REFLECT`, `REFRACT`, `FACEFORWARD`, `DOT_PRODUCT`, `DISTANCE`, `LENGTH`, `SCALE`, `NORMALIZE`, `ABSOLUTE`, `MINIMUM`, `MAXIMUM`, `FLOOR`, `CEIL`, `FRACTION`, `MODULO`, `WRAP`, `SNAP`, `SINE`, `COSINE`, `TANGENT`

## Other math helpers

### `mix(a, b, factor=0.5, data_type="FLOAT") → IRMathOp`

Linear interpolation.

```python
color = mix(color_a, color_b, factor=0.3, data_type="RGBA")
```

### `map_range(value, from_min, from_max, to_min, to_max, clamp=True) → IRMathOp`

Remap a value from one range to another.

```python
normalised = map_range(edge_angle(), 0.0, 3.14159, 0.0, 1.0)
```

### `clamp(value, min_val=0.0, max_val=1.0, clamp_type="MINMAX") → IRMathOp`

```python
safe = clamp(my_field, 0.0, 1.0)
```
