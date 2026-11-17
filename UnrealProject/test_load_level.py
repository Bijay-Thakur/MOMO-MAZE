import unreal

level_path = "/Game/MomoMaze/Maps/M_Maze_31x31"
level_subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
loaded = level_subsystem.load_level(level_path)
print(f"load_level result: {loaded}")

world = unreal.EditorLevelLibrary.get_editor_world()
print(f"Current world: {world.get_path_name()}")
