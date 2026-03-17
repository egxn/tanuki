# DSL Progress — Geometry Nodes Coverage

**Total: 204 / 223 unique Blender nodes implemented (93.2%)**

## Mesh Nodes (22 / 23)

- [x] Mesh > Cube — `cube()`
- [x] Mesh > UV Sphere — `sphere()`
- [x] Mesh > Cylinder — `cylinder()`
- [x] Mesh > Cone — `cone()`
- [x] Mesh > Circle — `circle()`
- [x] Mesh > Grid — `grid()`
- [x] Mesh > Ico Sphere — `ico_sphere()`
- [x] Mesh > Line — `line()`
- [x] Mesh > Boolean — `union()`, `difference()`, `intersect()`
- [x] Mesh > Dual Mesh — `dual_mesh(keep_boundaries)`
- [x] Mesh > Extrude Mesh — `extrude(offset_scale, individual)`
- [x] Mesh > Subdivide Mesh — `subdivide(level)`
- [x] Mesh > Mesh to Curve — `mesh_to_curve()`
- [x] Mesh > Mesh to Points — `mesh_to_points(radius, mode)`
- [x] Mesh > Mesh to Volume — `mesh_to_volume(density, voxel_size, ...)`
- [x] Mesh > Set Mesh Normal — `set_mesh_normal(remove_custom, ...)`
- [x] Mesh > Volume to Mesh — `volume_to_mesh(threshold, adaptivity, ...)`
- [x] Mesh > Curve to Mesh — `curve_to_mesh()`
- [x] Mesh > Mesh to SDF Grid — `mesh_to_sdf_grid(voxel_size, band_width)`
- [x] Mesh > Mesh to Density Grid — `mesh_to_density_grid(density, voxel_size, gradient_width)`
- [x] Mesh > Face Group Boundaries — `face_group_boundaries(face_group_id)`
- [x] Mesh > Grid to Mesh — `grid_to_mesh(threshold, adaptivity)`

> Note: Extrude, Subdivide, Subdivision Surface, Dual Mesh, Mesh to Curve/Points/Volume, Volume to Mesh, Set Mesh Normal, Curve to Mesh, Mesh to SDF Grid, Mesh to Density Grid, and Grid to Mesh are all implemented as geometry ops via `IRGeometryOp`.

## Geometry Ops (80 total)

