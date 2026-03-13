"""Immutable IR graph — a collection of nodes with a designated root.

All operations are pure functions that return new IRGraph instances.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace

from .nodes import IRNode, IROutput


@dataclass(frozen=True)
class IRGraph:
    """Immutable graph of IR nodes."""

    name: str = ""
    nodes: tuple[IRNode, ...] = ()
    root: IRNode | None = None


# ---------------------------------------------------------------------------
# Pure functional operations on IRGraph
# ---------------------------------------------------------------------------


def add_node(graph: IRGraph, node: IRNode) -> IRGraph:
    """Return a new graph with *node* appended."""
    return replace(graph, nodes=(*graph.nodes, node))


def set_root(graph: IRGraph, node: IRNode) -> IRGraph:
    """Return a new graph with *node* as the root output."""
    output = node if isinstance(node, IROutput) else IROutput(child=node, label="output")
    # Ensure output is also part of the nodes tuple
    if output not in graph.nodes:
        return replace(graph, nodes=(*graph.nodes, output), root=output)
    return replace(graph, root=output)


# ---------------------------------------------------------------------------
# Serialisation helpers
# ---------------------------------------------------------------------------


def _node_to_dict(node: IRNode) -> dict:
    """Recursively convert an IR node tree to a plain dict."""
    d: dict = {"type": type(node).__name__, "id": node.id, "label": node.label}
    for k, v in node.__dict__.items():
        if k in ("id", "label"):
            continue
        if isinstance(v, IRNode):
            d[k] = _node_to_dict(v)
        elif isinstance(v, tuple) and v and isinstance(v[0], IRNode):
            d[k] = [_node_to_dict(child) for child in v]
        elif isinstance(v, type) and issubclass(v, object):
            # Enum values
            d[k] = v.name if hasattr(v, "name") else str(v)
        else:
            d[k] = _enum_value(v)
    return d


def _enum_value(v):
    """Convert enum to its name, pass through everything else."""
    return v.name if hasattr(v, "name") and hasattr(v, "value") else v


def to_dict(graph: IRGraph) -> dict:
    """Serialise the full graph to a JSON-friendly dict."""
    return {
        "name": graph.name,
        "nodes": [_node_to_dict(n) for n in graph.nodes],
        "root": _node_to_dict(graph.root) if graph.root else None,
    }
