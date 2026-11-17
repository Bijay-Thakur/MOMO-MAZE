import unreal

bp_ghost = unreal.EditorAssetLibrary.load_asset("/Game/Blueprints/Core/BP_SpiritCharacter")
subsystem = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
lib = unreal.SubobjectDataBlueprintFunctionLibrary

with open("D:/Projects/MOMO MAZE/UnrealProject/bp_ghost_setup.txt", "w") as f:
    try:
        handles = subsystem.k2_gather_subobject_data_for_blueprint(bp_ghost)
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
            capsule_obj.set_editor_property("capsule_radius", 35.0)
            capsule_obj.set_editor_property("capsule_half_height", 50.0)
            f.write("Configured Ghost CapsuleComponent (35r, 50h)\n")

        # Configure Movement
        if move_obj:
            move_obj.set_editor_property("max_walk_speed", 330.0)
            move_obj.set_editor_property("max_acceleration", 1200.0)
            move_obj.set_editor_property("braking_deceleration_walking", 1500.0)
            move_obj.set_editor_property("orient_rotation_to_movement", True)
            f.write("Configured Ghost Movement (speed 330)\n")

        # Add Visual StaticMeshComponent
        params_mesh = unreal.AddNewSubobjectParams()
        params_mesh.parent_handle = root_handle
        params_mesh.new_class = unreal.StaticMeshComponent
        params_mesh.blueprint_context = bp_ghost
        
        mesh_handle, fail = subsystem.add_new_subobject(params_mesh)
        f.write(f"Added Ghost StaticMesh: fail={fail}\n")
        if lib.is_handle_valid(mesh_handle):
            mesh_data = subsystem.k2_find_subobject_data_from_handle(mesh_handle)
            mesh_comp = lib.get_associated_object(mesh_data)
            if mesh_comp:
                sm = unreal.EditorAssetLibrary.load_asset("/Game/Meshes/Characters/SK_Ghost_Follower")
                mat = unreal.EditorAssetLibrary.load_asset("/Game/Materials/Characters/M_Ghost_Master")
                mesh_comp.set_static_mesh(sm)
                mesh_comp.set_material(0, mat)
                mesh_comp.set_relative_location(unreal.Vector(0, 0, -30.0), False, False)
                mesh_comp.set_relative_rotation(unreal.Rotator(0, -90.0, 0), False, False)
                mesh_comp.set_relative_scale3d(unreal.Vector(0.5, 0.5, 0.5))
                f.write("Configured Ghost Mesh Component with SK_Ghost_Follower & M_Ghost_Master\n")

        # Save Blueprint
        unreal.EditorAssetLibrary.save_asset("/Game/Blueprints/Core/BP_SpiritCharacter")
        f.write("BP_SpiritCharacter setup successfully completed and saved!\n")

    except Exception as e:
        import traceback
        f.write(f"Error: {e}\n{traceback.format_exc()}\n")
