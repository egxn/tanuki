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
    set_instance_transform,
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
    distribute_points_in_grid, grid_to_mesh, points_to_sdf_grid,
)
from .attribute_ops import store_named_attribute, remove_named_attribute
from .importers import import_obj, import_stl, import_ply, import_csv, import_vdb, collection_info, object_info
from .field_nodes import (
    position, normal, index, id_field,
    edge_vertices, edge_angle,
    vertex_neighbors, face_neighbors, face_area,
    edge_neighbors, mesh_island, named_attribute,
    radius, is_edge_smooth, is_face_planar, is_face_smooth,
    curve_tangent, curve_tilt, is_spline_cyclic, spline_resolution,
    curve_handle_positions, endpoint_selection, handle_type_selection,
    spline_length, spline_parameter,
    curve_of_point, offset_point_in_curve, points_of_curve,
    shortest_edge_paths,
    instance_rotation, instance_scale,
    material_index,
    material_selection, input_material,
    scene_time, active_camera, self_object, is_viewport,
    instance_bounds, named_layer_selection, face_group_boundaries,
    corners_of_edge, corners_of_face, corners_of_vertex,
    edges_of_corner, edges_of_vertex,
    face_of_corner, vertex_of_corner, offset_corner_in_face,
    index_of_nearest, edge_paths_to_selection, edges_to_face_groups,
    instance_transform, viewport_transform,
    tool_selection, tool_face_set, tool_mouse_position, tool_3d_cursor, tool_active_element,
    input_collection, input_image, input_object,
    camera_info, image_texture, image_info,
    field_average, field_min_max, field_variance,
    uv_pack_islands, uv_unwrap,
    join_strings, import_text,
    blur_attribute, accumulate_field, evaluate_at_index, evaluate_on_domain,
    grid_info, sample_grid, sample_grid_index, sdf_grid_boolean,
    warning_node, gizmo_dial, gizmo_linear, gizmo_transform,
)
from .math_ops import (
    math_add, math_subtract, math_multiply, math_divide,
    math_power, math_sqrt, math_absolute, math_minimum, math_maximum,
    math_less_than, math_greater_than,
    math_sin, math_cos, math_tan, math_arcsin, math_arccos, math_arctan, math_arctan2,
    math_floor, math_ceil, math_round, math_modulo,
    vec_add, vec_subtract, vec_multiply, vec_divide,
    vec_cross, vec_dot, vec_normalize, vec_length, vec_distance, vec_scale,
    vec_project, vec_reflect, vec_faceforward,
    vec_minimum, vec_maximum, vec_floor, vec_ceil, vec_absolute,
    vec_sin, vec_cos, vec_tan,
)
from .export import combined_export, individual_export
from .context import model, output
