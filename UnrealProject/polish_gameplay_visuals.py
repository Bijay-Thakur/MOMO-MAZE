import unreal

def polish_visuals():
    log_file = "D:/Projects/MOMO MAZE/UnrealProject/polish_log.txt"
    with open(log_file, "w", encoding="utf-8") as log:
        log.write("=== Polishing Gameplay Visuals for Mobile ===\n")
        
        # 1. Create or ensure materials for Golumolu's 7 slots
        asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
        
        palette = {
            "M_Golumolu_Peach_Accent": (0.95, 0.72, 0.50),
            "M_Golumolu_Cheeks": (0.95, 0.40, 0.45),
            "M_Golumolu_Fluffy_Fur": (0.32, 0.72, 0.28),   # Vibrant dino green
            "M_Golumolu_Eyes": (0.05, 0.04, 0.04),
            "M_Golumolu_Mouth": (0.35, 0.12, 0.12),
            "M_Golumolu_Eye_Shine": (1.0, 1.0, 1.0),
            "M_Golumolu_Tongue": (0.95, 0.45, 0.48)
        }
        
        created_mats = {}
        for mat_name, (r, g, b) in palette.items():
            mat_path = f"/Game/Materials/Characters/{mat_name}"
            mat = unreal.EditorAssetLibrary.load_asset(mat_path)
            if not mat:
                mat_factory = unreal.MaterialFactoryNew()
                mat = asset_tools.create_asset(mat_name, "/Game/Materials/Characters", unreal.Material, mat_factory)
                
            color_node = unreal.MaterialEditingLibrary.create_material_expression(mat, unreal.MaterialExpressionVectorParameter, -400, 0)
            color_node.parameter_name = "BaseColor"
            color_node.default_value = unreal.LinearColor(r, g, b, 1.0)
            unreal.MaterialEditingLibrary.connect_material_property(color_node, "", unreal.MaterialProperty.MP_BASE_COLOR)
            
            rough_node = unreal.MaterialEditingLibrary.create_material_expression(mat, unreal.MaterialExpressionScalarParameter, -400, 200)
            rough_node.parameter_name = "Roughness"
            rough_node.default_value = 0.3 if "Eyes" in mat_name or "Shine" in mat_name else 0.6
            unreal.MaterialEditingLibrary.connect_material_property(rough_node, "", unreal.MaterialProperty.MP_ROUGHNESS)
            
            unreal.MaterialEditingLibrary.update_material(mat)
            unreal.EditorAssetLibrary.save_asset(mat_path)
            created_mats[mat_name] = mat
            log.write(f"Material ready: {mat_name} (RGB: {r:.2f}, {g:.2f}, {b:.2f})\n")

        # 2. Assign materials to SK_Golumolu StaticMesh slots
        sk_golumolu = unreal.EditorAssetLibrary.load_asset("/Game/Meshes/Characters/SK_Golumolu")
        if sk_golumolu:
            slot_names = [
                "M_Golumolu_Peach_Accent",
                "M_Golumolu_Cheeks",
                "M_Golumolu_Fluffy_Fur",
                "M_Golumolu_Eyes",
                "M_Golumolu_Mouth",
                "M_Golumolu_Eye_Shine",
                "M_Golumolu_Tongue"
            ]
            for i, sname in enumerate(slot_names):
                if sname in created_mats:
                    sk_golumolu.set_material(i, created_mats[sname])
                    log.write(f"Set SK_Golumolu slot {i} ({sname})\n")
            unreal.EditorAssetLibrary.save_asset("/Game/Meshes/Characters/SK_Golumolu")

        # 3. Update BP_GolumoluCharacter
        bp_path = "/Game/Blueprints/Core/BP_GolumoluCharacter"
        bp = unreal.EditorAssetLibrary.load_asset(bp_path)
        if bp:
            subsystem = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
            lib = unreal.SubobjectDataBlueprintFunctionLibrary
            handles = subsystem.k2_gather_subobject_data_for_blueprint(bp)
            
            for h in handles:
                data = subsystem.k2_find_subobject_data_from_handle(h)
                vname = str(lib.get_variable_name(data))
                obj = lib.get_associated_object(data)
                if "SpringArm" in vname and isinstance(obj, unreal.SpringArmComponent):
                    obj.set_editor_property("target_arm_length", 1350.0)
                    obj.set_editor_property("target_offset", unreal.Vector(0.0, 0.0, 100.0))
                    obj.set_relative_rotation(unreal.Rotator(-48.0, 0.0, 0.0), False, False)
                    log.write("SpringArm updated: arm_length=1350, pitch=-48, offset_z=100\n")
                elif "StaticMesh" in vname and isinstance(obj, unreal.StaticMeshComponent):
                    obj.set_static_mesh(sk_golumolu)
                    for i, sname in enumerate(slot_names):
                        if sname in created_mats:
                            obj.set_material(i, created_mats[sname])
                    log.write("StaticMeshComponent materials updated on BP\n")

            unreal.BlueprintEditorLibrary.compile_blueprint(bp)
            unreal.EditorAssetLibrary.save_asset(bp_path)
            log.write("BP_GolumoluCharacter recompiled and saved.\n")

        # 4. Polish Level M_Maze_31x31
        level_subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
        level_subsystem.load_level("/Game/MomoMaze/Maps/M_Maze_31x31")
        world = unreal.EditorLevelLibrary.get_editor_world()
        
        # World Settings: Force No Precomputed Lighting to eliminate the red text
        ws = world.get_world_settings()
        if ws:
            try:
                ws.set_editor_property("b_force_no_precomputed_lighting", True)
                log.write("Set b_force_no_precomputed_lighting = True on WorldSettings\n")
            except Exception as e:
                log.write(f"Note on world settings: {e}\n")

        actors = unreal.EditorLevelLibrary.get_all_level_actors()
        for a in actors:
            if isinstance(a, unreal.DirectionalLight):
                comp = a.root_component
                comp.set_mobility(unreal.ComponentMobility.MOVABLE)
                comp.set_editor_property("intensity", 7.0)
                comp.set_editor_property("light_color", unreal.Color(255, 245, 220, 255))
                log.write(f"Configured DirectionalLight: {a.get_name()} Movable, intensity=7.0\n")
            elif isinstance(a, unreal.SkyLight):
                comp = a.root_component
                comp.set_mobility(unreal.ComponentMobility.MOVABLE)
                comp.set_editor_property("intensity", 2.5)
                comp.set_editor_property("light_color", unreal.Color(180, 215, 255, 255))
                log.write(f"Configured SkyLight: {a.get_name()} Movable, intensity=2.5\n")

        level_subsystem.save_current_level()
        log.write("Level M_Maze_31x31 saved with polished dynamic lighting!\n")

if __name__ == "__main__":
    polish_visuals()
