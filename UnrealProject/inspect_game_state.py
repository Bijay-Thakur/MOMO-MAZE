import unreal

def inspect():
    subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    subsystem.load_level("/Game/Maps/LVL_MomoMaze_Game")
    world = unreal.EditorLevelLibrary.get_editor_world()
    
    with open("D:/Projects/MOMO MAZE/UnrealProject/inspect_world_out.txt", "w", encoding="utf-8") as f:
        f.write(f"World: {world}\n")
        
        # Check GameMode
        gm_bp = unreal.EditorAssetLibrary.load_asset("/Game/Blueprints/Core/BP_MomoGameMode")
        f.write(f"GameMode BP: {gm_bp}\n")
        if gm_bp:
            cdo = unreal.get_default_object(gm_bp.generated_class())
            f.write(f"  default_pawn_class: {cdo.get_editor_property('default_pawn_class')}\n")
            f.write(f"  player_controller_class: {cdo.get_editor_property('player_controller_class')}\n")
            f.write(f"  spectator_class: {cdo.get_editor_property('spectator_class')}\n")
            
        actors = unreal.EditorLevelLibrary.get_all_level_actors()
        f.write(f"Total Actors: {len(actors)}\n")
        
        counts = {}
        for a in actors:
            cls = a.get_class().get_name()
            counts[cls] = counts.get(cls, 0) + 1
            if isinstance(a, unreal.CameraActor):
                f.write(f"Camera: {a.get_name()}, loc: {a.get_actor_location()}, rot: {a.get_actor_rotation()}, auto_activate: {a.get_editor_property('auto_activate_for_player')}\n")
            elif isinstance(a, unreal.PlayerStart):
                f.write(f"PlayerStart: {a.get_name()}, loc: {a.get_actor_location()}\n")
            elif isinstance(a, unreal.DirectionalLight):
                comp = a.root_component
                f.write(f"DirectionalLight: {a.get_name()}, loc: {a.get_actor_location()}, rot: {a.get_actor_rotation()}, intensity: {comp.get_editor_property('intensity')}, mobility: {comp.get_editor_property('mobility')}\n")
            elif isinstance(a, unreal.SkyLight):
                comp = a.root_component
                f.write(f"SkyLight: {a.get_name()}, intensity: {comp.get_editor_property('intensity')}, mobility: {comp.get_editor_property('mobility')}\n")
            elif isinstance(a, unreal.PostProcessVolume):
                f.write(f"PostProcessVolume: {a.get_name()}, unbound: {a.get_editor_property('unbound')}\n")

        f.write(f"Actor class counts: {counts}\n")
        
        # Check Golumolu BP components
        golu_bp = unreal.EditorAssetLibrary.load_asset("/Game/Blueprints/Core/BP_GolumoluCharacter")
        if golu_bp:
            f.write(f"Golumolu BP: {golu_bp}\n")
            gcdo = unreal.get_default_object(golu_bp.generated_class())
            f.write(f"  Golumolu CDO: {gcdo}\n")
            # List components on CDO
            comps = gcdo.get_components_by_class(unreal.ActorComponent)
            f.write(f"  Golumolu CDO components: {[c.get_name() for c in comps]}\n")
            for c in comps:
                if isinstance(c, unreal.CameraComponent):
                    f.write(f"    CameraComp: rel_loc={c.get_relative_location()}, rel_rot={c.get_relative_rotation()}, fov={c.field_of_view}\n")
                elif isinstance(c, unreal.SpringArmComponent):
                    f.write(f"    SpringArm: target_arm_length={c.target_arm_length}, rel_rot={c.get_relative_rotation()}, do_collision={c.do_collision_test}\n")
                elif isinstance(c, unreal.StaticMeshComponent):
                    f.write(f"    StaticMeshComp: mesh={c.static_mesh}, mat0={c.get_material(0)}, rel_loc={c.get_relative_location()}\n")

if __name__ == "__main__":
    inspect()
