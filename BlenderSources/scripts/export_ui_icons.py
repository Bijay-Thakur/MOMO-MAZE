import bpy
import bmesh
import math
import os

def create_icons():
    scene_dir = r"D:\Projects\MOMO MAZE\BlenderSources\scenes"
    export_dir = r"D:\Projects\MOMO MAZE\BlenderSources\exports\fbx"
    
    # 1. Momo Icon: load SM_Momo_Collectible.fbx, scale and export as SM_UI_MomoIcon.fbx
    bpy.ops.wm.read_factory_settings(use_empty=True)
    momo_src = os.path.join(export_dir, "SM_Momo_Collectible.fbx")
    if os.path.exists(momo_src):
        bpy.ops.import_scene.fbx(filepath=momo_src)
        # Select all, join into single mesh
        bpy.ops.object.select_all(action='SELECT')
        bpy.context.view_layer.objects.active = bpy.context.selected_objects[0]
        bpy.ops.object.join()
        obj = bpy.context.active_object
        obj.name = "SM_UI_MomoIcon"
        # Center origin
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
        # Scale to ~0.7 unit
        obj.scale = (0.7, 0.7, 0.7)
        bpy.ops.object.transform_apply(scale=True)
        # Export
        out_path = os.path.join(export_dir, "SM_UI_MomoIcon.fbx")
        bpy.ops.export_scene.fbx(filepath=out_path, use_selection=True, mesh_smooth_type='FACE')
        print(f"Exported: SM_UI_MomoIcon.fbx")

    # 2. Spirit Icon: load ghost_follower_validated.fbx, join and scale to ~0.8 unit
    bpy.ops.wm.read_factory_settings(use_empty=True)
    ghost_src = os.path.join(export_dir, "ghost_follower_validated.fbx")
    if os.path.exists(ghost_src):
        bpy.ops.import_scene.fbx(filepath=ghost_src)
        bpy.ops.object.select_all(action='SELECT')
        bpy.context.view_layer.objects.active = bpy.context.selected_objects[0]
        bpy.ops.object.join()
        obj = bpy.context.active_object
        obj.name = "SM_UI_SpiritIcon"
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
        obj.scale = (0.008, 0.008, 0.008) # scale from character size down to icon size
        bpy.ops.object.transform_apply(scale=True)
        out_path = os.path.join(export_dir, "SM_UI_SpiritIcon.fbx")
        bpy.ops.export_scene.fbx(filepath=out_path, use_selection=True, mesh_smooth_type='FACE')
        print(f"Exported: SM_UI_SpiritIcon.fbx")

if __name__ == "__main__":
    create_icons()
