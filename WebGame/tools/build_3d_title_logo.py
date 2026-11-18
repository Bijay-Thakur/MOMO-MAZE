"""
Procedural 3D Title Logo Generator for MOMO MAZE
Creates SM_UI_TitleLogo matching Screen 01-A Splash reference:
- Steamed Momo dumpling crest on top with gathered pleats
- 3D pillowy "MOMO" bevelled text with cream face and toasted-brown outline
- 3D pillowy "MAZE" bevelled text with fresh leaf-green face and toasted-brown outline
- Flanking twin leaf pairs
- Stylized golden burst rays
Exports to:
- WebGame/models/SM_UI_TitleLogo.glb
- UnrealProject/Content/UI/SM_UI_TitleLogo.fbx
"""

import bpy
import bmesh
import math
import os
from mathutils import Vector, Matrix

# Clear all existing scene objects
bpy.ops.wm.read_factory_settings(use_empty=True)

# -------------------------------------------------------------------------
# Materials Helper
# -------------------------------------------------------------------------
def create_pbr_material(name, base_color, roughness=0.35, metallic=0.0):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = base_color
        bsdf.inputs['Roughness'].default_value = roughness
        bsdf.inputs['Metallic'].default_value = metallic
    return mat

mat_cream = create_pbr_material("M_LogoCream", (1.0, 0.98, 0.92, 1.0), roughness=0.3)
mat_green = create_pbr_material("M_LogoGreen", (0.55, 0.78, 0.18, 1.0), roughness=0.35)
mat_toast = create_pbr_material("M_LogoToastOutline", (0.38, 0.20, 0.10, 1.0), roughness=0.5)
mat_gold  = create_pbr_material("M_LogoGoldRays", (1.0, 0.75, 0.20, 1.0), roughness=0.25)
mat_leaf  = create_pbr_material("M_LogoLeaf", (0.42, 0.65, 0.15, 1.0), roughness=0.4)

root_collection = bpy.context.scene.collection
logo_objects = []

# -------------------------------------------------------------------------
# 1. Steamed Momo Dumpling Crest (Top Center)
# -------------------------------------------------------------------------
def make_momo_crest(center=(0, 0, 1.35), scale=0.45):
    # Base rounded bun
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=24, v_segments=16, radius=1.0)
    
    # Deform vertices into pleated steamed momo shape:
    # squash vertically, pull top vertex into a spiral twist peak, add vertical creases
    for v in bm.verts:
        # Normalize height
        z = v.co.z
        r = math.sqrt(v.co.x**2 + v.co.y**2)
        angle = math.atan2(v.co.y, v.co.x)
        
        # Pleats (6 flutes)
        pleat = 1.0 + 0.12 * math.cos(angle * 7.0) * max(0.0, z + 0.2)
        v.co.x *= pleat
        v.co.y *= pleat
        
        # Flatten bottom slightly, elevate peak
        if z < -0.3:
            v.co.z = -0.3 + (z + 0.3) * 0.3
        elif z > 0.6:
            v.co.z = 0.6 + (z - 0.6) * 1.4
            # twist near the peak
            twist = (z - 0.6) * 1.5
            cos_t, sin_t = math.cos(twist), math.sin(twist)
            x_new = v.co.x * cos_t - v.co.y * sin_t
            y_new = v.co.x * sin_t + v.co.y * cos_t
            v.co.x, v.co.y = x_new, y_new
            
        # Scale to size
        v.co.x *= scale * 1.2
        v.co.y *= scale * 0.8  # Slight front-back depth compression
        v.co.z *= scale * 0.95
        v.co.x += center[0]
        v.co.y += center[1]
        v.co.z += center[2]
        
    mesh = bpy.data.meshes.new("MomoCrestMesh")
    bm.to_mesh(mesh)
    bm.free()
    
    obj = bpy.data.objects.new("SM_MomoCrest", mesh)
    obj.data.materials.append(mat_cream)
    root_collection.objects.link(obj)
    
    # Subsurf modifier for soft pillowy feel
    sub = obj.modifiers.new("Subsurf", type='SUBSURF')
    sub.levels = 1
    sub.render_levels = 2
    
    # Also add a toast backplate behind the crest
    bm_back = bmesh.new()
    bmesh.ops.create_uvsphere(bm_back, u_segments=16, v_segments=12, radius=1.0)
    for v in bm_back.verts:
        v.co.x *= scale * 1.35
        v.co.y *= scale * 0.9
        v.co.z *= scale * 1.1
        v.co.x += center[0]
        v.co.y += center[1] - 0.08
        v.co.z += center[2]
    mesh_back = bpy.data.meshes.new("MomoCrestOutlineMesh")
    bm_back.to_mesh(mesh_back)
    bm_back.free()
    obj_back = bpy.data.objects.new("SM_MomoCrestOutline", mesh_back)
    obj_back.data.materials.append(mat_toast)
    root_collection.objects.link(obj_back)
    
    logo_objects.extend([obj, obj_back])

