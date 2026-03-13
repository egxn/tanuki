"""Tests for the DSL layer — verify DSL functions produce correct IR trees."""

from tanuki.dsl import (
    cube,
    sphere,
    cylinder,
    cone,
    point,
    union,
    difference,
    intersect,
    join,
    transform,
    set_position,
    translate,
    rotate,
    scale_by,
    place,
    pipe,
    clones,
    model,
    output,
)
from tanuki.ir.nodes import (
    BooleanOp,
    IRBoolean,
    IRInstanceOnPoints,
    IRJoin,
    IROutput,
    IRPrimitive,
    IRSetPosition,
    IRTransform,
    PrimitiveType,
)


# ---------------------------------------------------------------------------
# Primitives
# ---------------------------------------------------------------------------


class TestPrimitives:
    def test_cube_simple(self):
        c = cube(10, 20, 5, "box")
        assert isinstance(c, IRPrimitive)
        assert c.primitive_type == PrimitiveType.CUBE
        assert c.properties["size"] == (10, 20, 5)
        assert c.label == "box"

    def test_cube_with_position(self):
        c = cube(1, 2, 3, "moved") | place(5, 0, 0)
        assert isinstance(c, IRSetPosition)
        assert c.offset == (5, 0, 0)
        assert isinstance(c.child, IRPrimitive)

    def test_cube_with_transform(self):
        c = cube(1, 2, 3, "rotated") | rotate(0, 0, 90)
        assert isinstance(c, IRTransform)
        assert c.rotation == (0, 0, 90)

    def test_cube_with_position_and_rotation(self):
        c = cube(1, 2, 3, "both") | rotate(90, 0, 0) | place(1, 2, 3)
        # pipe: rotate first, then place
        assert isinstance(c, IRSetPosition)
        assert isinstance(c.child, IRTransform)

    def test_sphere(self):
        s = sphere(5.0, "ball")
        assert isinstance(s, IRPrimitive)
        assert s.properties["radius"] == 5.0

    def test_sphere_with_segments(self):
        s = sphere(5.0, segments=16, rings=8)
        assert s.properties["segments"] == 16
        assert s.properties["rings"] == 8

    def test_cylinder(self):
        c = cylinder(2.5, 10.0, "tube")
        assert isinstance(c, IRPrimitive)
        assert c.properties["radius"] == 2.5
        assert c.properties["depth"] == 10.0
        assert c.properties["vertices"] == 32

    def test_cylinder_custom_vertices(self):
        c = cylinder(1, 5, vertices=64)
        assert c.properties["vertices"] == 64

    def test_cone(self):
        c = cone(5.0, 0.0, 10.0, "pointy")
        assert isinstance(c, IRPrimitive)
        assert c.properties["radius_top"] == 5.0
        assert c.properties["radius_bottom"] == 0.0
        assert c.properties["depth"] == 10.0

    def test_point(self):
        p = point(1, 2, 3, "dot")
        assert isinstance(p, IRPrimitive)
        assert p.primitive_type == PrimitiveType.POINT
        assert p.properties["position"] == (1, 2, 3)


# ---------------------------------------------------------------------------
# Boolean operations
# ---------------------------------------------------------------------------


class TestOperations:
    def test_union(self):
        a, b = cube(1, 1, 1, "a"), cube(2, 2, 2, "b")
        u = union([a, b])
        assert isinstance(u, IRBoolean)
        assert u.operation == BooleanOp.UNION
        assert len(u.children) == 2

    def test_difference(self):
        base = cylinder(5, 10, "base")
        hole = cylinder(3, 10, "hole")
        d = difference(base, [hole])
        assert d.operation == BooleanOp.DIFFERENCE
        assert d.children[0] is base
        assert d.children[1] is hole

    def test_intersect(self):
        a, b = cube(1, 1, 1), sphere(1)
        i = intersect([a, b])
        assert i.operation == BooleanOp.INTERSECT

    def test_join(self):
        a, b = cube(1, 1, 1), cube(2, 2, 2)
        j = join([a, b])
        assert isinstance(j, IRJoin)
        assert len(j.children) == 2


# ---------------------------------------------------------------------------
# Transforms
# ---------------------------------------------------------------------------


