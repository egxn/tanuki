import bpy
from typing import List, Optional, Tuple

node_height = 200
node_width = 180

class NodeGrid:
    def __init__(self):
        self.partial_x = 0
        self.partial_y = 0
        self.global_x = 0
        self.global_y = 0


class Settings:
    def __init__(self):
        self.object_name = ""

    def set_object_name(self, object_name: str) -> None:
        print("object_name :", object_name)
        self.object_name = object_name

    def get_object_name(self) -> str:
        return self.object_name


grid = NodeGrid()
settings = Settings()


def get_location(type: str = "start", grid: NodeGrid = grid) -> Tuple[int, int]:
    if type == "start":
        grid.global_x = (
            grid.partial_x if grid.partial_x >= grid.global_x else grid.global_x
        )
        grid.partial_x = 0
        grid.partial_y = grid.global_y + 1
        grid.global_y = grid.partial_y + 1
    elif type == "middle":
        grid.partial_x = grid.partial_x + 1

    return (grid.partial_x * node_width, grid.partial_y * node_height)


def get_global_location(grid: NodeGrid = grid) -> Tuple[int, int]:
    node_location = (grid.global_x * node_width, (grid.global_y + 1.5) * node_height)

    return node_location


def debug_object(obj):
    print(f"Debugging object: {obj}")
    print("Attributes and methods:")
    for attr in dir(obj):
        try:
            value = getattr(obj, attr)
            print(f"{attr}: {value}")
        except AttributeError:
            print(f"{attr}: <AttributeError>")


def delete_mesh_by_name(name: str) -> None:
    if name in bpy.data.objects:
        obj = bpy.data.objects[name]
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode="OBJECT")
        bpy.ops.object.select_all(action="DESELECT")
        obj.select_set(True)
        bpy.ops.object.delete()


def start(object_name: str) -> bpy.types.NodeTree:
    settings.set_object_name(object_name)
    delete_mesh_by_name(object_name)
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 0))
    bpy.context.active_object.name = object_name
    plane = bpy.context.active_object
    geom_nodes_modifier = plane.modifiers.new(name="GeometryNodes", type="NODES")
    bpy.ops.node.new_geometry_node_group_assign()
    node_tree = geom_nodes_modifier.node_group

    nodes_to_delete = [node for node in node_tree.nodes]

    for node in nodes_to_delete:
        node_tree.nodes.remove(node)

    return node_tree


def get_node_tree() -> bpy.types.NodeTree:
    object_name = settings.get_object_name()
    for obj in bpy.context.scene.objects:
        if obj.type == "MESH" and obj.name == object_name:
            for modifier in obj.modifiers:
                if modifier.type == "NODES":
                    return modifier.node_group


def get_input_nodes_for_socket(
    node: bpy.types.Node, socket_name: str
) -> List[bpy.types.Node]:
    input_nodes = []
    for input_socket in node.inputs:
        if input_socket.name == socket_name and input_socket.is_linked:
            for link in input_socket.links:
                input_nodes.append(link.from_node)
    return input_nodes


def mesh(
    type: str, label: Optional[str] = None, node_location: Tuple[float, float] = (0, 0)
) -> bpy.types.Node:
    node_tree = get_node_tree()
    mesh = node_tree.nodes.new(type)
    mesh.location = node_location

    if label is not None:
        mesh.label = label

    return mesh


def output(node: Optional[bpy.types.Node]) -> bpy.types.Node:
    node_location = get_global_location()
    output_node = mesh(
        type="NodeGroupOutput", label="output", node_location=node_location
    )

    if node is not None:
        link_by_socket_index(node, output_node, 0, 0)

    return output_node


def value(
    label: Optional[str] = None,
    node_location: Tuple[float, float] = (0, 0),
    value: float = 0,
) -> bpy.types.Node:
    v = mesh(label=label, node_location=node_location, type="ShaderNodeValue")
    v.outputs[0].default_value = value
    return v


