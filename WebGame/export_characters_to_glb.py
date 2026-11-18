import bpy
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
SCENES_DIR = os.path.join(PROJECT_ROOT, "BlenderSources", "scenes")
MODELS_DIR = os.path.join(PROJECT_ROOT, "WebGame", "models")

os.makedirs(MODELS_DIR, exist_ok=True)

# ── 1. GOLUMOLU EXPORT ─────────────────────────────────────────────────────────
golu_blend = os.path.join(SCENES_DIR, "golumolu_validated.blend")
bpy.ops.wm.open_mainfile(filepath=golu_blend)

# Modify fur material to be distinct, vibrant warm golden-apricot / honey dino
for mat in bpy.data.materials:
    if "Fur" in mat.name or "Body" in mat.name:
        if "Principled BSDF" in mat.node_tree.nodes:
            # Warm golden peach fur: (1.0, 0.62, 0.28)
            mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (1.0, 0.62, 0.28, 1.0)
            mat.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.82
    elif "Peach" in mat.name or "Accent" in mat.name:
        if "Principled BSDF" in mat.node_tree.nodes:
            # Richer peach for ears/paws/tail: (1.0, 0.50, 0.22)
            mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (1.0, 0.50, 0.22, 1.0)
    elif "Cheek" in mat.name or "blush" in mat.name.lower():
        if "Principled BSDF" in mat.node_tree.nodes:
            # Bright rosy blush
            mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (1.0, 0.35, 0.45, 1.0)

# Export Golumolu GLB
golu_out = os.path.join(MODELS_DIR, "golumolu.glb")
bpy.ops.export_scene.gltf(
    filepath=golu_out,
    export_format='GLB',
    use_selection=False
)
print("Exported Golumolu to:", golu_out, os.path.getsize(golu_out))


# ── 2. GHOSTS EXPORT (With Elongated Flying Tails) ─────────────────────────────
ghosts_blend = os.path.join(SCENES_DIR, "ghosts_validated.blend")
bpy.ops.wm.open_mainfile(filepath=ghosts_blend)

# Elongate all tail meshes to make them long, wispy, floating and flying!
for obj in bpy.data.objects:
    if obj.type == 'MESH':
        name_lower = obj.name.lower()
        if "tail" in name_lower:
            # Stretch tail along trailing axis by 2.4x
            obj.scale.y *= 2.4
            obj.scale.z *= 2.4
            bpy.ops.object.select_all(action='DESELECT')
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.transform_apply(scale=True)
            print(f"Elongated ghost tail mesh: {obj.name}")

# Ensure ghost material has soft ethereal glow and translucent look
for mat in bpy.data.materials:
    if "Principled BSDF" in mat.node_tree.nodes:
        bsdf = mat.node_tree.nodes["Principled BSDF"]
        # Ethereal silver-white body with subtle emission
        if "body" in mat.name.lower() or "white" in mat.name.lower():
            bsdf.inputs["Base Color"].default_value = (0.96, 0.98, 1.0, 0.85)
            if "Emission Color" in bsdf.inputs:
                bsdf.inputs["Emission Color"].default_value = (0.9, 0.95, 1.0, 1.0)
                bsdf.inputs["Emission Strength"].default_value = 0.45

# 2A. Export Follower
bpy.ops.object.select_all(action='DESELECT')
for obj in bpy.data.objects:
    if "follower" in obj.name.lower() or obj.name == "Spirit_Follower_Root":
        obj.select_set(True)

follower_out = os.path.join(MODELS_DIR, "ghost_follower.glb")
bpy.ops.export_scene.gltf(
    filepath=follower_out,
    export_format='GLB',
    use_selection=True
)
print("Exported Ghost Follower to:", follower_out, os.path.getsize(follower_out))

# 2B. Export Cutter
bpy.ops.object.select_all(action='DESELECT')
for obj in bpy.data.objects:
    if "cutter" in obj.name.lower() or obj.name == "Spirit_Cutter_Root":
        obj.select_set(True)

cutter_out = os.path.join(MODELS_DIR, "ghost_cutter.glb")
bpy.ops.export_scene.gltf(
    filepath=cutter_out,
    export_format='GLB',
    use_selection=True
)
print("Exported Ghost Cutter to:", cutter_out, os.path.getsize(cutter_out))

# 2C. Export Wanderer
bpy.ops.object.select_all(action='DESELECT')
for obj in bpy.data.objects:
    if "wanderer" in obj.name.lower() or obj.name == "Spirit_Wanderer_Root":
        obj.select_set(True)

wanderer_out = os.path.join(MODELS_DIR, "ghost_wanderer.glb")
bpy.ops.export_scene.gltf(
    filepath=wanderer_out,
    export_format='GLB',
    use_selection=True
)
print("Exported Ghost Wanderer to:", wanderer_out, os.path.getsize(wanderer_out))
