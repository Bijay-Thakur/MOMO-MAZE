import unreal

level_path = "/Game/MomoMaze/Maps/M_Maze_31x31"
if unreal.EditorAssetLibrary.does_asset_exist(level_path):
    print("Asset exists, deleting existing level to recreate cleanly...")
    unreal.EditorAssetLibrary.delete_asset(level_path)

level_subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
success = level_subsystem.new_level(level_path)
print(f"new_level result: {success}")

world = unreal.EditorLevelLibrary.get_editor_world()
print(f"Current world: {world.get_path_name()}")

# Spawn a test hedge
mesh_hedge = unreal.EditorAssetLibrary.load_asset("/Game/Meshes/Environment/SM_Hedge_Straight")
actor = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(0,0,0))
actor.static_mesh_component.set_static_mesh(mesh_hedge)

# Save
saved = unreal.EditorLoadingAndSavingUtils.save_current_level()
print(f"Saved current level: {saved}")