def vector(
    label: Optional[str] = None,
    node_location: Tuple[float, float] = (0, 0),
    value: Tuple[float, float, float] = (0, 0, 0),
) -> bpy.types.Node:
    vector = mesh(
        label=label, node_location=node_location, type="FunctionNodeInputVector"
    )
    vector.vector = value
    return vector


def join(nodes: Optional[List[bpy.types.Node]]) -> bpy.types.Node:
    created_join = mesh(
        label="join",
        node_location=get_global_location(),
        type="GeometryNodeJoinGeometry",
    )

    if nodes is not None:
        for node in nodes:
            output_sockets = [socket.name for socket in node.outputs]
            if "Geometry" in output_sockets:
                link(node, "Geometry", created_join, "Geometry")
            elif "Points" in output_sockets:
                link(node, "Points", created_join, "Geometry")
            elif "Mesh" in output_sockets:
                link(node, "Mesh", created_join, "Geometry")

    return created_join


def bool_operation(operation: str) -> bpy.types.Node:
    node_location = get_global_location()
    node = mesh(node_location=node_location, type="GeometryNodeMeshBoolean")
    node.operation = operation
    node.solver = "EXACT"
    return node


def difference(
    first: Optional[bpy.types.Node], rest: Optional[List[bpy.types.Node]]
) -> bpy.types.Node:
    difference = bool_operation("DIFFERENCE")

    if first is not None:
        link_by_socket_index(first, difference, 0, 0)

    if rest is not None:
        for node in rest:
            link_by_socket_index(node, difference, 0, 1)

    return difference


def union(nodes: Optional[List[bpy.types.Node]]) -> bpy.types.Node:
    union = bool_operation("UNION")

    if nodes is not None:
        for node in nodes:
            link_by_socket_index(node, union, 0, 1)

    return union


def intersect(nodes: Optional[List[bpy.types.Node]]) -> bpy.types.Node:
    intersect = bool_operation("INTERSECT")

    if nodes is not None:
        for node in nodes:
            link_by_socket_index(node, intersect, 0, 1)

    return intersect


def link(
    output_node: bpy.types.Node,
    output_socket_name: str,
    input_node: bpy.types.Node,
    input_socket_name: str,
    debug: bool = False,
) -> None:
    node_tree = get_node_tree()
    output_socket = next(
        (socket for socket in output_node.outputs if socket.name == output_socket_name),
        None,
    )
    input_socket = next(
        (socket for socket in input_node.inputs if socket.name == input_socket_name),
        None,
    )

    if debug:
        output_sockets = [socket.name for socket in output_node.outputs]
        input_sockets = [socket.name for socket in input_node.inputs]
        print("output_node", output_node, output_sockets)
        print("input_node", input_node, input_sockets)

    if output_socket is None or input_socket is None:
        print(
            f"Error: Could not find specified sockets '{output_socket_name}' or '{input_socket_name}'."
        )
        return

    node_tree.links.new(output_socket, input_socket)


def link_by_socket_index(
    output_node: bpy.types.Node,
    input_node: bpy.types.Node,
    output_socket_index: int = 0,
    input_socket_index: int = 0,
    debug: bool = False,
) -> None:
    if debug:
        output_sockets = [socket.name for socket in output_node.outputs]
        input_sockets = [socket.name for socket in input_node.inputs]
        print("output_node", output_node, output_sockets)
        print("input_node", input_node, input_sockets)
    node_tree = get_node_tree()
    node_tree.links.new(
        output_node.outputs[output_socket_index], input_node.inputs[input_socket_index]
    )