make_momo_crest()

# -------------------------------------------------------------------------
# 2. Text "MOMO" and "MAZE"
# -------------------------------------------------------------------------
def create_pillowy_text(text_string, loc, font_size, extrude_depth, bevel_depth, mat_face, mat_outline, y_offset=0.0):
    # Text Curve Object
    t_data = bpy.data.curves.new(name=f"TextCurve_{text_string}", type='FONT')
    t_data.body = text_string
    t_data.size = font_size
    t_data.align_x = 'CENTER'
    t_data.align_y = 'CENTER'
    t_data.extrude = extrude_depth
    t_data.bevel_depth = bevel_depth
    t_data.bevel_resolution = 3
    
    # Front text object
    obj_front = bpy.data.objects.new(f"Text_{text_string}_Front", t_data)
    obj_front.location = Vector((loc[0], loc[1] + 0.05, loc[2]))
    obj_front.rotation_euler = (math.radians(90), 0, 0)
    obj_front.data.materials.append(mat_face)
    root_collection.objects.link(obj_front)
    
    # Convert front to mesh so it exports cleanly in glb
    bpy.context.view_layer.objects.active = obj_front
    obj_front.select_set(True)
    bpy.ops.object.convert(target='MESH')
    obj_front.select_set(False)
    
    # Backing outline object (slightly thicker, behind front)
    t_back_data = bpy.data.curves.new(name=f"TextCurve_{text_string}_Back", type='FONT')
    t_back_data.body = text_string
    t_back_data.size = font_size
    t_back_data.align_x = 'CENTER'
    t_back_data.align_y = 'CENTER'
    t_back_data.extrude = extrude_depth + 0.08
    t_back_data.bevel_depth = bevel_depth + 0.06
    t_back_data.bevel_resolution = 2
    
    obj_back = bpy.data.objects.new(f"Text_{text_string}_Outline", t_back_data)
    obj_back.location = Vector((loc[0], loc[1] - 0.04, loc[2]))
    obj_back.rotation_euler = (math.radians(90), 0, 0)
    obj_back.data.materials.append(mat_outline)
    root_collection.objects.link(obj_back)
    
    bpy.context.view_layer.objects.active = obj_back
    obj_back.select_set(True)
    bpy.ops.object.convert(target='MESH')
    obj_back.select_set(False)
    
    logo_objects.extend([obj_front, obj_back])

# "MOMO" in Cream on top
create_pillowy_text(
    "MOMO",
    loc=(0, 0, 0.72),
    font_size=1.05,
    extrude_depth=0.10,
    bevel_depth=0.08,
    mat_face=mat_cream,
    mat_outline=mat_toast
)

# "MAZE" in Leaf-Green below
create_pillowy_text(
    "MAZE",
    loc=(0, 0, -0.22),
    font_size=1.15,
    extrude_depth=0.10,
    bevel_depth=0.08,
    mat_face=mat_green,
    mat_outline=mat_toast
)