- [x] Extrude Mesh — `extrude(offset_scale, individual)`
- [x] Subdivide Mesh — `subdivide(level)`
- [x] Subdivision Surface — `subdivide_surface(level)`
- [x] Set Shade Smooth — `set_shade_smooth(shade_smooth)`
- [x] Merge by Distance — `merge_by_distance(distance)`
- [x] Dual Mesh — `dual_mesh(keep_boundaries)`
- [x] Mesh to Curve — `mesh_to_curve()`
- [x] Mesh to Points — `mesh_to_points(radius, mode)`
- [x] Mesh to Volume — `mesh_to_volume(density, voxel_size, ...)`
- [x] Volume to Mesh — `volume_to_mesh(threshold, adaptivity, ...)`
- [x] Set Mesh Normal — `set_mesh_normal(remove_custom, ...)`
- [x] Curve to Mesh — `curve_to_mesh(profile, scale, fill_caps)`
- [x] Fill Curve — `fill_curve(group_id)`
- [x] Fillet Curve — `fillet_curve(count, radius, limit_radius)`
- [x] Resample Curve — `resample_curve(count)`
- [x] Reverse Curve — `reverse_curve()`
- [x] Subdivide Curve — `subdivide_curve(cuts)`
- [x] Trim Curve — `trim_curve(start, end)`
- [x] Curve to Points — `curve_to_points(count)`
- [x] Deform Curves on Surface — `deform_curves_on_surface()`
- [x] Sample Curve — `sample_curve(factor, curve_index)`
- [x] Set Curve Normal — `set_curve_normal(normal)`
- [x] Set Curve Radius — `set_curve_radius(radius)`
- [x] Set Curve Tilt — `set_curve_tilt(tilt)`
- [x] Set Handle Positions — `set_handle_positions(position, offset)`
- [x] Set Handle Type — `set_handle_type(handle_type)`
- [x] Set Spline Cyclic — `set_spline_cyclic(cyclic)`
- [x] Set Spline Resolution — `set_spline_resolution(resolution)`
- [x] Set Spline Type — `set_spline_type(spline_type)`
- [x] Convex Hull — `convex_hull()`
- [x] Delete Geometry — `delete_geometry(mode, domain)`
- [x] Distribute Points on Faces — `distribute_points_on_faces(density, seed, ...)`
- [x] Duplicate Elements — `duplicate_elements(amount, domain)`
- [x] Flip Faces — `flip_faces()`
- [x] Scale Elements — `scale_elements(scale, center, axis, domain, scale_mode)`
- [x] Split Edges — `split_edges()`
- [x] Triangulate — `triangulate(quad_method, ngon_method)`
- [x] Bounding Box — `bounding_box(use_radius)`
- [x] Separate Components — `separate_components(component)`
- [x] Separate Geometry — `separate_geometry()`
- [x] Set ID — `set_id(id_value)`
- [x] Set Point Radius — `set_point_radius(radius)`
- [x] Sort Elements — `sort_elements(sort_weight, group_id, domain)`
- [x] Store Named Attribute — `store_named_attribute(name, value, data_type, domain)`
- [x] Remove Named Attribute — `remove_named_attribute(name)`
- [x] Points to Vertices — `points_to_vertices()`
- [x] Set Geometry Name — `set_geometry_name(name)`
- [x] Set Face Set — `set_face_set(face_set)`
- [x] Set Selection — `set_selection(domain, selection_type)`
- [x] Merge Layers — `merge_layers(mode, group_id)`
- [x] Set Grease Pencil Depth — `set_grease_pencil_depth(depth_order)`
- [x] Set Grease Pencil Softness — `set_grease_pencil_softness(softness)`
- [x] Switch — `switch(switch_value, true_child)`
- [x] Get Named Grid — `get_named_grid(name, remove, data_type)`
- [x] Store Named Grid — `store_named_grid(name, grid_value, data_type)`
- [x] Set Grease Pencil Color — `set_grease_pencil_color(color, opacity)`
- [x] Viewer — `viewer(value, data_type, domain)` *(pass-through terminal)*
- [x] Curve Length — `curve_length()`
- [x] Domain Size — `domain_size()`
- [x] Geometry Proximity — `geometry_proximity(target_element, sample_position, ...)`
- [x] Sample Nearest — `sample_nearest(domain, sample_position)`
- [x] Sample Index — `sample_index(value, index, data_type, domain, clamp)`
- [x] Attribute Statistic — `attribute_statistic(attribute, data_type, domain)`
- [x] Raycast — `raycast(attribute, source_position, ray_direction, ray_length, data_type)`
- [x] Sample Nearest Surface — `sample_nearest_surface(value, sample_position, data_type, ...)`
- [x] Sample UV Surface — `sample_uv_surface(value, uv_map, sample_uv, data_type)`
- [x] Mesh to SDF Grid — `mesh_to_sdf_grid(voxel_size, band_width)`
- [x] Mesh to Density Grid — `mesh_to_density_grid(density, voxel_size, gradient_width)`

## Curve Nodes (45 / 45)

> 35 nodes from the Blender Curve category + 10 curve-related nodes from other categories (1 Mesh, 5 Input, 4 Other).

### Curve Primitives

