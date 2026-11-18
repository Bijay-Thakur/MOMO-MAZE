import unreal

def check_spawned_golumolu():
    log_file = "D:/Projects/MOMO MAZE/UnrealProject/golumolu_spawn_test.txt"
    with open(log_file, "w", encoding="utf-8") as log:
        subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
        subsystem.load_level("/Game/MomoMaze/Maps/M_Maze_31x31")
        world = unreal.EditorLevelLibrary.get_editor_world()
        
        bp_path = "/Game/Blueprints/Core/BP_GolumoluCharacter"
        bp = unreal.EditorAssetLibrary.load_asset(bp_path)
        gen_cls = bp.generated_class()
        
        # Spawn actor in world
        spawn_loc = unreal.Vector(0.0, 360.0, 100.0)
        actor = unreal.EditorLevelLibrary.spawn_actor_from_class(gen_cls, spawn_loc)
        log.write(f"Spawned actor: {actor}\n")
        if actor:
            comps = actor.get_components_by_class(unreal.ActorComponent)
            log.write(f"Spawned actor components ({len(comps)}):\n")
            for c in comps:
                cname = c.get_name()
                ccls = c.get_class().get_name()
                log.write(f"  {cname} ({ccls})\n")
                if isinstance(c, unreal.CameraComponent):
                    log.write(f"    Camera: rel_loc={c.get_relative_location()}, rel_rot={c.get_relative_rotation()}, fov={c.field_of_view}\n")
                elif isinstance(c, unreal.SpringArmComponent):
                    log.write(f"    SpringArm: arm_length={c.target_arm_length}, rel_rot={c.get_relative_rotation()}, do_collision={c.do_collision_test}\n")
                elif isinstance(c, unreal.StaticMeshComponent):
                    log.write(f"    StaticMesh: mesh={c.static_mesh}, mat={c.get_material(0)}\n")
            
            # Destroy temporary spawned actor
            unreal.EditorLevelLibrary.destroy_actor(actor)
            log.write("Cleaned up test actor.\n")

if __name__ == "__main__":
    check_spawned_golumolu()
