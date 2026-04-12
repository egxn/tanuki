"""Backend compilers for geometry IR.

Provides a unified ``render()`` function to compile or execute IR graphs.
Accepts a single graph or a sequence of graphs for batch export.
"""

from __future__ import annotations

from pathlib import Path
from typing import Sequence, Union

from ..ir.graph import IRGraph

_VALID_TARGETS = {"blender", "jscad", "opencascade", "openscad"}


def render(
    graph: IRGraph | Sequence[IRGraph],
    target: str = "blender",
    mode: str = "script",
    output_path: str | Path | None = None,
) -> str | Path | list[Path] | None:
    """Render one or more IR graphs to the specified backend.

    Args:
        graph: A single IR graph **or** a sequence of graphs.
            When multiple graphs are given:
            - *script* mode with ``output_path`` ending in ``.py`` uses
              ``combined_export`` (single file, one ``setup_<name>()`` each).
            - *script* mode with a directory path (or no extension) uses
              ``individual_export`` (one file per graph).
        target: Backend target (``"blender"``, ``"jscad"``, ``"opencascade"``, or ``"openscad"``).
        mode: ``"script"`` to generate source file(s), ``"direct"`` to execute via bpy (blender only).
        output_path: File or directory path for script mode.

    Returns:
        Single graph + no output_path → source string.
        Single graph + output_path → Path written.
        Multiple graphs + combined → Path written.
        Multiple graphs + individual → list[Path] written.
        Direct mode → None.
    """
    if target not in _VALID_TARGETS:
        raise ValueError(
            f"Unsupported target: {target!r}. "
            f"Choose from: {', '.join(sorted(_VALID_TARGETS))}"
        )

    # --- jscad backend ------------------------------------------------------
    if target == "jscad":
        from .jscad.compiler import compile_to_source as jscad_to_source
        from .jscad.compiler import compile_to_script as jscad_to_script

        if isinstance(graph, (list, tuple)):
            graphs_jscad: Sequence[IRGraph] = graph
            if mode != "script":
                raise ValueError("JSCAD backend only supports mode='script'.")
            if output_path is None:
                return "\n".join(jscad_to_source(g) for g in graphs_jscad)
            p = Path(output_path)
            if p.suffix == ".jscad":
                combined = "\n".join(jscad_to_source(g) for g in graphs_jscad)
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(combined)
                return p
            # Individual files
            p.mkdir(parents=True, exist_ok=True)
            paths = []
            for g in graphs_jscad:
                fp = p / f"{g.name}_gen.jscad"
                fp.write_text(jscad_to_source(g))
                paths.append(fp)
            return paths

        # Single graph
        if mode != "script":
            raise ValueError("JSCAD backend only supports mode='script'.")
        if output_path is not None:
            return jscad_to_script(graph, output_path)
        return jscad_to_source(graph)

    # --- openscad backend ---------------------------------------------------
    if target == "openscad":
        from .openscad.compiler import compile_to_source as scad_to_source
        from .openscad.compiler import compile_to_script as scad_to_script

        if isinstance(graph, (list, tuple)):
            graphs_scad: Sequence[IRGraph] = graph
            if mode != "script":
                raise ValueError("OpenSCAD backend only supports mode='script'.")
            if output_path is None:
                return "\n".join(scad_to_source(g) for g in graphs_scad)
            p = Path(output_path)
            if p.suffix == ".scad":
                combined = "\n".join(scad_to_source(g) for g in graphs_scad)
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(combined)
                return p
            # Individual files
            p.mkdir(parents=True, exist_ok=True)
            paths = []
            for g in graphs_scad:
                fp = p / f"{g.name}_gen.scad"
                fp.write_text(scad_to_source(g))
                paths.append(fp)
            return paths

        # Single graph
        if mode != "script":
            raise ValueError("OpenSCAD backend only supports mode='script'.")
        if output_path is not None:
            return scad_to_script(graph, output_path)
        return scad_to_source(graph)

    # --- opencascade backend ------------------------------------------------
    if target == "opencascade":
        from .opencascade.compiler import compile_to_source as oc_to_source
        from .opencascade.compiler import compile_to_script as oc_to_script

        if isinstance(graph, (list, tuple)):
            graphs: Sequence[IRGraph] = graph
            if mode != "script":
                raise ValueError("OpenCascade backend only supports mode='script'.")
            if output_path is None:
                return "\n".join(oc_to_source(g) for g in graphs)
            p = Path(output_path)
            if p.suffix == ".js":
                combined = "\n".join(oc_to_source(g) for g in graphs)
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(combined)
                return p
            # Individual files
            p.mkdir(parents=True, exist_ok=True)
            paths = []
            for g in graphs:
                fp = p / f"{g.name}_gen.js"
                fp.write_text(oc_to_source(g))
                paths.append(fp)
            return paths

        # Single graph
        if mode != "script":
            raise ValueError("OpenCascade backend only supports mode='script'.")
        if output_path is not None:
            return oc_to_script(graph, output_path)
        return oc_to_source(graph)

    # --- blender backend ----------------------------------------------------
    if isinstance(graph, (list, tuple)):
        graphs = graph

        if mode == "direct":
            from .blender.runtime import execute
            for g in graphs:
                execute(g)
            return None

        if mode != "script":
            raise ValueError(f"Unsupported mode: {mode!r}. Use 'script' or 'direct'.")

        from ..dsl.export import combined_export, individual_export

        if output_path is None:
            output_path = "output_gen.py"

        p = Path(output_path)
        if p.suffix == ".py":
            return combined_export(graphs, p)
        return individual_export(graphs, p)

    # --- single graph -------------------------------------------------------
    if mode == "script":
        from .blender.compiler import compile_to_source, compile_to_script

        if output_path is not None:
            return compile_to_script(graph, output_path)
        return compile_to_source(graph)

    if mode == "direct":
        from .blender.runtime import execute  # noqa: F811

        execute(graph)
        return None

    raise ValueError(f"Unsupported mode: {mode!r}. Use 'script' or 'direct'.")