- [x] Curve Primitives > Arc — `curve_arc()`
- [x] Curve Primitives > Circle — `curve_circle()`
- [x] Curve Primitives > Line — `curve_line()`
- [x] Curve Primitives > Quadrilateral — `curve_quadrilateral()`
- [x] Curve Primitives > Star — `curve_star()`
- [x] Curve Primitives > Spiral — `curve_spiral()`
- [x] Curve Primitives > Bezier Segment — `bezier_segment(resolution, start, start_handle, end_handle, end)`
- [x] Curve Primitives > Quadratic Bezier — `quadratic_bezier(resolution, start, middle, end)`

### Curve Operations

- [x] Curve > Curve to Mesh — `curve_to_mesh(profile, scale, fill_caps)` *(Mesh category)*
- [x] Curve > Curve to Points — `curve_to_points(count)`
- [x] Curve > Deform Curves on Surface — `deform_curves_on_surface()`
- [x] Curve > Edge Paths to Curves — `edge_paths_to_curves(start_vertices, next_vertex_index)`
- [x] Curve > Fill Curve — `fill_curve(group_id)`
- [x] Curve > Fillet Curve — `fillet_curve(count, radius, limit_radius)`
- [x] Curve > Interpolate Curves — `interpolate_curves(guide_up, guide_group_id, points, ...)`
- [x] Curve > Points to Curves — `points_to_curves(curve_group_id, weight)`
- [x] Curve > Resample Curve — `resample_curve(count)`
- [x] Curve > Reverse Curve — `reverse_curve()`
- [x] Curve > Sample Curve — `sample_curve(factor, curve_index)`
- [x] Curve > Subdivide Curve — `subdivide_curve(cuts)`
- [x] Curve > Trim Curve — `trim_curve(start, end)`
- [x] Curve > Curves to Grease Pencil — `curves_to_grease_pencil(instances_as_layers)`
- [x] Curve > Grease Pencil to Curves — `grease_pencil_to_curves(layers_as_instances)`
- [x] Curve > String to Curves — `string_to_curves(string, size, character_spacing, ...)`

### Curve Attributes (Set)

- [x] Curve > Set Curve Normal — `set_curve_normal(normal)`
- [x] Curve > Set Curve Radius — `set_curve_radius(radius)`
- [x] Curve > Set Curve Tilt — `set_curve_tilt(tilt)`
- [x] Curve > Set Handle Positions — `set_handle_positions(position, offset)`
- [x] Curve > Set Handle Type — `set_handle_type(handle_type)`
- [x] Curve > Set Spline Cyclic — `set_spline_cyclic(cyclic)` *(Other category)*
- [x] Curve > Set Spline Resolution — `set_spline_resolution(resolution)` *(Other category)*
- [x] Curve > Set Spline Type — `set_spline_type(spline_type)`

### Curve Info / Input

- [x] Curve > Curve Handle Positions — `curve_handle_positions(relative, output)` *(Input category)*
- [x] Curve > Curve Length — `curve_length()`
- [x] Curve > Curve of Point — `curve_of_point(point_index, output)`
- [x] Curve > Curve Tangent — `curve_tangent()` *(Input category)*
- [x] Curve > Curve Tilt — `curve_tilt()` *(Input category)*
- [x] Curve > Endpoint Selection — `endpoint_selection(start_size, end_size)`
- [x] Curve > Handle Type Selection — `handle_type_selection(handle_type, mode)`
- [x] Curve > Is Spline Cyclic — `is_spline_cyclic()` *(Input category)*
- [x] Curve > Offset Point in Curve — `offset_point_in_curve(point_index, offset, output)`
- [x] Curve > Points of Curve — `points_of_curve(curve_index, weights, sort_index, output)`
- [x] Curve > Spline Length — `spline_length(output)` *(Other category)*
- [x] Curve > Spline Parameter — `spline_parameter(output)` *(Other category)*
- [x] Curve > Spline Resolution — `spline_resolution()` *(Input category)*

## Instances Nodes (12 / 13)

### Instance Operations

