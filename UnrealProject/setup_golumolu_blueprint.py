import unreal

bp_golu = unreal.EditorAssetLibrary.load_asset("/Game/Blueprints/Core/BP_GolumoluCharacter")
subsystem = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
lib = unreal.SubobjectDataBlueprintFunctionLibrary

with open("D:/Projects/MOMO MAZE/UnrealProject/bp_golu_setup.txt", "w") as f:
    try:
        handles = subsystem.k2_gather_subobject_data_for_blueprint(bp_golu)
        root_handle = None
        capsule_obj = None
        move_obj = None

        for h in handles:
            data = subsystem.k2_find_subobject_data_from_handle(h)
            name = lib.get_variable_name(data)
            obj = lib.get_associated_object(data)
            if str(name) == "CapsuleComponent":
                root_handle = h
                capsule_obj = obj
            elif str(name) == "CharacterMovement":
                move_obj = obj

        f.write(f"Found root_handle: {root_handle}, capsule: {capsule_obj}, move: {move_obj}\n")

        # Configure Capsule
        if capsule_obj:
            capsule_obj.set_editor_property("capsule_radius", 45.0)
            capsule_obj.set_editor_property("capsule_half_height", 60.0)
            f.write("Configured CapsuleComponent (45r, 60h)\n")

        # Configure Movement
        if move_obj:
            move_obj.set_editor_property("max_walk_speed", 450.0)
            move_obj.set_editor_property("max_acceleration", 1800.0)
            move_obj.set_editor_property("braking_deceleration_walking", 2000.0)
            move_obj.set_editor_property("orient_rotation_to_movement", True)
            f.write("Configured CharacterMovement (speed 450, orient rotation)\n")

        # Add Visual StaticMeshComponent
        params_mesh = unreal.AddNewSubobjectParams()
        params_mesh.parent_handle = root_handle
        params_mesh.new_class = unreal.StaticMeshComponent
        params_mesh.blueprint_context = bp_golu
        
        mesh_handle, fail = subsystem.add_new_subobject(params_mesh)
        f.write(f"Added Golumolu StaticMesh: fail={fail}\n")
        if lib.is_handle_valid(mesh_handle):
            mesh_data = subsystem.k2_find_subobject_data_from_handle(mesh_handle)
            mesh_comp = lib.get_associated_object(mesh_data)
            if mesh_comp:
                sm = unreal.EditorAssetLibrary.load_asset("/Game/Meshes/Characters/SK_Golumolu")
                mat = unreal.EditorAssetLibrary.load_asset("/Game/Materials/Characters/M_Golumolu_Fur")
                mesh_comp.set_static_mesh(sm)
                mesh_comp.set_material(0, mat)
                mesh_comp.set_relative_location(unreal.Vector(0, 0, -55.0), False, False)
                mesh_comp.set_relative_rotation(unreal.Rotator(0, -90.0, 0), False, False)
                mesh_comp.set_relative_scale3d(unreal.Vector(0.55, 0.55, 0.55))
                f.write("Configured Golumolu Mesh Component with SK_Golumolu & M_Golumolu_Fur\n")

        # Add SpringArmComponent
        params_arm = unreal.AddNewSubobjectParams()
        params_arm.parent_handle = root_handle
        params_arm.new_class = unreal.SpringArmComponent
        params_arm.blueprint_context = bp_golu
        
        arm_handle, fail = subsystem.add_new_subobject(params_arm)
        f.write(f"Added SpringArm: fail={fail}\n")
        if lib.is_handle_valid(arm_handle):
            arm_data = subsystem.k2_find_subobject_data_from_handle(arm_handle)
            arm_comp = lib.get_associated_object(arm_data)
            if arm_comp:
                arm_comp.set_editor_property("target_arm_length", 1350.0)
                arm_comp.set_editor_property("do_collision_test", False)
                arm_comp.set_editor_property("inherit_pitch", False)
                arm_comp.set_editor_property("inherit_yaw", False)
                arm_comp.set_editor_property("inherit_roll", False)
                arm_comp.set_relative_rotation(unreal.Rotator(-54.0, 0.0, 0.0), False, False)
                f.write("Configured SpringArm (1350 length, -54 pitch)\n")

            # Add CameraComponent attached to SpringArm
            params_cam = unreal.AddNewSubobjectParams()
            params_cam.parent_handle = arm_handle
            params_cam.new_class = unreal.CameraComponent
            params_cam.blueprint_context = bp_golu
            
            cam_handle, fail = subsystem.add_new_subobject(params_cam)
            f.write(f"Added Camera: fail={fail}\n")
            if lib.is_handle_valid(cam_handle):
                cam_data = subsystem.k2_find_subobject_data_from_handle(cam_handle)
                cam_comp = lib.get_associated_object(cam_data)
                if cam_comp:
                    cam_comp.set_editor_property("field_of_view", 52.0)
                    f.write("Configured Camera (FOV 52)\n")

        # Save Blueprint
        unreal.EditorAssetLibrary.save_asset("/Game/Blueprints/Core/BP_GolumoluCharacter")
        f.write("BP_GolumoluCharacter setup successfully completed and saved!\n")

    except Exception as e:
        import traceback
        f.write(f"Error: {e}\n{traceback.format_exc()}\n")
