"""File importer constructors — OBJ, STL, PLY, CSV, VDB — and reference sources."""

from __future__ import annotations

from ..ir.nodes import IRPrimitive, PrimitiveType


def import_obj(path: str = "") -> IRPrimitive:
    """Import geometry from an OBJ file."""
    return IRPrimitive(
        primitive_type=PrimitiveType.IMPORT_OBJ,
        properties={"path": path},
        label="import_obj",
    )


def import_stl(path: str = "") -> IRPrimitive:
    """Import geometry from an STL file."""
    return IRPrimitive(
        primitive_type=PrimitiveType.IMPORT_STL,
        properties={"path": path},
        label="import_stl",
    )


def import_ply(path: str = "") -> IRPrimitive:
    """Import geometry from a PLY file."""
    return IRPrimitive(
        primitive_type=PrimitiveType.IMPORT_PLY,
        properties={"path": path},
        label="import_ply",
    )


def import_csv(path: str = "", delimiter: str = ",") -> IRPrimitive:
    """Import point cloud from a CSV file."""
    return IRPrimitive(
        primitive_type=PrimitiveType.IMPORT_CSV,
        properties={"path": path, "delimiter": delimiter},
        label="import_csv",
    )


def import_vdb(path: str = "") -> IRPrimitive:
    """Import volume from a VDB file."""
    return IRPrimitive(
        primitive_type=PrimitiveType.IMPORT_VDB,
        properties={"path": path},
        label="import_vdb",
    )


def collection_info(
    collection: str = "",
    separate_children: bool = False,
    reset_children: bool = False,
    transform_space: str = "ORIGINAL",
) -> IRPrimitive:
    """Retrieve geometry from a collection as instances."""
    return IRPrimitive(
        primitive_type=PrimitiveType.COLLECTION_INFO,
        properties={
            "collection": collection,
            "separate_children": separate_children,
            "reset_children": reset_children,
            "transform_space": transform_space,
        },
        label="collection_info",
    )


def object_info(
    object: str = "",
    as_instance: bool = False,
    transform_space: str = "ORIGINAL",
) -> IRPrimitive:
    """Retrieve geometry from an object."""
    return IRPrimitive(
        primitive_type=PrimitiveType.OBJECT_INFO,
        properties={
            "object": object,
            "as_instance": as_instance,
            "transform_space": transform_space,
        },
        label="object_info",
    )
