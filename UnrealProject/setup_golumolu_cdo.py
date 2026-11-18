import unreal

def configure_golumolu():
    log_file = "D:/Projects/MOMO MAZE/UnrealProject/golumolu_setup_log.txt"
    with open(log_file, "w", encoding="utf-8") as log:
        log.write("=== Configuring BP_GolumoluCharacter ===\n")
        
        bp_path = "/Game/Blueprints/Core/BP_GolumoluCharacter"
        bp = unreal.EditorAssetLibrary.load_asset(bp_path)
        if not bp:
            log.write(f"Error: {bp_path} not found\n")
            return
            
        subsystem = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
        lib = unreal.SubobjectDataBlueprintFunctionLibrary
        
        handles = subsystem.k2_gather_subobject_data_for_blueprint(bp)
        log.write(f"Initial handles count: {len(handles)}\n")
        
        root_handle = None
        existing_spring_arm = None
        existing_camera = None
        existing_visual = None
        
        for h in handles:
            data = subsystem.k2_find_subobject_data_from_handle(h)
            vname = str(lib.get_variable_name(data))
            obj = lib.get_associated_object(data)
            log.write(f"Handle: {vname} -> {obj}\n")
            if vname == "CapsuleComponent" or "Capsule" in vname:
                root_handle = h
            elif "SpringArm" in vname:
                existing_spring_arm = h
            elif "Camera" in vname:
                existing_camera = h
            elif "GolumoluVisual" in vname or "Visual" in vname:
                existing_visual = h
                
        if not root_handle:
            root_handle = handles[0]
            log.write(f"Using handles[0] as root_handle: {root_handle}\n")

        # 1. SpringArm
        arm_handle = existing_spring_arm
        if not arm_handle:
            params_arm = unreal.AddNewSubobjectParams()
            params_arm.parent_handle = root_handle
            params_arm.new_class = unreal.SpringArmComponent
            params_arm.blueprint_context = bp
            arm_handle, fail = subsystem.add_new_subobject(params_arm)
            log.write(f"Added new SpringArmComponent: fail={fail}\n")
            if lib.is_handle_valid(arm_handle):
                subsystem.rename_subobject(arm_handle, "SpringArm")

        if arm_handle and lib.is_handle_valid(arm_handle):
            data = subsystem.k2_find_subobject_data_from_handle(arm_handle)
            comp = lib.get_associated_object(data)
            if comp:
                comp.set_editor_property("target_arm_length", 1100.0)
                comp.set_editor_property("do_collision_test", False)
                comp.set_editor_property("inherit_pitch", False)
                comp.set_editor_property("inherit_yaw", False)
                comp.set_editor_property("inherit_roll", False)
                comp.set_relative_rotation(unreal.Rotator(-55.0, 0.0, 0.0), False, False)
                log.write("Configured SpringArm: length=1100, pitch=-55\n")

        # 2. Camera
        cam_handle = existing_camera
        if not cam_handle:
            params_cam = unreal.AddNewSubobjectParams()
            params_cam.parent_handle = arm_handle
            params_cam.new_class = unreal.CameraComponent
            params_cam.blueprint_context = bp
            cam_handle, fail = subsystem.add_new_subobject(params_cam)
            log.write(f"Added new CameraComponent: fail={fail}\n")
            if lib.is_handle_valid(cam_handle):
                subsystem.rename_subobject(cam_handle, "Camera")

        if cam_handle and lib.is_handle_valid(cam_handle):
            data = subsystem.k2_find_subobject_data_from_handle(cam_handle)
            comp = lib.get_associated_object(data)
            if comp:
                comp.set_editor_property("field_of_view", 60.0)
                log.write("Configured CameraComponent FOV=60\n")

        # 3. Visual StaticMeshComponent
        mesh_handle = existing_visual
        if not mesh_handle:
            params_sm = unreal.AddNewSubobjectParams()
            params_sm.parent_handle = root_handle
            params_sm.new_class = unreal.StaticMeshComponent
            params_sm.blueprint_context = bp
            mesh_handle, fail = subsystem.add_new_subobject(params_sm)
            log.write(f"Added new StaticMeshComponent: fail={fail}\n")
            if lib.is_handle_valid(mesh_handle):
                subsystem.rename_subobject(mesh_handle, "GolumoluVisual")

        if mesh_handle and lib.is_handle_valid(mesh_handle):
            data = subsystem.k2_find_subobject_data_from_handle(mesh_handle)
            comp = lib.get_associated_object(data)
            if comp:
                sm = unreal.EditorAssetLibrary.load_asset("/Game/Meshes/Characters/SK_Golumolu")
                mat = unreal.EditorAssetLibrary.load_asset("/Game/Materials/Characters/M_Golumolu_Fur")
                if sm:
                    comp.set_static_mesh(sm)
                if mat:
                    comp.set_material(0, mat)
                comp.set_relative_location(unreal.Vector(0.0, 0.0, -45.0), False, False)
                comp.set_relative_scale3d(unreal.Vector(0.55, 0.55, 0.55))
                log.write("Configured GolumoluVisual static mesh and material\n")

        # 4. Compile and Save Blueprint
        unreal.BlueprintEditorLibrary.compile_blueprint(bp)
        log.write("Compiled Blueprint via unreal.BlueprintEditorLibrary.compile_blueprint\n")
        
        saved = unreal.EditorAssetLibrary.save_asset(bp_path)
        log.write(f"Saved asset: {saved}\n")

        # 5. Verification on CDO
        cdo = unreal.get_default_object(bp.generated_class())
        comps = cdo.get_components_by_class(unreal.ActorComponent)
        comp_names = [c.get_name() for c in comps]
        log.write(f"Verification CDO components: {comp_names}\n")

if __name__ == "__main__":
    configure_golumolu()