- [x] Instance on Points — `clones()`
- [x] Realize Instances — `realize_instances()`
- [x] Rotate Instances — `rotate_instances()`
- [x] Scale Instances — `scale_instances()`
- [x] Translate Instances — `translate_instances()`
- [x] Geometry to Instance — `geometry_to_instance()`
- [x] Instances to Points — `instances_to_points(position, radius)`
- [ ] Set Instance Transform — requires MATRIX input (deferred)
- [x] Split to Instances — `split_to_instances(group_id)`

### Instance Info / Input

- [x] Instance Transform (read) — `instance_transform()`
- [x] Instance Bounds — `instance_bounds(use_radius, output)`
- [x] Instance Rotation — `instance_rotation()`
- [x] Instance Scale — `instance_scale()`

## Input Nodes (37 / 37)

### Geometry Fields

- [x] Input > Position — `position()`
- [x] Input > Normal — `normal()`
- [x] Input > Index — `index()`
- [x] Input > ID — `id_field()`
- [x] Input > Radius — `radius()`

### Mesh Info

- [x] Input > Edge Angle — `edge_angle(unsigned)`
- [x] Input > Edge Neighbors — `edge_neighbors()`
- [x] Input > Edge Vertices — `edge_vertices(output)`
- [x] Input > Face Area — `face_area()`
- [x] Input > Face Neighbors — `face_neighbors(output)`
- [x] Input > Is Edge Smooth — `is_edge_smooth()`
- [x] Input > Is Face Planar — `is_face_planar(threshold)`
- [x] Input > Is Face Smooth — `is_face_smooth()`
- [x] Input > Mesh Island — `mesh_island(output)`
- [x] Input > Vertex Neighbors — `vertex_neighbors(output)`
- [x] Input > Shortest Edge Paths — `shortest_edge_paths(end_vertex, edge_cost, output)`

### Curve / Spline Info

- [x] Input > Curve Handle Positions — `curve_handle_positions(relative, output)`
- [x] Input > Curve Tangent — `curve_tangent()`
- [x] Input > Curve Tilt — `curve_tilt()`
- [x] Input > Is Spline Cyclic — `is_spline_cyclic()`
- [x] Input > Spline Resolution — `spline_resolution()`

> Also tracked in Curve Nodes > Curve Info / Input

### Instance Info

- [x] Input > Instance Bounds — `instance_bounds(use_radius, output)`
- [x] Input > Instance Rotation — `instance_rotation()`
- [x] Input > Instance Scale — `instance_scale()`

> Also tracked in Instances Nodes > Instance Info / Input

### Material / Named Data

- [x] Input > Material — `input_material(material)`
- [x] Input > Material Index — `material_index()`
- [x] Input > Named Attribute — `named_attribute(name, data_type)`
- [x] Input > Named Layer Selection — `named_layer_selection(name)`

### Scene / Object

- [x] Input > Active Camera — `active_camera()`
- [x] Input > Collection — `input_collection(collection)`
- [x] Input > Image — `input_image(image)`
- [x] Input > Object — `input_object(object_name)`
- [x] Input > Scene Time — `scene_time(output)`

### Control Flow

- [ ] Input > Closure Input
- [ ] Input > For Each Geometry Element Input
- [ ] Input > Repeat Input
- [ ] Input > Simulation Input

> Note: All field input nodes use the new `IRFieldInput` IR type. They produce per-element values (scalar, vector, integer) evaluated in context — they have no geometry input socket.

## Math Nodes (11 / 11)

Math nodes use the `IRMathOp` IR type. They are exposed as pure functions in `tanuki.dsl.math_ops`.

### Scalar Math (`ShaderNodeMath`)

