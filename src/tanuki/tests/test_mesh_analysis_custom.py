import ast

from tanuki.backends.blender.compiler import compile_to_source
from tanuki.dsl import cube, model, output
from tanuki.dsl.custom import (
    angles_group,
    flattened_angles_group,
    mesh_analysis_planar,
    mesh_analysis_split,
)
from tanuki.ir.nodes import IRFieldInput, IRGeometryOp, IRJoin, IRMathOp, IRNode, IRTransform


def _compile_model(name: str, build_fn) -> str:
    with model(name) as ctx:
        build_fn()
    return compile_to_source(ctx.graph)


def _assert_valid_python(source: str) -> None:
    ast.parse(source)


def _walk(node: IRNode):
    yield node

    if isinstance(node, IRGeometryOp):
        if node.child is not None:
            yield from _walk(node.child)
        for extra_child in node.extra_children.values():
            yield from _walk(extra_child)
        return

    if isinstance(node, IRJoin):
        for child in node.children:
            yield from _walk(child)
        return

    if isinstance(node, IRTransform) and node.child is not None:
        yield from _walk(node.child)
        return

    if isinstance(node, IRMathOp):
        for child in node.inputs.values():
            yield from _walk(child)


class TestMeshAnalysisCustomIR:
    def test_angles_group_returns_visible_curves(self):
        node = cube(1, 1, 1) | angles_group(arm_length=0.25)

        assert isinstance(node, IRGeometryOp)
        assert node.op_type == "GeometryNodePointsToCurves"
        assert set(node.extra_children) == {"Curve Group ID", "Weight"}
        assert isinstance(node.child, IRJoin)
        assert len(node.child.children) == 3

    def test_flattened_angles_group_uses_interior_dihedral_without_normalize(self):
        node = cube(1, 1, 1) | flattened_angles_group(arm_length=0.25, plane="XY")

        math_ops = {
            current.operation
            for current in _walk(node)
            if isinstance(current, IRMathOp)
        }
        field_types = {
            current.field_type
            for current in _walk(node)
            if isinstance(current, IRFieldInput)
        }

        assert "GeometryNodeInputMeshEdgeAngle" in field_types
        assert "SUBTRACT" in math_ops
        assert "NORMALIZE" not in math_ops

    def test_flattened_angles_group_rejects_invalid_plane(self):
        mesh = cube(1, 1, 1)

        try:
            mesh | flattened_angles_group(plane="AB")
        except ValueError as exc:
            assert "Unsupported plane" in str(exc)
        else:
            raise AssertionError("Expected invalid plane to raise ValueError")

    def test_mesh_analysis_split_returns_all_groups(self):
        parts = mesh_analysis_split(cube(1, 1, 1), arm_length=0.4, flatten_plane="YZ")

        assert set(parts) == {"edges", "faces", "angles", "flat_angles"}

    def test_mesh_analysis_planar_offsets_groups(self):
        parts = mesh_analysis_planar(cube(1, 1, 1), arm_length=0.3, spacing=7.0)

        assert set(parts) == {"edges", "faces", "flat_angles"}
        assert isinstance(parts["faces"], IRTransform)
        assert parts["faces"].translation == (7.0, 0.0, 0.0)
        assert isinstance(parts["flat_angles"], IRTransform)
        assert parts["flat_angles"].translation == (14.0, 0.0, 0.0)


class TestMeshAnalysisCustomCompiler:
    def test_flattened_angles_group_compiles_with_ordered_curve_inputs(self):
        src = _compile_model(
            "flat_edge_connectors",
            lambda: output(cube(1, 1, 1) | flattened_angles_group(arm_length=0.3, plane="XZ")),
        )

        _assert_valid_python(src)
        assert "GeometryNodePointsToCurves" in src
        assert 'inputs["Curve Group ID"]' in src
        assert 'inputs["Weight"]' in src
        assert "GeometryNodeInputMeshEdgeAngle" in src
        assert 'operation = "SUBTRACT"' in src