def transform(
    node: bpy.types.Node,
    translation: Optional[tuple[float, float, float]] = None,
    rotation: Optional[tuple[float, float, float]] = None,
    scale: Optional[tuple[float, float, float]] = None,
    node_output: str = "Mesh",
) -> bpy.types.Node:
    node_location = get_location("middle")
    label = node.label

    transform_node = mesh(
        type="GeometryNodeTransform",
        label=f"{label} transform",
        node_location=node_location,
    )

    if translation is not None:
        node_location = get_location("middle")
        translation_vector = vector(
            label=f"{label} translation vector",
            node_location=node_location,
            value=translation,
        )
        translation_vector.label = f"{label} translation"
        link(translation_vector, "Vector", transform_node, "Translation")

    if rotation is not None:
        degree_vector = [c * 0.0174533 for c in rotation]
        node_location = get_location("middle")
        rotation_vector = vector(
            label=f"{label} rotation vector",
            node_location=node_location,
            value=degree_vector,
        )
        rotation_vector.label = f"{label} rotation"
        link(rotation_vector, "Vector", transform_node, "Rotation")

    if scale is not None:
        node_location = get_location("middle")
        scale_vector = vector(
            label=f"{label} scale", node_location=node_location, value=scale
        )
        scale_vector.label = f"{label} scale vector"
        link(scale_vector, "Vector", transform_node, "Scale")

    link(node, node_output, transform_node, "Geometry")
    return transform_node


def combine_xyz(x: float = 0, y: float = 0, z: float = 0) -> bpy.types.Node:
    node_location = get_location("middle")
    combine = mesh(
        label="combine xyz", node_location=node_location, type="ShaderNodeCombineXYZ"
    )
    combine.inputs[0].default_value = x
    combine.inputs[1].default_value = y
    combine.inputs[2].default_value = z
    return combine


def separate_xyz(x: float = 0, y: float = 0, z: float = 0) -> bpy.types.Node:
    node_location = get_location("middle")
    separate = mesh(node_location=node_location, type="ShaderNodeSeparateXYZ")
    separate.inputs[0].default_value = x
    separate.inputs[1].default_value = y
    separate.inputs[2].default_value = z
    return separate


def set_position(
    node: bpy.types.Node,
    position: Tuple[float, float, float],
) -> bpy.types.Node:
    label = node.label
    position_node = mesh(
        node_location=get_location("middle"), type="GeometryNodeSetPosition"
    )
    position_vector = vector(
        label=f"{label} position",
        node_location=get_location("middle"),
        value=position,
    )
    link(position_vector, "Vector", position_node, "Offset")

    output_sockets = [socket.name for socket in node.outputs]

    if "Geometry" in output_sockets:
        link(node, "Geometry", position_node, "Geometry")
    elif "Mesh" in output_sockets:
        link(node, "Mesh", position_node, "Geometry")

    return position_node


def extra_ops(
    node,
    position: Optional[Tuple[float, float, float]] = None,
    rotation: Optional[Tuple[float, float, float]] = None,
    scale: Optional[Tuple[float, float, float]] = None,
    translation: Optional[Tuple[float, float, float]] = None,
) -> bpy.types.Node:
    use_transform = translation is not None or rotation is not None or scale is not None
    use_position = position is not None and len(position) == 3

    if use_transform:
        node_transform = transform(node, translation, rotation, scale)
        if use_position is False:
            return node_transform

    if use_position:
        new_mesh = node_transform if use_transform else node
        node_position = set_position(new_mesh, position)
        return node_position

    return node


def point(x: float = 0, y: float = 0, z: float = 0, label: str = "") -> bpy.types.Node:

    new_point = mesh(
        type="GeometryNodePoints", label=label, node_location=(get_location("middle"))
    )
    new_point.inputs[1].default_value = [x, y, z]

    return new_point


def cube(
    x: float,
    y: float,
    z: float,
    label: str,
    position: Optional[Tuple[float, float, float]] = None,
    rotation: Optional[Tuple[float, float, float]] = None,
    scale: Optional[Tuple[float, float, float]] = None,
    translation: Optional[Tuple[float, float, float]] = None,
) -> bpy.types.Node:

    cube_main_size = vector(
        label=f"{label} size", node_location=get_location("start"), value=(x, y, z)
    )
    cube_main = mesh(
        label=f"{label}",
        node_location=(get_location("end")),
        type="GeometryNodeMeshCube",
    )
    cube_main.label = f"{label}"
    link(cube_main_size, "Vector", cube_main, "Size")

    return extra_ops(cube_main, position, rotation, scale, translation)


