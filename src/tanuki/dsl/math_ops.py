"""Math operations — scalar and vector math nodes.

These mirror Blender's ``ShaderNodeMath`` and ``ShaderNodeVectorMath``
nodes, producing field values that can be wired into geometry inputs.
"""

from __future__ import annotations

from ..ir.nodes import IRMathOp, IRNode


# ---------------------------------------------------------------------------
# Scalar math  (ShaderNodeMath)
# ---------------------------------------------------------------------------

def math_add(a: IRNode, b: IRNode, *, clamp: bool = False) -> IRMathOp:
    """``a + b`` (scalar)."""
    return IRMathOp(math_type="ShaderNodeMath", operation="ADD",
                    inputs={"Value": a, "Value_001": b}, clamp=clamp, label="add")


def math_subtract(a: IRNode, b: IRNode, *, clamp: bool = False) -> IRMathOp:
    """``a - b`` (scalar)."""
    return IRMathOp(math_type="ShaderNodeMath", operation="SUBTRACT",
                    inputs={"Value": a, "Value_001": b}, clamp=clamp, label="subtract")


def math_multiply(a: IRNode, b: IRNode, *, clamp: bool = False) -> IRMathOp:
    """``a * b`` (scalar)."""
    return IRMathOp(math_type="ShaderNodeMath", operation="MULTIPLY",
                    inputs={"Value": a, "Value_001": b}, clamp=clamp, label="multiply")


def math_divide(a: IRNode, b: IRNode, *, clamp: bool = False) -> IRMathOp:
    """``a / b`` (scalar)."""
    return IRMathOp(math_type="ShaderNodeMath", operation="DIVIDE",
                    inputs={"Value": a, "Value_001": b}, clamp=clamp, label="divide")


def math_power(base: IRNode, exponent: IRNode, *, clamp: bool = False) -> IRMathOp:
    """``base ** exponent`` (scalar)."""
    return IRMathOp(math_type="ShaderNodeMath", operation="POWER",
                    inputs={"Value": base, "Value_001": exponent}, clamp=clamp, label="power")


def math_sqrt(a: IRNode, *, clamp: bool = False) -> IRMathOp:
    """Square root (scalar)."""
    return IRMathOp(math_type="ShaderNodeMath", operation="SQRT",
                    inputs={"Value": a}, clamp=clamp, label="sqrt")


def math_absolute(a: IRNode, *, clamp: bool = False) -> IRMathOp:
    """Absolute value (scalar)."""
    return IRMathOp(math_type="ShaderNodeMath", operation="ABSOLUTE",
                    inputs={"Value": a}, clamp=clamp, label="abs")


def math_minimum(a: IRNode, b: IRNode) -> IRMathOp:
    """``min(a, b)`` (scalar)."""
    return IRMathOp(math_type="ShaderNodeMath", operation="MINIMUM",
                    inputs={"Value": a, "Value_001": b}, label="min")


def math_maximum(a: IRNode, b: IRNode) -> IRMathOp:
    """``max(a, b)`` (scalar)."""
    return IRMathOp(math_type="ShaderNodeMath", operation="MAXIMUM",
                    inputs={"Value": a, "Value_001": b}, label="max")


def math_less_than(a: IRNode, b: IRNode) -> IRMathOp:
    """``1.0 if a < b else 0.0`` (scalar)."""
    return IRMathOp(math_type="ShaderNodeMath", operation="LESS_THAN",
                    inputs={"Value": a, "Value_001": b}, label="less_than")


def math_greater_than(a: IRNode, b: IRNode) -> IRMathOp:
    """``1.0 if a > b else 0.0`` (scalar)."""
    return IRMathOp(math_type="ShaderNodeMath", operation="GREATER_THAN",
                    inputs={"Value": a, "Value_001": b}, label="greater_than")


