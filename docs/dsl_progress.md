# DSL Progress — Geometry Nodes Coverage

**Total: 116 / 223 unique Blender nodes implemented (52.0%)**

## Mesh Nodes (20 / 22)

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
- [ ] Mesh > Face Group Boundaries — info/selection node (out of scope)
- [ ] Mesh > Grid to Mesh — requires VALUE grid input (out of scope)

> Note: Extrude, Subdivide, Subdivision Surface, Dual Mesh, Mesh to Curve/Points/Volume, Volume to Mesh, Set Mesh Normal, Curve to Mesh, Mesh to SDF Grid, and Mesh to Density Grid are all implemented as geometry ops via `IRGeometryOp`. Two niche grid nodes are out of scope for the current geometry pipeline.

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

## Curve Nodes (33 / 45)

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

- [ ] Curve > Curve Handle Positions *(Input category)*
- [x] Curve > Curve Length — `curve_length()`
- [ ] Curve > Curve of Point
- [ ] Curve > Curve Tangent *(Input category)*
- [ ] Curve > Curve Tilt *(Input category)*
- [ ] Curve > Endpoint Selection
- [ ] Curve > Handle Type Selection
- [ ] Curve > Is Spline Cyclic *(Input category)*
- [ ] Curve > Offset Point in Curve
- [ ] Curve > Points of Curve
- [ ] Curve > Spline Length *(Other category)*
- [ ] Curve > Spline Parameter *(Other category)*

> Curve Length is now implemented as `curve_length()`.
- [ ] Curve > Spline Resolution *(Input category)*

## Instances Nodes (8 / 13)

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

- [ ] Instance Transform (read)
- [ ] Instance Bounds
- [ ] Instance Rotation
- [ ] Instance Scale

## Input Nodes (0 / 37)

### Geometry Fields

- [ ] Input > Position
- [ ] Input > Normal
- [ ] Input > Index
- [ ] Input > ID
- [ ] Input > Radius

### Mesh Info

- [ ] Input > Edge Angle
- [ ] Input > Edge Neighbors
- [ ] Input > Edge Vertices
- [ ] Input > Face Area
- [ ] Input > Face Neighbors
- [ ] Input > Is Edge Smooth
- [ ] Input > Is Face Planar
- [ ] Input > Is Face Smooth
- [ ] Input > Mesh Island
- [ ] Input > Vertex Neighbors
- [ ] Input > Shortest Edge Paths

### Curve / Spline Info

- [ ] Input > Curve Handle Positions
- [ ] Input > Curve Tangent
- [ ] Input > Curve Tilt
- [ ] Input > Is Spline Cyclic
- [ ] Input > Spline Resolution

> Also tracked in Curve Nodes > Curve Info / Input

### Instance Info

- [ ] Input > Instance Bounds
- [ ] Input > Instance Rotation
- [ ] Input > Instance Scale

> Also tracked in Instances Nodes > Instance Info / Input

### Material / Named Data

- [ ] Input > Material
- [ ] Input > Material Index
- [ ] Input > Named Attribute
- [ ] Input > Named Layer Selection

### Scene / Object

- [ ] Input > Active Camera
- [ ] Input > Collection
- [ ] Input > Image
- [ ] Input > Object
- [ ] Input > Scene Time

### Control Flow

- [ ] Input > Closure Input
- [ ] Input > For Each Geometry Element Input
- [ ] Input > Repeat Input
- [ ] Input > Simulation Input

## Transform Nodes (1 / 3)

- [x] Transform > Transform Geometry — `translate()`, `rotate()`, `scale_by()`
- [ ] Transform > Transform Gizmo
- [ ] Transform > Viewport Transform

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

## Material Nodes (3 / 4)

- [ ] Material > Material Selection — field node (deferred, requires field IR)
- [x] Material > Replace Material — `replace_material(old, new)`
- [x] Material > Set Material — `set_material(material)`
- [x] Material > Set Material Index — `set_material_index(material_index)`

## Volume Nodes (3 / 3)

- [x] Volume > Distribute Points in Volume — `distribute_points_in_volume(density, seed, spacing, threshold)`
- [x] Volume > Points to Volume — `points_to_volume(density, voxel_size, voxel_amount, radius)`
- [x] Volume > Volume Cube — `volume_cube(density, background, min, max, resolution_x, resolution_y, resolution_z)`

## Texture Nodes (0 / 1)

- [ ] Texture > Image Texture

## Color Nodes (1 / 1)

- [x] Color > Set Grease Pencil Color — `set_grease_pencil_color(color, opacity)` *(also in Other)*

## Other Nodes (50 / 97)

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

### Not Implemented (47 remaining)

Key nodes pending:

- [ ] Other > Set Spline Cyclic *(implemented — see Curve Attributes)*
- [ ] Other > Set Spline Resolution *(implemented — see Curve Attributes)*
- [ ] Other > Spline Length *(also in Curve Info)*
- [ ] Other > Spline Parameter *(also in Curve Info)*
- [ ] ... (43 more — control flow, topology queries, grids, gizmos, etc.)

## Also Implemented (cross-cutting)

- [x] Group Output — `output()` (conceptual, not in Blender registry)
- [x] Pipe operator `|` for composability
- [x] `IRGeometryOp` generic pattern with `extra_children` for multi-input ops