def cylinder(
    r: float,
    d: float,
    label: str = "",
    position: Optional[Tuple[float, float, float]] = None,
    translation: Optional[Tuple[float, float, float]] = None,
    rotation: Optional[Tuple[float, float, float]] = None,
    scale: Optional[Tuple[float, float, float]] = None,
    vertices: Optional[int] = 32,
) -> bpy.types.Node:

    cylinder_r = value(
        label=f"{label} radius", node_location=get_location("start"), value=r
    )
    cylinder_d = value(
        label=f"{label} depth", node_location=get_location("middle"), value=d
    )
    created_cylinder = mesh(
        label=f"{label}",
        node_location=get_location("middle"),
        type="GeometryNodeMeshCylinder",
    )
    created_cylinder.label = f"{label}"
    created_cylinder.inputs["Vertices"].default_value = vertices
    link(cylinder_r, "Value", created_cylinder, "Radius")
    link(cylinder_d, "Value", created_cylinder, "Depth")

    return extra_ops(created_cylinder, position, rotation, scale, translation)


def cone(
    r1: float,
    r2: float,
    d: float,
    label: str = "",
    position: Optional[Tuple[float, float, float]] = None,
    translation: Optional[Tuple[float, float, float]] = None,
    rotation: Optional[Tuple[float, float, float]] = None,
    scale: Optional[Tuple[float, float, float]] = None,
) -> bpy.types.Node:

    cone_r1 = value(
        label=f"{label} radius 1", node_location=get_location("start"), value=r1
    )
    cone_r2 = value(
        label=f"{label} radius 2", node_location=get_location("middle"), value=r2
    )
    cone_d = value(
        label=f"{label} depth", node_location=get_location("middle"), value=d
    )
    created_cone = mesh(
        label=f"{label}",
        node_location=get_location("middle"),
        type="GeometryNodeMeshCone",
    )
    created_cone.label = f"{label}"
    link(cone_r1, "Value", created_cone, "Radius Top")
    link(cone_r2, "Value", created_cone, "Radius Bottom")
    link(cone_d, "Value", created_cone, "Depth", debug=True)

    return extra_ops(created_cone, position, rotation, scale, translation)


def sphere(
    r: float,
    label: str = "",
    position: Optional[Tuple[float, float, float]] = None,
    translation: Optional[Tuple[float, float, float]] = None,
    rotation: Optional[Tuple[float, float, float]] = None,
    scale: Optional[Tuple[float, float, float]] = None,
    segments: Optional[int] = None,
    rings: Optional[int] = None,
) -> bpy.types.Node:

    sphere_r = value(
        label=f"{label} radius", node_location=get_location("start"), value=r
    )
    created_sphere = mesh(
        label=f"{label}",
        node_location=get_location("middle"),
        type="GeometryNodeMeshUVSphere",
    )
    created_sphere.label = f"{label}"
    link(sphere_r, "Value", created_sphere, "Radius")

    if segments is not None:
        created_sphere.inputs["Segments"].default_value = segments

    if rings is not None:
        created_sphere.inputs["Radius"].default_value = rings

    return extra_ops(created_sphere, position, rotation, scale, translation)


def clones(
    node: bpy.types.Node,
    points: List[Tuple[float, float, float]],
) -> bpy.types.Node:
    clones = []
    label = node.label
    for i, p in enumerate(points):
        new_point = point(*p, label=f"{label} {i} point")
        clones.append(new_point)
    clones_join = join(clones)

    instance_on_points = mesh(
        label=f"{label} instance on points",
        node_location=get_location("middle"),
        type="GeometryNodeInstanceOnPoints",
    )
    link(clones_join, "Geometry", instance_on_points, "Points")
    link(node, "Geometry", instance_on_points, "Instance")
    return instance_on_points
