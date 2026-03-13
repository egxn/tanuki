"""Model context — the single point of mutable state in the DSL.

Uses contextvars for thread-safe implicit access.  The context manager
ensures proper setup/teardown and collects the final IRGraph.
"""

from __future__ import annotations

from contextvars import ContextVar
from dataclasses import replace

from ..ir.graph import IRGraph, set_root
from ..ir.nodes import IRNode, IROutput


_current_graph: ContextVar[IRGraph | None] = ContextVar("_current_graph", default=None)


def _get_graph() -> IRGraph:
    g = _current_graph.get()
    if g is None:
        raise RuntimeError("No active model context. Use `with model(name):` first.")
    return g


def _set_graph(graph: IRGraph) -> None:
    _current_graph.set(graph)


class ModelContext:
    """Context manager that holds the active IRGraph for a model."""

    def __init__(self, name: str) -> None:
        self.name = name
        self._graph: IRGraph | None = None
        self._token = None

    def __enter__(self) -> ModelContext:
        self._graph = IRGraph(name=self.name)
        self._token = _current_graph.set(self._graph)
        return self

    def __exit__(self, *_exc) -> None:
        self._graph = _current_graph.get()
        _current_graph.reset(self._token)

    @property
    def graph(self) -> IRGraph:
        if self._graph is None:
            raise RuntimeError("Context not entered yet.")
        return self._graph


def model(name: str) -> ModelContext:
    """Create a new model context.

    Usage::

        with model("my_part") as ctx:
            part = cube(10, 10, 10, "base")
            output(part)
        graph = ctx.graph
    """
    return ModelContext(name)


def output(node: IRNode) -> IROutput:
    """Mark *node* as the output of the current model.

    Pure: creates an IROutput wrapping *node* and sets it as the graph root.
    """
    out = IROutput(child=node, label="output")
    graph = _get_graph()
    _set_graph(set_root(graph, out))
    return out
