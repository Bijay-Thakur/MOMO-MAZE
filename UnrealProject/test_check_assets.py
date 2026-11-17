import unreal

assets_to_check = [
    "/Game/MomoMaze/Meshes/Environment/SM_Hedge_Straight",
    "/Game/MomoMaze/Meshes/Environment/SM_Path_Tile",
    "/Game/MomoMaze/Meshes/Environment/SM_Momo_Collectible",
    "/Game/MomoMaze/Meshes/Environment/SM_Leaf_Gate",
    "/Game/MomoMaze/Meshes/Characters/golumolu_validated",
    "/Game/MomoMaze/Meshes/Characters/ghost_follower_validated",
    "/Game/MomoMaze/Meshes/Characters/ghost_cutter_validated",
    "/Game/MomoMaze/Meshes/Characters/ghost_wanderer_validated",
    "/Game/Meshes/Environment/SM_Hedge_Straight",
    "/Game/Meshes/Environment/SM_Path_Tile",
]

with open("D:/Projects/MOMO MAZE/UnrealProject/check_assets.txt", "w") as f:
    for path in assets_to_check:
        obj = unreal.EditorAssetLibrary.load_asset(path)
        f.write(f"{path} -> {obj}\n")