- [x] Add — `math_add(a, b)`
- [x] Subtract — `math_subtract(a, b)`
- [x] Multiply — `math_multiply(a, b)`
- [x] Divide — `math_divide(a, b)`
- [x] Power — `math_power(base, exponent)`
- [x] Sqrt — `math_sqrt(a)`
- [x] Absolute — `math_absolute(a)`
- [x] Minimum — `math_minimum(a, b)`
- [x] Maximum — `math_maximum(a, b)`
- [x] Less Than — `math_less_than(a, b)`
- [x] Greater Than — `math_greater_than(a, b)`
- [x] Sine — `math_sin(a)`
- [x] Cosine — `math_cos(a)`
- [x] Tangent — `math_tan(a)`
- [x] Arctan2 — `math_arctan2(a, b)`
- [x] Floor — `math_floor(a)`
- [x] Ceil — `math_ceil(a)`
- [x] Round — `math_round(a)`
- [x] Modulo — `math_modulo(a, b)`

### Vector Math (`ShaderNodeVectorMath`)

- [x] Add — `vec_add(a, b)`
- [x] Subtract — `vec_subtract(a, b)`
- [x] Multiply — `vec_multiply(a, b)`
- [x] Divide — `vec_divide(a, b)`
- [x] Cross Product — `vec_cross(a, b)`
- [x] Dot Product — `vec_dot(a, b)` *(scalar output)*
- [x] Normalize — `vec_normalize(a)`
- [x] Length — `vec_length(a)` *(scalar output)*
- [x] Distance — `vec_distance(a, b)` *(scalar output)*
- [x] Scale — `vec_scale(vector, scale)`
- [x] Project — `vec_project(a, b)`
- [x] Reflect — `vec_reflect(a, b)`
- [x] Faceforward — `vec_faceforward(a, b, c)`
- [x] Minimum — `vec_minimum(a, b)`
- [x] Maximum — `vec_maximum(a, b)`
- [x] Floor — `vec_floor(a)`
- [x] Ceil — `vec_ceil(a)`
- [x] Absolute — `vec_absolute(a)`
- [x] Sine — `vec_sin(a)`
- [x] Cosine — `vec_cos(a)`
- [x] Tangent — `vec_tan(a)`

> Note: Both Math and VectorMath are Blender utility nodes (not in the Geometry Nodes registry but used extensively within node trees). All operations from both nodes are fully implemented.

## Custom Composite Nodes

**Module:** `tanuki.dsl.custom`

Custom nodes are high-level operations composed from DSL primitives. They live in `src/tanuki/dsl/custom/` and build on the existing field, math, and geometry op modules to create reusable analysis and visualization tools.

### Mesh Analysis (`tanuki.dsl.custom.mesh_analysis`)

Given a mesh geometry, generates three visualization groups:

| Function | Output | Description |
|---|---|---|
| `edges_group()` | Curves | All mesh edges converted to curves via `MeshToCurve` |
| `faces_group()` | Mesh | The mesh geometry as-is (semantic pass-through — the mesh *is* the face data) |
| `angles_group(arm_length)` | Points + Attributes | Per-edge points with direction vectors and dihedral angle stored as named attributes |
| `mesh_analysis(mesh, arm_length)` | Joined geometry | Combines all three into a single `join()` |

The `angles_group` implements the following Geometry Nodes graph:

1. **Edge Vertices** → positions `P1`, `P2` of each edge
2. **VectorMath(Subtract)** → direction `P2 - P1` and `P1 - P2`
3. **VectorMath(Normalize)** → unit direction vectors
4. **VectorMath(Scale)** → arms of length `arm_length`
5. **Mesh to Points (EDGES)** → one point per edge
6. **Store Named Attribute** × 3 → `_arm_dir_1`, `_arm_dir_2` (vectors), `_edge_angle` (float)

Usage:

```python
from tanuki import *
from tanuki.dsl.custom import mesh_analysis

with model("analysis") as ctx:
    base = cube(2, 2, 2, "box")
    result = mesh_analysis(base, arm_length=0.3)
    output(result)

combined_export([ctx.graph], "mesh_analysis_output.py")
```

To create your own custom nodes, add a new `.py` module to `src/tanuki/dsl/custom/` and re-export from `custom/__init__.py`. Custom nodes follow the same `Op = Callable[[IRNode], IRNode]` pattern and compose with `|`.

