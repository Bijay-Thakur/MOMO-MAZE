import unreal

def inspect_maps():
    subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    
    maps = [
        "/Game/Maps/LVL_MomoMaze_Game",
        "/Game/MomoMaze/Maps/M_Maze_31x31",
        "/Game/Maps/LVL_UI_TestStage"
    ]
    
    with open("D:/Projects/MOMO MAZE/UnrealProject/inspect_maps_out.txt", "w", encoding="utf-8") as f:
        for m in maps:
            f.write(f"\n========================================\nMAP: {m}\n========================================\n")
            if not unreal.EditorAssetLibrary.does_asset_exist(m):
                f.write("Asset does not exist!\n")
                continue
            subsystem.load_level(m)
            actors = unreal.EditorLevelLibrary.get_all_level_actors()
            f.write(f"Actor count: {len(actors)}\n")
            
            cams = []
            starts = []
            lights = []
            char_actors = []
            for a in actors:
                cls = a.get_class().get_name()
                if "Camera" in cls:
                    cams.append(f"{a.get_name()} ({a.get_actor_location()}) rot={a.get_actor_rotation()} auto={a.get_editor_property('auto_activate_for_player') if hasattr(a, 'auto_activate_for_player') else 'N/A'}")
                elif "PlayerStart" in cls:
                    starts.append(f"{a.get_name()} ({a.get_actor_location()})")
                elif "Light" in cls:
                    lights.append(f"{a.get_name()} class={cls} loc={a.get_actor_location()}")
                elif "Character" in cls or "Pawn" in cls or "Golumolu" in a.get_name() or "Ghost" in a.get_name():
                    char_actors.append(f"{a.get_name()} class={cls} loc={a.get_actor_location()}")
                    
            f.write(f"Cameras ({len(cams)}): {cams}\n")
            f.write(f"PlayerStarts ({len(starts)}): {starts}\n")
            f.write(f"Lights ({len(lights)}): {lights}\n")
            f.write(f"Characters/Pawns ({len(char_actors)}): {char_actors[:10]}\n")

if __name__ == "__main__":
    inspect_maps()
