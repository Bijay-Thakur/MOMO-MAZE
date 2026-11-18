import bpy
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
SCENES_DIR = os.path.join(PROJECT_ROOT, "BlenderSources", "scenes")
MODELS_DIR = os.path.join(PROJECT_ROOT, "WebGame", "models")

modular_blend = os.path.join(SCENES_DIR, "environment_modular.blend")
bpy.ops.wm.open_mainfile(filepath=modular_blend)

pieces = [
    ("SM_Hedge_Straight", "SM_Hedge_Straight"),
    ("SM_Hedge_Corner", "SM_Hedge_Corner"),
    ("SM_Path_Tile", "SM_Path_Tile"),
    ("SM_Momo_Collectible", "SM_Momo_Collectible"),
    ("SM_Flower_Cluster", "SM_Flower_Cluster"),
    ("SM_Leaf_Gate", "SM_Leaf_Gate")
]

for obj_name, file_prefix in pieces:
    bpy.ops.object.select_all(action='DESELECT')
    target = None
    for obj in bpy.data.objects:
        if obj_name.lower() in obj.name.lower():
            obj.select_set(True)
            if not target: target = obj
    
    if target:
        bpy.context.view_layer.objects.active = target
        out_path = os.path.join(MODELS_DIR, f"{file_prefix}.glb")
        bpy.ops.export_scene.gltf(
            filepath=out_path,
            export_format='GLB',
            use_selection=True
        )
        print(f"Exported {file_prefix} -> {out_path} ({os.path.getsize(out_path)} bytes)")

print("Modular pieces export completed!")
