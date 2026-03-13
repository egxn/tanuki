"""Curve primitive constructors."""

from __future__ import annotations

from ..ir.nodes import IRPrimitive, PrimitiveType


def curve_arc(
    resolution: int = 16,
    radius: float = 1.0,
    start_angle: float = 0.0,
    sweep_angle: float = 315.0,
    label: str = "",
) -> IRPrimitive:
    """Create a curve arc."""
    return IRPrimitive(
        primitive_type=PrimitiveType.CURVE_ARC,
        label=label,
        properties={
            "resolution": resolution,
            "radius": radius,
            "start_angle": start_angle,
            "sweep_angle": sweep_angle,
        },
    )


def curve_circle(
    resolution: int = 32,
    radius: float = 1.0,
    label: str = "",
) -> IRPrimitive:
    """Create a curve circle."""
    return IRPrimitive(
        primitive_type=PrimitiveType.CURVE_CIRCLE,
        label=label,
        properties={"resolution": resolution, "radius": radius},
    )


def curve_line(
    start: tuple[float, float, float] = (0, 0, 0),
    end: tuple[float, float, float] = (0, 0, 1),
    label: str = "",
) -> IRPrimitive:
    """Create a curve line between two points."""
    return IRPrimitive(
        primitive_type=PrimitiveType.CURVE_LINE,
        label=label,
        properties={"start": start, "end": end},
    )


def curve_quadrilateral(
    width: float = 2.0,
    height: float = 2.0,
    label: str = "",
) -> IRPrimitive:
    """Create a curve quadrilateral (rectangle)."""
    return IRPrimitive(
        primitive_type=PrimitiveType.CURVE_QUADRILATERAL,
        label=label,
        properties={"width": width, "height": height},
    )


def curve_star(
    points: int = 8,
    inner_radius: float = 1.0,
    outer_radius: float = 2.0,
    label: str = "",
) -> IRPrimitive:
    """Create a curve star."""
    return IRPrimitive(
        primitive_type=PrimitiveType.CURVE_STAR,
        label=label,
        properties={
            "points": points,
            "inner_radius": inner_radius,
            "outer_radius": outer_radius,
        },
    )


def curve_spiral(
    resolution: int = 32,
    rotations: float = 2.0,
    start_radius: float = 1.0,
    end_radius: float = 2.0,
    height: float = 2.0,
    label: str = "",
) -> IRPrimitive:
    """Create a curve spiral."""
    return IRPrimitive(
        primitive_type=PrimitiveType.CURVE_SPIRAL,
        label=label,
        properties={
            "resolution": resolution,
            "rotations": rotations,
            "start_radius": start_radius,
            "end_radius": end_radius,
            "height": height,
        },
    )


def bezier_segment(
    resolution: int = 16,
    start: tuple[float, float, float] = (-1.0, 0.0, 0.0),
    start_handle: tuple[float, float, float] = (-0.5, 0.5, 0.0),
    end_handle: tuple[float, float, float] = (0.0, 0.0, 0.0),
    end: tuple[float, float, float] = (1.0, 0.0, 0.0),
    label: str = "",
) -> IRPrimitive:
    """Create a Bézier segment from control points and handles."""
    return IRPrimitive(
        primitive_type=PrimitiveType.CURVE_BEZIER_SEGMENT,
        label=label,
        properties={
            "resolution": resolution,
            "start": start,
            "start_handle": start_handle,
            "end_handle": end_handle,
            "end": end,
        },
    )


def quadratic_bezier(
    resolution: int = 16,
    start: tuple[float, float, float] = (-1.0, 0.0, 0.0),
    middle: tuple[float, float, float] = (0.0, 2.0, 0.0),
    end: tuple[float, float, float] = (1.0, 0.0, 0.0),
    label: str = "",
) -> IRPrimitive:
    """Create a quadratic Bézier curve (parabola shape)."""
    return IRPrimitive(
        primitive_type=PrimitiveType.CURVE_QUADRATIC_BEZIER,
        label=label,
        properties={
            "resolution": resolution,
            "start": start,
            "middle": middle,
            "end": end,
        },
    )