class TestTransforms:
    def test_transform_translation(self):
        c = cube(1, 1, 1, "c")
        t = transform(c, translation=(1, 2, 3))
        assert isinstance(t, IRTransform)
        assert t.translation == (1, 2, 3)
        assert t.child is c

    def test_transform_rotation(self):
        c = cube(1, 1, 1, "c")
        t = transform(c, rotation=(90, 0, 0))
        assert t.rotation == (90, 0, 0)

    def test_set_position(self):
        c = cube(1, 1, 1, "c")
        sp = set_position(c, (5, 0, 0))
        assert isinstance(sp, IRSetPosition)
        assert sp.offset == (5, 0, 0)

    def test_translate_curried(self):
        c = cube(1, 1, 1, "c")
        result = c | translate(1, 2, 3)
        assert isinstance(result, IRTransform)
        assert result.translation == (1, 2, 3)

    def test_rotate_curried(self):
        c = cube(1, 1, 1, "c")
        result = c | rotate(90, 0, 0)
        assert isinstance(result, IRTransform)
        assert result.rotation == (90, 0, 0)

    def test_scale_by_curried(self):
        c = cube(1, 1, 1, "c")
        result = c | scale_by(2, 2, 2)
        assert isinstance(result, IRTransform)
        assert result.scale == (2, 2, 2)

    def test_place_curried(self):
        c = cube(1, 1, 1, "c")
        result = c | place(5, 0, 0)
        assert isinstance(result, IRSetPosition)
        assert result.offset == (5, 0, 0)

    def test_pipe_utility(self):
        c = cube(1, 1, 1, "c")
        result = pipe(c, rotate(0, 90, 0), translate(0, 0, 5), place(1, 0, 0))
        assert isinstance(result, IRSetPosition)
        assert isinstance(result.child, IRTransform)
        assert isinstance(result.child.child, IRTransform)


# ---------------------------------------------------------------------------
# Instancing
# ---------------------------------------------------------------------------


class TestInstancing:
    def test_clones(self):
        s = cube(1, 1, 1, "sprocket")
        positions = [(0, 0, 0), (5, 0, 0), (10, 0, 0)]
        result = clones(s, positions)
        assert isinstance(result, IRInstanceOnPoints)
        assert result.instance is s
        assert isinstance(result.points, IRJoin)
        assert len(result.points.children) == 3


# ---------------------------------------------------------------------------
# Context / model
# ---------------------------------------------------------------------------


class TestModelContext:
    def test_basic_model(self):
        with model("test_part") as ctx:
            c = cube(10, 10, 10, "base")
            output(c)
        g = ctx.graph
        assert g.name == "test_part"
        assert g.root is not None
        assert isinstance(g.root, IROutput)

    def test_model_belt_holder(self):
        """Mirrors deprecated/lab/belt_holder.py"""
        with model("belt_holder") as ctx:
            base = cylinder(5.5, 15, "hole1")
            hole2 = cylinder(4.5, 15, "hole2")
            base = difference(base, [hole2])
            output(base)

        g = ctx.graph
        assert g.root is not None
        root_child = g.root.child
        assert isinstance(root_child, IRBoolean)
        assert root_child.operation == BooleanOp.DIFFERENCE
        assert len(root_child.children) == 2

    def test_model_tray(self):
        """Mirrors deprecated/lab/tray.py"""
        with model("tray") as ctx:
            base = cube(107.5, 31, 9, "base")
            h1 = cube(103, 31, 9, "h_base_1") | place(0, -2, 2)
            h2 = cube(23, 31, 9, "h_base_2") | place(0, 0, 2)
            base = difference(base, [h1, h2])
            output(base)

        g = ctx.graph
        root_child = g.root.child
        assert isinstance(root_child, IRBoolean)
        assert len(root_child.children) == 3  # target + 2 operands

    def test_model_claw_clones(self):
        """Mirrors deprecated/lab/claw.py clones pattern"""
        with model("claw") as ctx:
            sprocket = cube(2.5, 1.8, 3, "sprocket") | place(0, 0, 1)
            positions = [(5, y, 0) for y in range(3)]
            sprockets = clones(sprocket, positions)
            output(sprockets)

        g = ctx.graph
        root_child = g.root.child
        assert isinstance(root_child, IRInstanceOnPoints)