# Trigonometric
def math_sin(a: IRNode) -> IRMathOp:
    """``sin(a)`` (scalar, radians)."""
    return IRMathOp(math_type="ShaderNodeMath", operation="SINE",
                    inputs={"Value": a}, label="sin")


def math_cos(a: IRNode) -> IRMathOp:
    """``cos(a)`` (scalar, radians)."""
    return IRMathOp(math_type="ShaderNodeMath", operation="COSINE",
                    inputs={"Value": a}, label="cos")


def math_tan(a: IRNode) -> IRMathOp:
    """``tan(a)`` (scalar, radians)."""
    return IRMathOp(math_type="ShaderNodeMath", operation="TANGENT",
                    inputs={"Value": a}, label="tan")


def math_arctan2(a: IRNode, b: IRNode) -> IRMathOp:
    """``atan2(a, b)`` (scalar)."""
    return IRMathOp(math_type="ShaderNodeMath", operation="ARCTAN2",
                    inputs={"Value": a, "Value_001": b}, label="arctan2")


# Rounding
def math_floor(a: IRNode) -> IRMathOp:
    return IRMathOp(math_type="ShaderNodeMath", operation="FLOOR",
                    inputs={"Value": a}, label="floor")


def math_ceil(a: IRNode) -> IRMathOp:
    return IRMathOp(math_type="ShaderNodeMath", operation="CEIL",
                    inputs={"Value": a}, label="ceil")


def math_round(a: IRNode) -> IRMathOp:
    return IRMathOp(math_type="ShaderNodeMath", operation="ROUND",
                    inputs={"Value": a}, label="round")


def math_modulo(a: IRNode, b: IRNode) -> IRMathOp:
    return IRMathOp(math_type="ShaderNodeMath", operation="MODULO",
                    inputs={"Value": a, "Value_001": b}, label="modulo")


# ---------------------------------------------------------------------------
# Vector math  (ShaderNodeVectorMath)
# ---------------------------------------------------------------------------

def vec_add(a: IRNode, b: IRNode) -> IRMathOp:
    """``a + b`` (vector)."""
    return IRMathOp(math_type="ShaderNodeVectorMath", operation="ADD",
                    inputs={"Vector": a, "Vector_001": b}, label="vec_add")


def vec_subtract(a: IRNode, b: IRNode) -> IRMathOp:
    """``a - b`` (vector)."""
    return IRMathOp(math_type="ShaderNodeVectorMath", operation="SUBTRACT",
                    inputs={"Vector": a, "Vector_001": b}, label="vec_subtract")


def vec_multiply(a: IRNode, b: IRNode) -> IRMathOp:
    """Component-wise ``a * b`` (vector)."""
    return IRMathOp(math_type="ShaderNodeVectorMath", operation="MULTIPLY",
                    inputs={"Vector": a, "Vector_001": b}, label="vec_multiply")


def vec_divide(a: IRNode, b: IRNode) -> IRMathOp:
    """Component-wise ``a / b`` (vector)."""
    return IRMathOp(math_type="ShaderNodeVectorMath", operation="DIVIDE",
                    inputs={"Vector": a, "Vector_001": b}, label="vec_divide")


def vec_cross(a: IRNode, b: IRNode) -> IRMathOp:
    """Cross product (vector)."""
    return IRMathOp(math_type="ShaderNodeVectorMath", operation="CROSS_PRODUCT",
                    inputs={"Vector": a, "Vector_001": b}, label="vec_cross")


def vec_dot(a: IRNode, b: IRNode) -> IRMathOp:
    """Dot product (scalar output)."""
    return IRMathOp(math_type="ShaderNodeVectorMath", operation="DOT_PRODUCT",
                    inputs={"Vector": a, "Vector_001": b}, label="vec_dot")


def vec_normalize(a: IRNode) -> IRMathOp:
    """Normalize vector to unit length."""
    return IRMathOp(math_type="ShaderNodeVectorMath", operation="NORMALIZE",
                    inputs={"Vector": a}, label="vec_normalize")


