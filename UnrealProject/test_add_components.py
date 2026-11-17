import unreal

bp_golu = unreal.EditorAssetLibrary.load_asset("/Game/Blueprints/Core/BP_GolumoluCharacter")
subsystem = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)

with open("D:/Projects/MOMO MAZE/UnrealProject/bp_setup_log.txt", "w") as f:
    try:
        handles = subsystem.k2_gather_subobject_data_for_blueprint(bp_golu)
        root_handle = handles[0]
        f.write(f"Root handle: {root_handle}\n")

        # 1. Add SpringArmComponent
        params_arm = unreal.AddNewSubobjectParams()
        params_arm.parent_handle = root_handle
        params_arm.new_class = unreal.SpringArmComponent
        params_arm.blueprint_context = bp_golu
        
        arm_handle, fail = subsystem.add_new_subobject(params_arm)
        f.write(f"Added SpringArm: {arm_handle.is_valid()}, fail: {fail}\n")

        # 2. Add CameraComponent under SpringArm
        params_cam = unreal.AddNewSubobjectParams()
        params_cam.parent_handle = arm_handle
        params_cam.new_class = unreal.CameraComponent
        params_cam.blueprint_context = bp_golu
        
        cam_handle, fail = subsystem.add_new_subobject(params_cam)
        f.write(f"Added Camera: {cam_handle.is_valid()}, fail: {fail}\n")

        # 3. Add StaticMeshComponent for visual Golumolu
        params_mesh = unreal.AddNewSubobjectParams()
        params_mesh.parent_handle = root_handle
        params_mesh.new_class = unreal.StaticMeshComponent
        params_mesh.blueprint_context = bp_golu
        
        mesh_handle, fail = subsystem.add_new_subobject(params_mesh)
        f.write(f"Added StaticMesh: {mesh_handle.is_valid()}, fail: {fail}\n")

        unreal.EditorAssetLibrary.save_asset("/Game/Blueprints/Core/BP_GolumoluCharacter")
        f.write("Saved BP_GolumoluCharacter successfully!\n")

    except Exception as e:
        import traceback
        f.write(f"Error: {e}\n{traceback.format_exc()}")
