import unreal

world = unreal.EditorLoadingAndSavingUtils.load_map("/Game/MomoMaze/Maps/M_Maze_31x31")
all_actors = unreal.EditorLevelLibrary.get_all_level_actors()
with open("D:/Projects/MOMO MAZE/UnrealProject/count_actors.txt", "w") as f:
    f.write(f"Map: {world}\n")
    f.write(f"Total Actors: {len(all_actors)}\n")
    for a in all_actors[:20]:
        f.write(f"  {a.get_actor_label()} ({a.get_class().get_name()})\n")