# -------------------------------------------------------------------------
# 3. Flanking Side Leaves (Left and Right of "MAZE")
# -------------------------------------------------------------------------
def create_leaf_sprig(center, angle_deg, scale=(0.3, 0.15, 0.06)):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=16, v_segments=10, radius=1.0)
    for v in bm.verts:
        # Teardrop tapering
        t = (v.co.x + 1.0) * 0.5
        v.co.y *= (1.0 - t * 0.6)
        v.co.z *= 0.35
        v.co.x *= scale[0]
        v.co.y *= scale[1]
        v.co.z *= scale[2]
        
    mesh = bpy.data.meshes.new("LeafMesh")
    bm.to_mesh(mesh)
    bm.free()
    
    obj = bpy.data.objects.new("SM_LogoLeaf", mesh)
    obj.location = Vector(center)
    obj.rotation_euler = (math.radians(90), 0, math.radians(angle_deg))
    obj.data.materials.append(mat_leaf)
    root_collection.objects.link(obj)
    logo_objects.append(obj)

# Left leaf pair
create_leaf_sprig((-1.55, 0, -0.20), angle_deg=160, scale=(0.32, 0.16, 0.06))
create_leaf_sprig((-1.35, 0, -0.40), angle_deg=200, scale=(0.26, 0.14, 0.05))

# Right leaf pair
create_leaf_sprig((1.55, 0, -0.20), angle_deg=20, scale=(0.32, 0.16, 0.06))
create_leaf_sprig((1.35, 0, -0.40), angle_deg=-20, scale=(0.26, 0.14, 0.05))

# -------------------------------------------------------------------------
# 4. Stylized Golden Sunburst Rays
# -------------------------------------------------------------------------
def create_burst_ray(center, angle_deg, length=0.25, width=0.06):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=12, v_segments=8, radius=1.0)
    for v in bm.verts:
        v.co.x *= width
        v.co.y *= width * 0.6
        v.co.z *= length
    mesh = bpy.data.meshes.new("RayMesh")
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new("SM_SunburstRay", mesh)
    obj.location = Vector(center)
    obj.rotation_euler = (math.radians(90), math.radians(angle_deg), 0)
    obj.data.materials.append(mat_gold)
    root_collection.objects.link(obj)
    logo_objects.append(obj)

# Rays radiating around top and sides
ray_positions = [
    ((-1.8, 0, 0.6), 40),
    ((-1.9, 0, 0.35), 65),
    ((-1.85, 0, 0.1), 85),
    ((1.8, 0, 0.6), -40),
    ((1.9, 0, 0.35), -65),
    ((1.85, 0, 0.1), -85),
]
for pos, ang in ray_positions:
    create_burst_ray(pos, ang)

# -------------------------------------------------------------------------
# 5. Join into Single Cohesive Static Mesh & Export
# -------------------------------------------------------------------------
bpy.ops.object.select_all(action='DESELECT')
for obj in logo_objects:
    obj.select_set(True)
bpy.context.view_layer.objects.active = logo_objects[0]
bpy.ops.object.join()
final_logo = bpy.context.active_object
final_logo.name = "SM_UI_TitleLogo"

# Ensure smooth shading
for poly in final_logo.data.polygons:
    poly.use_smooth = True

# Export GLB
glb_path = r"d:\Projects\MOMO MAZE\WebGame\models\SM_UI_TitleLogo.glb"
os.makedirs(os.path.dirname(glb_path), exist_ok=True)
bpy.ops.export_scene.gltf(
    filepath=glb_path,
    export_format='GLB',
    use_selection=True,
    export_materials='EXPORT',
    export_yup=True
)
print(f"Exported GLB: {glb_path} ({os.path.getsize(glb_path)} bytes)")

# Export FBX for Unreal Engine
fbx_path = r"d:\Projects\MOMO MAZE\UnrealProject\Content\UI\SM_UI_TitleLogo.fbx"
os.makedirs(os.path.dirname(fbx_path), exist_ok=True)
bpy.ops.export_scene.fbx(
    filepath=fbx_path,
    use_selection=True,
    bake_space_transform=True,
    axis_forward='-Z',
    axis_up='Y'
)
print(f"Exported FBX: {fbx_path} ({os.path.getsize(fbx_path)} bytes)")
