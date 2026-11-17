import unreal
import os
import traceback

LOG_FILE = "D:/Projects/MOMO MAZE/UnrealProject/ue_import_log.txt"

def log(msg):
    with open(LOG_FILE, "a") as f:
        f.write(msg + "\n")
    print(msg)

FBX_DIR = "D:/Projects/MOMO MAZE/BlenderSources/exports/fbx"

ASSET_MAPPINGS = [
    # Characters
    {"fbx": "golumolu_validated.fbx", "dest": "/Game/MomoMaze/Meshes/Characters"},
    {"fbx": "ghost_follower_validated.fbx", "dest": "/Game/MomoMaze/Meshes/Characters"},
    {"fbx": "ghost_cutter_validated.fbx", "dest": "/Game/MomoMaze/Meshes/Characters"},
    {"fbx": "ghost_wanderer_validated.fbx", "dest": "/Game/MomoMaze/Meshes/Characters"},
    # Environment
    {"fbx": "SM_Hedge_Straight.fbx", "dest": "/Game/MomoMaze/Meshes/Environment"},
    {"fbx": "SM_Hedge_Corner.fbx", "dest": "/Game/MomoMaze/Meshes/Environment"},
    {"fbx": "SM_Path_Tile.fbx", "dest": "/Game/MomoMaze/Meshes/Environment"},
    {"fbx": "SM_Leaf_Gate.fbx", "dest": "/Game/MomoMaze/Meshes/Environment"},
    {"fbx": "SM_Momo_Collectible.fbx", "dest": "/Game/MomoMaze/Meshes/Environment"},
    {"fbx": "SM_Flower_Cluster.fbx", "dest": "/Game/MomoMaze/Meshes/Environment"},
]

def main():
    with open(LOG_FILE, "w") as f:
        f.write("Starting UE 5.8 Master Asset Import...\n")
    try:
        log("Importing Master FBX Assets into Unreal Engine 5.8...")
        asset_tools = unreal.AssetToolsHelpers.get_asset_tools()

        for item in ASSET_MAPPINGS:
            source_file = f"{FBX_DIR}/{item['fbx']}"
            if not os.path.exists(source_file):
                log(f"Error: {source_file} not found!")
                continue

            task = unreal.AssetImportTask()
            task.filename = source_file
            task.destination_path = item["dest"]
            task.destination_name = os.path.splitext(item["fbx"])[0]
            task.replace_existing = True
            task.automated = True
            task.save = True

            options = unreal.FbxImportUI()
            options.import_mesh = True
            options.import_textures = False
            options.import_materials = False
            options.import_as_skeletal = False
            
            mesh_data = unreal.FbxStaticMeshImportData()
            mesh_data.combine_meshes = True
            mesh_data.auto_generate_collision = True
            options.static_mesh_import_data = mesh_data
            task.options = options

            asset_tools.import_asset_tasks([task])
            log(f"  ✓ Imported -> {item['dest']}/{task.destination_name}")

        unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
        log("All assets imported and saved into Unreal Engine project successfully!")
    except Exception as e:
        log(f"EXCEPTION: {e}\n{traceback.format_exc()}")

if __name__ == "__main__":
    main()