## Transform Nodes (2 / 3)

- [x] Transform > Transform Geometry — `translate()`, `rotate()`, `scale_by()`
- [ ] Transform > Transform Gizmo
- [x] Transform > Viewport Transform — `viewport_transform(output)`

> Note: Set Position (`place()` / `set_position()`) is in the Other category, not Transform.

## Output Nodes (0 / 4)

- [ ] Output > Closure Output
- [ ] Output > For Each Geometry Element Output
- [ ] Output > Repeat Output
- [ ] Output > Simulation Output

> Note: `output()` in the DSL maps to the conceptual Group Output (implicit in Blender, not in the node registry). The four Output nodes above are control-flow nodes for loops/simulations.

## Attribute Nodes (4 / 6)

- [x] Attribute > Domain Size — `domain_size()`
- [x] Attribute > Attribute Statistic — `attribute_statistic(attribute, data_type, domain)`
- [ ] Attribute > Blur Attribute — field processor, no geometry I/O (deferred, needs field IR)
- [ ] Attribute > Capture Attribute — dynamic extension sockets (deferred, needs dynamic socket IR)
- [x] Attribute > Remove Named Attribute — `remove_named_attribute(name)`
- [x] Attribute > Store Named Attribute — `store_named_attribute(name, value, data_type, domain)`

## Material Nodes (4 / 4)

- [x] Material > Material Selection — `material_selection(material)`
- [x] Material > Replace Material — `replace_material(old, new)`
- [x] Material > Set Material — `set_material(material)`
- [x] Material > Set Material Index — `set_material_index(material_index)`

## Volume Nodes (3 / 3)

- [x] Volume > Distribute Points in Volume — `distribute_points_in_volume(density, seed, spacing, threshold)`
- [x] Volume > Points to Volume — `points_to_volume(density, voxel_size, voxel_amount, radius)`
- [x] Volume > Volume Cube — `volume_cube(density, background, min, max, resolution_x, resolution_y, resolution_z)`

## Texture Nodes (1 / 1)

- [x] Texture > Image Texture — `image_texture(image, interpolation, extension, output)`

## Color Nodes (1 / 1)

- [x] Color > Set Grease Pencil Color — `set_grease_pencil_color(color, opacity)` *(also in Other)*

## Other Nodes (72 / 97)

### Implemented