def vec_length(a: IRNode) -> IRMathOp:
    """Length of vector (scalar output)."""
    return IRMathOp(math_type="ShaderNodeVectorMath", operation="LENGTH",
                    inputs={"Vector": a}, label="vec_length")


def vec_distance(a: IRNode, b: IRNode) -> IRMathOp:
    """Distance between two vectors (scalar output)."""
    return IRMathOp(math_type="ShaderNodeVectorMath", operation="DISTANCE",
                    inputs={"Vector": a, "Vector_001": b}, label="vec_distance")


def vec_scale(vector: IRNode, scale: IRNode) -> IRMathOp:
    """Scale vector by scalar factor."""
    return IRMathOp(math_type="ShaderNodeVectorMath", operation="SCALE",
                    inputs={"Vector": vector, "Scale": scale}, label="vec_scale")


def vec_project(a: IRNode, b: IRNode) -> IRMathOp:
    """Project *a* onto *b*."""
    return IRMathOp(math_type="ShaderNodeVectorMath", operation="PROJECT",
                    inputs={"Vector": a, "Vector_001": b}, label="vec_project")


def vec_reflect(a: IRNode, b: IRNode) -> IRMathOp:
    """Reflect *a* around *b*."""
    return IRMathOp(math_type="ShaderNodeVectorMath", operation="REFLECT",
                    inputs={"Vector": a, "Vector_001": b}, label="vec_reflect")


def vec_faceforward(a: IRNode, b: IRNode, c: IRNode) -> IRMathOp:
    """Faceforward: flip *a* to point away from *b* relative to *c*."""
    return IRMathOp(math_type="ShaderNodeVectorMath", operation="FACEFORWARD",
                    inputs={"Vector": a, "Vector_001": b, "Vector_002": c},
                    label="vec_faceforward")


def vec_minimum(a: IRNode, b: IRNode) -> IRMathOp:
    """Component-wise minimum (vector)."""
    return IRMathOp(math_type="ShaderNodeVectorMath", operation="MINIMUM",
                    inputs={"Vector": a, "Vector_001": b}, label="vec_min")


def vec_maximum(a: IRNode, b: IRNode) -> IRMathOp:
    """Component-wise maximum (vector)."""
    return IRMathOp(math_type="ShaderNodeVectorMath", operation="MAXIMUM",
                    inputs={"Vector": a, "Vector_001": b}, label="vec_max")


def vec_floor(a: IRNode) -> IRMathOp:
    """Component-wise floor (vector)."""
    return IRMathOp(math_type="ShaderNodeVectorMath", operation="FLOOR",
                    inputs={"Vector": a}, label="vec_floor")


def vec_ceil(a: IRNode) -> IRMathOp:
    """Component-wise ceil (vector)."""
    return IRMathOp(math_type="ShaderNodeVectorMath", operation="CEIL",
                    inputs={"Vector": a}, label="vec_ceil")


def vec_absolute(a: IRNode) -> IRMathOp:
    """Component-wise absolute (vector)."""
    return IRMathOp(math_type="ShaderNodeVectorMath", operation="ABSOLUTE",
                    inputs={"Vector": a}, label="vec_abs")


def vec_sin(a: IRNode) -> IRMathOp:
    """Component-wise sin (vector)."""
    return IRMathOp(math_type="ShaderNodeVectorMath", operation="SINE",
                    inputs={"Vector": a}, label="vec_sin")


def vec_cos(a: IRNode) -> IRMathOp:
    """Component-wise cos (vector)."""
    return IRMathOp(math_type="ShaderNodeVectorMath", operation="COSINE",
                    inputs={"Vector": a}, label="vec_cos")


def vec_tan(a: IRNode) -> IRMathOp:
    """Component-wise tan (vector)."""
    return IRMathOp(math_type="ShaderNodeVectorMath", operation="TANGENT",
                    inputs={"Vector": a}, label="vec_tan")
