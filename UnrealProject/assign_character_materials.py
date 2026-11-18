import unreal

def assign_materials():
    log_file = "D:/Projects/MOMO MAZE/UnrealProject/assign_mats_log.txt"
    with open(log_file, "w", encoding="utf-8") as log:
        log.write("=== Assigning Beautiful Existing Materials to Golumolu ===\n")
        
        m_fur = unreal.EditorAssetLibrary.load_asset("/Game/Materials/Characters/M_Golumolu_Fur")
        m_green = unreal.EditorAssetLibrary.load_asset("/Game/Materials/UI/M_UI_LeafGreen")
        m_gold = unreal.EditorAssetLibrary.load_asset("/Game/Materials/UI/M_UI_Gold")
        m_coral = unreal.EditorAssetLibrary.load_asset("/Game/Materials/UI/M_UI_CoralHeart")
        m_white = unreal.EditorAssetLibrary.load_asset("/Game/Materials/UI/M_UI_SpiritWhite")
        m_dark = unreal.EditorAssetLibrary.load_asset("/Game/Materials/UI/M_UI_ToastBrown")
        
        log.write(f"Loaded mats: green={m_green}, gold={m_gold}, coral={m_coral}, white={m_white}, dark={m_dark}\n")
        
        # 1. Update SK_Golumolu mesh slots
        sk = unreal.EditorAssetLibrary.load_asset("/Game/Meshes/Characters/SK_Golumolu")
        if sk:
            # Slot 0: Peach Accent (Horns, tail spikes, belly) -> Gold
            sk.set_material(0, m_gold)
            # Slot 1: Cheeks -> Coral pink
            sk.set_material(1, m_coral)
            # Slot 2: Fluffy Fur (Main body) -> Leaf Green / Fur
            sk.set_material(2, m_green if m_green else m_fur)
            # Slot 3: Eyes -> Toast Brown / Dark
            sk.set_material(3, m_dark)
            # Slot 4: Mouth -> Coral / Dark
            sk.set_material(4, m_dark)
            # Slot 5: Eye Shine -> Spirit White
            sk.set_material(5, m_white)
            # Slot 6: Tongue -> Coral
            sk.set_material(6, m_coral)
            
            unreal.EditorAssetLibrary.save_asset("/Game/Meshes/Characters/SK_Golumolu")
            log.write("Saved SK_Golumolu with all 7 colorful materials!\n")

        # 2. Update BP_GolumoluCharacter
        bp = unreal.EditorAssetLibrary.load_asset("/Game/Blueprints/Core/BP_GolumoluCharacter")
        if bp:
            subsystem = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
            lib = unreal.SubobjectDataBlueprintFunctionLibrary
            handles = subsystem.k2_gather_subobject_data_for_blueprint(bp)
            
            for h in handles:
                data = subsystem.k2_find_subobject_data_from_handle(h)
                vname = str(lib.get_variable_name(data))
                obj = lib.get_associated_object(data)
                if "SpringArm" in vname and isinstance(obj, unreal.SpringArmComponent):
                    obj.set_editor_property("target_arm_length", 1300.0)
                    obj.set_editor_property("target_offset", unreal.Vector(0.0, 0.0, 80.0))
                    obj.set_relative_rotation(unreal.Rotator(-48.0, 0.0, 0.0), False, False)
                    log.write("SpringArm updated: arm_length=1300, pitch=-48\n")
                elif "StaticMesh" in vname and isinstance(obj, unreal.StaticMeshComponent):
                    obj.set_static_mesh(sk)
                    obj.set_material(0, m_gold)
                    obj.set_material(1, m_coral)
                    obj.set_material(2, m_green if m_green else m_fur)
                    obj.set_material(3, m_dark)
                    obj.set_material(4, m_dark)
                    obj.set_material(5, m_white)
                    obj.set_material(6, m_coral)
                    log.write("StaticMeshComponent materials updated on Blueprint\n")

            unreal.BlueprintEditorLibrary.compile_blueprint(bp)
            unreal.EditorAssetLibrary.save_asset("/Game/Blueprints/Core/BP_GolumoluCharacter")
            log.write("BP_GolumoluCharacter compiled and saved!\n")

        # 3. Update Level M_Maze_31x31
        level_sub = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
        level_sub.load_level("/Game/MomoMaze/Maps/M_Maze_31x31")
        actors = unreal.EditorLevelLibrary.get_all_level_actors()
        for a in actors:
            if isinstance(a, unreal.DirectionalLight):
                comp = a.root_component
                comp.set_mobility(unreal.ComponentMobility.MOVABLE)
                comp.set_editor_property("intensity", 7.0)
                comp.set_editor_property("light_color", unreal.Color(255, 245, 225, 255))
            elif isinstance(a, unreal.SkyLight):
                comp = a.root_component
                comp.set_mobility(unreal.ComponentMobility.MOVABLE)
                comp.set_editor_property("intensity", 2.5)
                comp.set_editor_property("light_color", unreal.Color(180, 220, 255, 255))
        
        world = unreal.EditorLevelLibrary.get_editor_world()
        ws = world.get_world_settings()
        if ws:
            try:
                ws.set_editor_property("b_force_no_precomputed_lighting", True)
                log.write("Set b_force_no_precomputed_lighting on WorldSettings\n")
            except Exception as e:
                log.write(f"WorldSettings note: {e}\n")

        level_sub.save_current_level()
        log.write("Saved M_Maze_31x31!\n")

if __name__ == "__main__":
    assign_materials()