- [x] Other > Points — `point()`
- [x] Other > Join Geometry — `join()`
- [x] Other > Set Position — `place()` / `set_position()`
- [x] Other > Set Shade Smooth — `set_shade_smooth()`
- [x] Other > Merge by Distance — `merge_by_distance()`
- [x] Other > Subdivision Surface — `subdivide_surface(level)`
- [x] Other > Set Spline Cyclic — `set_spline_cyclic(cyclic)` *(also in Curve Attributes)*
- [x] Other > Set Spline Resolution — `set_spline_resolution(resolution)` *(also in Curve Attributes)*
- [x] Other > Convex Hull — `convex_hull()`
- [x] Other > Delete Geometry — `delete_geometry(mode, domain)`
- [x] Other > Distribute Points on Faces — `distribute_points_on_faces(density, seed, ...)`
- [x] Other > Duplicate Elements — `duplicate_elements(amount, domain)`
- [x] Other > Flip Faces — `flip_faces()`
- [x] Other > Scale Elements — `scale_elements(scale, center, axis, domain, scale_mode)`
- [x] Other > Split Edges — `split_edges()`
- [x] Other > Triangulate — `triangulate(quad_method, ngon_method)`
- [x] Other > Bounding Box — `bounding_box(use_radius)`
- [x] Other > Separate Components — `separate_components(component)`
- [x] Other > Separate Geometry — `separate_geometry()`
- [x] Other > Set ID — `set_id(id_value)`
- [x] Other > Set Point Radius — `set_point_radius(radius)`
- [x] Other > Sort Elements — `sort_elements(sort_weight, group_id, domain)`
- [x] Other > Points to Vertices — `points_to_vertices()`
- [x] Other > Set Geometry Name — `set_geometry_name(name)`
- [x] Other > Set Face Set — `set_face_set(face_set)`
- [x] Other > Set Selection — `set_selection(domain, selection_type)`
- [x] Other > Merge Layers — `merge_layers(mode, group_id)`
- [x] Other > Set Grease Pencil Depth — `set_grease_pencil_depth(depth_order)`
- [x] Other > Set Grease Pencil Softness — `set_grease_pencil_softness(softness)`
- [x] Other > Switch — `switch(switch_value, true_child)`
- [x] Other > Get Named Grid — `get_named_grid(name, remove, data_type)`
- [x] Other > Store Named Grid — `store_named_grid(name, grid_value, data_type)`
- [x] Other > Set Grease Pencil Color — `set_grease_pencil_color(color, opacity)` *(Color category)*
- [x] Other > Viewer — `viewer(value, data_type, domain)` *(pass-through terminal)*
- [x] Other > Import OBJ — `import_obj(path)`
- [x] Other > Import STL — `import_stl(path)`
- [x] Other > Import PLY — `import_ply(path)`
- [x] Other > Import CSV — `import_csv(path, delimiter)`
- [x] Other > Import VDB — `import_vdb(path)`
- [x] Other > Collection Info — `collection_info(collection, separate_children, reset_children, transform_space)`
- [x] Other > Object Info — `object_info(object, as_instance, transform_space)`
- [x] Other > Geometry Proximity — `geometry_proximity(target_element, sample_position, ...)`
- [x] Other > Raycast — `raycast(attribute, source_position, ray_direction, ray_length, data_type)`
- [x] Other > Sample Index — `sample_index(value, index, data_type, domain, clamp)`
- [x] Other > Sample Nearest — `sample_nearest(domain, sample_position)`
- [x] Other > Sample Nearest Surface — `sample_nearest_surface(value, sample_position, data_type, ...)`
- [x] Other > Sample UV Surface — `sample_uv_surface(value, uv_map, sample_uv, data_type)`
- [x] Other > Domain Size — `domain_size()` *(also in Attribute)*
- [x] Other > Attribute Statistic — `attribute_statistic(attribute, data_type, domain)` *(also in Attribute)*

### Topology Queries

- [x] Other > Corners of Edge — `corners_of_edge(edge_index, weights, sort_index, output)`
- [x] Other > Corners of Face — `corners_of_face(face_index, weights, sort_index, output)`
- [x] Other > Corners of Vertex — `corners_of_vertex(vertex_index, weights, sort_index, output)`
- [x] Other > Edges of Corner — `edges_of_corner(corner_index, output)`
- [x] Other > Edges of Vertex — `edges_of_vertex(vertex_index, weights, sort_index, output)`
- [x] Other > Face of Corner — `face_of_corner(corner_index, output)`
- [x] Other > Vertex of Corner — `vertex_of_corner(corner_index)`
- [x] Other > Offset Corner in Face — `offset_corner_in_face(corner_index, offset)`

### Selection / Grouping Fields

- [x] Other > Edge Paths to Selection — `edge_paths_to_selection(start_vertices, next_vertex_index)`
- [x] Other > Edges to Face Groups — `edges_to_face_groups(boundary_edges)`
- [x] Other > Index of Nearest — `index_of_nearest(output)`
- [x] Other > Self Object — `self_object()`
- [x] Other > Is Viewport — `is_viewport()`

### Information / Statistics

- [x] Other > Camera Info — `camera_info(camera, output)`
- [x] Other > Image Info — `image_info(image, frame, output)`
- [x] Other > Field Average — `field_average(group_id, data_type, domain, output)`
- [x] Other > Field Min & Max — `field_min_max(group_id, data_type, domain, output)`
- [x] Other > Field Variance — `field_variance(group_id, data_type, domain, output)`

