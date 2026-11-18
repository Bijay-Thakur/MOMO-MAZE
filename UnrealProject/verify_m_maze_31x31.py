import unreal

def verify_and_prep_maze():
    log_file = "D:/Projects/MOMO MAZE/UnrealProject/maze_prep_log.txt"
    with open(log_file, "w", encoding="utf-8") as log:
        subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
        map_path = "/Game/MomoMaze/Maps/M_Maze_31x31"
        subsystem.load_level(map_path)
        world = unreal.EditorLevelLibrary.get_editor_world()
        actors = unreal.EditorLevelLibrary.get_all_level_actors()
        
        log.write(f"Map: {map_path}, Total Actors: {len(actors)}\n")
        
        # Check CameraActors: ensure none have auto_activate_for_player set to PLAYER0
        for a in actors:
            if isinstance(a, unreal.CameraActor):
                auto_act = a.get_editor_property("auto_activate_for_player")
                log.write(f"CameraActor: {a.get_name()}, auto_activate={auto_act}\n")
                if auto_act != unreal.AutoReceiveInput.DISABLED:
                    a.set_editor_property("auto_activate_for_player", unreal.AutoReceiveInput.DISABLED)
                    log.write(f"  Disabled auto_activate on {a.get_name()}\n")

        # Check Lights
        dir_lights = [a for a in actors if isinstance(a, unreal.DirectionalLight)]
        sky_lights = [a for a in actors if isinstance(a, unreal.SkyLight)]
        log.write(f"DirectionalLights ({len(dir_lights)}):\n")
        for dl in dir_lights:
            comp = dl.root_component
            intensity = comp.get_editor_property("intensity")
            log.write(f"  {dl.get_name()}: intensity={intensity}, rot={dl.get_actor_rotation()}\n")
            if intensity < 3.0:
                comp.set_editor_property("intensity", 6.0)
                log.write(f"  Boosted intensity to 6.0 on {dl.get_name()}\n")

        log.write(f"SkyLights ({len(sky_lights)}):\n")
        for sl in sky_lights:
            comp = sl.root_component
            intensity = comp.get_editor_property("intensity")
            log.write(f"  {sl.get_name()}: intensity={intensity}\n")
            if intensity < 1.5:
                comp.set_editor_property("intensity", 2.0)
                log.write(f"  Boosted intensity to 2.0 on {sl.get_name()}\n")

        # Check PlayerStart
        starts = [a for a in actors if isinstance(a, unreal.PlayerStart)]
        log.write(f"PlayerStarts ({len(starts)}):\n")
        for ps in starts:
            log.write(f"  {ps.get_name()}: loc={ps.get_actor_location()}\n")

        # Save level
        saved = subsystem.save_current_level()
        log.write(f"Saved level: {saved}\n")

if __name__ == "__main__":
    verify_and_prep_maze()
