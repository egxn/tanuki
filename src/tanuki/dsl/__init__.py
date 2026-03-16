"""Tanuki DSL — Declarative API for procedural geometry."""

from .primitives import cube, sphere, cylinder, cone, point, circle, grid, ico_sphere, line
from .operations import union, difference, intersect, join
from .transforms import (
    translate, rotate, scale_by, place,
    transform, set_position,
    pipe,
)
from .instancing import clones
from .instance_ops import (
    realize_instances, rotate_instances, scale_instances, translate_instances,
    geometry_to_instance, instances_to_points, split_to_instances,
)
from .mesh_ops import (
    extrude, subdivide, subdivide_surface, set_shade_smooth, merge_by_distance,
    dual_mesh, mesh_to_curve, mesh_to_points, mesh_to_volume,
    volume_to_mesh, set_mesh_normal, curve_to_mesh,
)
from .curves import curve_arc, curve_circle, curve_line, curve_quadrilateral, curve_star, curve_spiral, bezier_segment, quadratic_bezier
from .curve_ops import (
    fill_curve, fillet_curve, resample_curve, reverse_curve,
    subdivide_curve, trim_curve, curve_to_points,
    deform_curves_on_surface, sample_curve,
    set_curve_normal, set_curve_radius, set_curve_tilt,
    set_handle_positions, set_handle_type,
    set_spline_cyclic, set_spline_resolution, set_spline_type,
    edge_paths_to_curves, interpolate_curves, points_to_curves,
    curves_to_grease_pencil, grease_pencil_to_curves, string_to_curves,
)
from .material_ops import set_material, replace_material, set_material_index
from .volume_ops import distribute_points_in_volume, points_to_volume, volume_cube
from .other_ops import (
    convex_hull, delete_geometry, distribute_points_on_faces,
    duplicate_elements, flip_faces, scale_elements, split_edges, triangulate,
    bounding_box, separate_components, separate_geometry,
    set_id, set_point_radius, sort_elements,
    points_to_vertices, set_geometry_name, set_face_set, set_selection,
    merge_layers, set_grease_pencil_depth, set_grease_pencil_softness,
    switch, get_named_grid, store_named_grid, set_grease_pencil_color, viewer,
    curve_length, domain_size, geometry_proximity, sample_nearest, sample_index, attribute_statistic,
    raycast, sample_nearest_surface, sample_uv_surface, mesh_to_sdf_grid, mesh_to_density_grid,
)
from .attribute_ops import store_named_attribute, remove_named_attribute
from .importers import import_obj, import_stl, import_ply, import_csv, import_vdb, collection_info, object_info
from .field_nodes import (
    position, normal, index, id_field,
    edge_vertices, edge_angle,
    vertex_neighbors, face_neighbors, face_area,
    edge_neighbors, mesh_island, named_attribute,
)
from .math_ops import (
    math_add, math_subtract, math_multiply, math_divide,
    math_power, math_sqrt, math_absolute, math_minimum, math_maximum,
    math_less_than, math_greater_than,
    math_sin, math_cos, math_tan, math_arctan2,
    math_floor, math_ceil, math_round, math_modulo,
    vec_add, vec_subtract, vec_multiply, vec_divide,
    vec_cross, vec_dot, vec_normalize, vec_length, vec_distance, vec_scale,
    vec_project, vec_reflect, vec_faceforward,
    vec_minimum, vec_maximum, vec_floor, vec_ceil, vec_absolute,
    vec_sin, vec_cos, vec_tan,
)
from .export import combined_export, individual_export
from .context import model, output
