import unreal
import os

def run_import():
    fbx_dir = r"D:/Projects/MOMO MAZE/BlenderSources/exports/fbx"
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    
    # 1. Import UI meshes
    ui_files = [f for f in os.listdir(fbx_dir) if f.startswith("SM_UI_") and f.endswith(".fbx")]
    print(f"Found {len(ui_files)} UI FBX files to import...")
    
    tasks = []
    for f in ui_files:
        task = unreal.AssetImportTask()
        task.filename = os.path.join(fbx_dir, f).replace("\\", "/")
        task.destination_path = "/Game/Meshes/UI"
        task.destination_name = f.replace(".fbx", "")
        task.replace_existing = True
        task.automated = True
        task.save = True
        
        options = unreal.FbxImportUI()
        options.import_mesh = True
        options.import_textures = False
        options.import_materials = False
        options.mesh_type_to_import = unreal.FBXImportType.FBXIT_STATIC_MESH
        options.static_mesh_import_data.combine_meshes = True
        options.static_mesh_import_data.generate_lightmap_u_vs = True
        options.static_mesh_import_data.auto_generate_collision = True
        task.options = options
        tasks.append(task)
        
    # 2. Import Environment meshes
    env_files = ["SM_Flower_Cluster.fbx", "SM_Hedge_Corner.fbx", "SM_Hedge_Straight.fbx", "SM_Leaf_Gate.fbx", "SM_Momo_Collectible.fbx", "SM_Path_Tile.fbx"]
    for f in env_files:
        full_p = os.path.join(fbx_dir, f).replace("\\", "/")
        if os.path.exists(full_p):
            task = unreal.AssetImportTask()
            task.filename = full_p
            task.destination_path = "/Game/Meshes/Environment"
            task.destination_name = f.replace(".fbx", "")
            task.replace_existing = True
            task.automated = True
            task.save = True
            
            options = unreal.FbxImportUI()
            options.import_mesh = True
            options.import_textures = False
            options.import_materials = False
            options.mesh_type_to_import = unreal.FBXImportType.FBXIT_STATIC_MESH
            options.static_mesh_import_data.combine_meshes = True
            options.static_mesh_import_data.auto_generate_collision = True
            task.options = options
            tasks.append(task)

    # 3. Import Character meshes (Golumolu and ghosts)
    char_files = [
        ("golumolu_validated.fbx", "SK_Golumolu"),
        ("ghost_follower_validated.fbx", "SK_Ghost_Follower"),
        ("ghost_cutter_validated.fbx", "SK_Ghost_Cutter"),
        ("ghost_wanderer_validated.fbx", "SK_Ghost_Wanderer")
    ]
    for f, asset_name in char_files:
        full_p = os.path.join(fbx_dir, f).replace("\\", "/")
        if os.path.exists(full_p):
            task = unreal.AssetImportTask()
            task.filename = full_p
            task.destination_path = "/Game/Meshes/Characters"
            task.destination_name = asset_name
            task.replace_existing = True
            task.automated = True
            task.save = True
            
            options = unreal.FbxImportUI()
            options.import_mesh = True
            options.import_textures = False
            options.import_materials = False
            # Static mesh representation for game rendering
            options.mesh_type_to_import = unreal.FBXImportType.FBXIT_STATIC_MESH
            options.static_mesh_import_data.combine_meshes = True
            options.static_mesh_import_data.auto_generate_collision = True
            task.options = options
            tasks.append(task)

    print(f"Total tasks executing: {len(tasks)}")
    asset_tools.import_asset_tasks(tasks)
    print("Import finished successfully!")

if __name__ == "__main__":
    run_import()