### UV Operations

- [x] Other > Pack UV Islands — `uv_pack_islands(margin, rotate)`
- [x] Other > UV Unwrap — `uv_unwrap(margin, fill_holes, method)`

### Tool Nodes

- [x] Other > Selection (Tool) — `tool_selection(output)`
- [x] Other > Face Set (Tool) — `tool_face_set(output)`
- [x] Other > Mouse Position — `tool_mouse_position(output)`
- [x] Other > 3D Cursor — `tool_3d_cursor(output)`
- [x] Other > Active Element — `tool_active_element(domain, output)`

### String / Utility

- [x] Other > Join Strings — `join_strings(delimiter)`
- [x] Other > Import Text — `import_text(path)`

### Batch 20 — Field Processors, Grid, Gizmos, Warning

- [x] Attribute > Blur Attribute — `blur_attribute(value, iterations, weight, data_type)`
- [x] Other > Accumulate Field — `accumulate_field(value, group_id, data_type, domain, output)`
- [x] Other > Evaluate at Index — `evaluate_at_index(value, index, domain, data_type)`
- [x] Other > Evaluate on Domain — `evaluate_on_domain(value, domain, data_type)`
- [x] Other > Grid Info — `grid_info(data_type, output)`
- [x] Other > Sample Grid — `sample_grid(data_type, interpolation_mode)`
- [x] Other > Sample Grid Index — `sample_grid_index(x, y, z, data_type)`
- [x] Other > SDF Grid Boolean — `sdf_grid_boolean(operation)`
- [x] Other > Warning — `warning_node(show, message, warning_type)`
- [x] Other > Dial Gizmo — `gizmo_dial(value, position, up, screen_space, radius, color_id)`
- [x] Other > Linear Gizmo — `gizmo_linear(value, position, direction, color_id, draw_style)`
- [x] Transform > Transform Gizmo — `gizmo_transform(position, rotation, use_translation_x, ...)`
- [x] Other > Distribute Points in Grid — `distribute_points_in_grid(density, seed, spacing, threshold, mode)`
- [x] Other > Points to SDF Grid — `points_to_sdf_grid(radius, voxel_size)`
- [x] Instances > Set Instance Transform — `set_instance_transform()`
- [x] Mesh > Grid to Mesh — `grid_to_mesh(threshold, adaptivity)`

### Not Implemented (15 remaining — control flow / dynamic sockets)

These nodes require new IR patterns (zone pairs, dynamic sockets, bundles):

- [ ] Closure Input / Output — zone pair, dynamic sockets
- [ ] Repeat Input / Output — zone pair, dynamic sockets
- [ ] Simulation Input / Output — zone pair, dynamic sockets
- [ ] For Each Geometry Element Input / Output — zone pair
- [ ] Bake — dynamic sockets
- [ ] Capture Attribute — dynamic output sockets
- [ ] Evaluate Closure — CLOSURE socket type
- [ ] Combine Bundle / Separate Bundle — BUNDLE socket type
- [ ] Index Switch / Menu Switch — dynamic indexed inputs

## Also Implemented (cross-cutting)

- [x] Group Output — `output()` (conceptual, not in Blender registry)
- [x] Pipe operator `|` for composability
- [x] `IRGeometryOp` generic pattern with `extra_children` for multi-input ops
- [x] `IRFieldInput` for per-element field nodes (Position, Normal, Edge Angle, etc.)
- [x] `IRFieldInput.input_defaults` for field nodes with input socket defaults (Is Face Planar, Endpoint Selection, etc.)
- [x] `("MATERIAL", name)` tuple convention for material references in field input properties and input_defaults
- [x] `IRMathOp` for scalar (`ShaderNodeMath`) and vector (`ShaderNodeVectorMath`) math operations
- [x] `dsl/custom/` framework for composing high-level nodes from DSL primitives
