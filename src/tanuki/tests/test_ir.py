"""Tests for the IR layer — nodes and graph."""

import json

from tanuki.ir.nodes import (
    BooleanOp,
    IRBoolean,
    IRJoin,
    IRNode,
    IROutput,
    IRPrimitive,
    IRSetPosition,
    IRTransform,
    IRValue,
    IRVector,
    PrimitiveType,
)
from tanuki.ir.graph import IRGraph, add_node, set_root, to_dict


# ---------------------------------------------------------------------------
# IRNode basics
# ---------------------------------------------------------------------------


class TestIRNodes:
    def test_node_has_unique_id(self):
        a = IRNode()
        b = IRNode()
        assert a.id != b.id

    def test_node_is_frozen(self):
        n = IRNode(label="x")
        try:
            n.label = "y"
            assert False, "Should have raised"
        except AttributeError:
            pass

    def test_value_node(self):
        v = IRValue(value=3.14)
        assert v.value == 3.14

    def test_vector_node(self):
        v = IRVector(value=(1.0, 2.0, 3.0))
        assert v.value == (1.0, 2.0, 3.0)

    def test_pipe_operator(self):
        p = IRPrimitive(
            primitive_type=PrimitiveType.CUBE,
            label="box",
            properties={"size": (1.0, 1.0, 1.0)},
        )
        result = p | (lambda node: IRTransform(
            child=node,
            translation=(5.0, 0.0, 0.0),
            rotation=(0.0, 0.0, 0.0),
            scale=(1.0, 1.0, 1.0),
        ))
        assert isinstance(result, IRTransform)
        assert result.child is p
        assert result.translation == (5.0, 0.0, 0.0)

    def test_pipe_operator_non_callable(self):
        n = IRNode()
        result = n.__or__(42)
        assert result is NotImplemented


# ---------------------------------------------------------------------------
# IRPrimitive
# ---------------------------------------------------------------------------


class TestIRPrimitive:
    def test_cube(self):
        c = IRPrimitive(
            primitive_type=PrimitiveType.CUBE,
            label="box",
            properties={"size": (10.0, 20.0, 5.0)},
        )
        assert c.primitive_type == PrimitiveType.CUBE
        assert c.properties["size"] == (10.0, 20.0, 5.0)
        assert c.label == "box"

    def test_cylinder(self):
        cyl = IRPrimitive(
            primitive_type=PrimitiveType.CYLINDER,
            properties={"radius": 5.0, "depth": 10.0, "vertices": 32},
        )
        assert cyl.properties["radius"] == 5.0
        assert cyl.properties["vertices"] == 32


# ---------------------------------------------------------------------------
# IRBoolean
# ---------------------------------------------------------------------------


class TestIRBoolean:
    def test_union(self):
        a = IRPrimitive(primitive_type=PrimitiveType.CUBE)
        b = IRPrimitive(primitive_type=PrimitiveType.SPHERE)
        u = IRBoolean(operation=BooleanOp.UNION, children=(a, b))
        assert u.operation == BooleanOp.UNION
        assert len(u.children) == 2

    def test_difference_first_is_target(self):
        target = IRPrimitive(label="target")
        cut = IRPrimitive(label="cut")
        d = IRBoolean(operation=BooleanOp.DIFFERENCE, children=(target, cut))
        assert d.children[0].label == "target"


# ---------------------------------------------------------------------------
# IRTransform / IRSetPosition
# ---------------------------------------------------------------------------


class TestIRTransform:
    def test_translation(self):
        child = IRPrimitive()
        t = IRTransform(child=child, translation=(1.0, 2.0, 3.0))
        assert t.translation == (1.0, 2.0, 3.0)
        assert t.child is child

    def test_set_position(self):
        child = IRPrimitive()
        sp = IRSetPosition(child=child, offset=(5.0, 0.0, 0.0))
        assert sp.offset == (5.0, 0.0, 0.0)


# ---------------------------------------------------------------------------
# IRJoin / IRInstanceOnPoints / IROutput
# ---------------------------------------------------------------------------


class TestCompositeNodes:
    def test_join(self):
        a, b = IRPrimitive(), IRPrimitive()
        j = IRJoin(children=(a, b))
        assert len(j.children) == 2

    def test_output(self):
        child = IRPrimitive()
        out = IROutput(child=child)
        assert out.child is child


# ---------------------------------------------------------------------------
# IRGraph
# ---------------------------------------------------------------------------


class TestIRGraph:
    def test_empty_graph(self):
        g = IRGraph(name="test")
        assert g.name == "test"
        assert g.nodes == ()
        assert g.root is None

    def test_add_node_returns_new_graph(self):
        g = IRGraph()
        n = IRPrimitive(label="a")
        g2 = add_node(g, n)
        assert len(g.nodes) == 0  # original unchanged
        assert len(g2.nodes) == 1
        assert g2.nodes[0] is n

    def test_set_root(self):
        g = IRGraph()
        n = IRPrimitive(label="root")
        g2 = set_root(g, n)
        assert g2.root is not None
        assert isinstance(g2.root, IROutput)
        assert g2.root.child is n

    def test_set_root_with_output_node(self):
        g = IRGraph()
        out = IROutput(child=IRPrimitive())
        g2 = set_root(g, out)
        assert g2.root is out


# ---------------------------------------------------------------------------
# Serialisation
# ---------------------------------------------------------------------------


class TestSerialisation:
    def test_to_dict_simple(self):
        n = IRPrimitive(
            primitive_type=PrimitiveType.CUBE,
            label="box",
            properties={"size": (1.0, 2.0, 3.0)},
        )
        g = set_root(IRGraph(name="test"), n)
        d = to_dict(g)
        assert d["name"] == "test"
        assert d["root"]["type"] == "IROutput"
        # Should be JSON-serialisable
        json.dumps(d)

    def test_to_dict_nested(self):
        a = IRPrimitive(primitive_type=PrimitiveType.CUBE, label="a")
        b = IRPrimitive(primitive_type=PrimitiveType.CYLINDER, label="b")
        diff = IRBoolean(operation=BooleanOp.DIFFERENCE, children=(a, b))
        g = set_root(IRGraph(name="nested"), diff)
        d = to_dict(g)
        root_child = d["root"]["child"]
        assert root_child["type"] == "IRBoolean"
        assert len(root_child["children"]) == 2
        json.dumps(d)
