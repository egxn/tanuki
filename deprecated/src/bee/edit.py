import bpy
from typing import List, Optional, Tuple

def apply_all_modifiers(obj_name):
    obj = bpy.data.objects[obj_name]
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='OBJECT')

    for modifier in obj.modifiers:
        bpy.ops.object.modifier_apply(modifier=modifier.name)

def select_vertex(obj_name,
                  min_y: float,
                  min_x: float,
                  min_z: float,
                  max_y: float,
                  max_x: float,
                  max_z: float,
                  extend: bool = False):
    obj = bpy.data.objects[obj_name]
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    if not extend:
        bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.mesh.select_mode(type="VERT")
    mesh = obj.data
    bpy.ops.object.mode_set(mode='OBJECT')
    for vert in mesh.vertices:
        if min_x <= vert.co.x <= max_x and min_y <= vert.co.y <= max_y and min_z <= vert.co.z <= max_z:
            vert.select = True
    bpy.ops.object.mode_set(mode='EDIT')

def select_vertex_by_radius(obj_name: str, min_radius: float, max_radius: float, extend: bool = False):
    obj = bpy.data.objects[obj_name]
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    if not extend:
        bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.mesh.select_mode(type="VERT")
    mesh = obj.data
    bpy.ops.object.mode_set(mode='OBJECT')
    for vert in mesh.vertices:
        radius = (vert.co.x ** 2 + vert.co.y ** 2 + vert.co.z ** 2) ** 0.5
        if min_radius <= radius <= max_radius:
            vert.select = True
    bpy.ops.object.mode_set(mode='EDIT')

def select_faces_by_radius(obj_name: str, min_radius: float, max_radius: float, extend: bool = False):
    obj = bpy.data.objects[obj_name]
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    if not extend:
        bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.mesh.select_mode(type="FACE")
    mesh = obj.data
    bpy.ops.object.mode_set(mode='OBJECT')
    for face in mesh.polygons:
        center = face.center
        radius = (center.x ** 2 + center.y ** 2 + center.z ** 2) ** 0.5
        if min_radius <= radius <= max_radius:
            face.select = True
    bpy.ops.object.mode_set(mode='EDIT')
    
def select_faces_z_by_radius(obj_name: str, min_radius: float, max_radius: float, extend: bool = False):
    obj = bpy.data.objects[obj_name]
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    if not extend:
        bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.mesh.select_mode(type="FACE")
    mesh = obj.data
    bpy.ops.object.mode_set(mode='OBJECT')
    for face in mesh.polygons:
        center = face.center
        radius = (center.x ** 2 + center.y ** 2) ** 0.5
        if min_radius <= radius <= max_radius and center.z == 0:
            face.select = True
    bpy.ops.object.mode_set(mode='EDIT')

def clone_object(obj_name):
    obj = bpy.data.objects[obj_name]
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.ops.object.duplicate()
    duplicated_obj = bpy.context.selected_objects[0]
    return duplicated_obj

def scale(scale_x: Optional[float] = 1, scale_y: Optional[float] = 1, scale_z: Optional[float] = 1):
    bpy.ops.transform.resize(value=(scale_x, scale_y, scale_z))


