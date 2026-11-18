import unreal

def configure_golumolu():
    bp_path = "/Game/Blueprints/Core/BP_GolumoluCharacter"
    bp = unreal.EditorAssetLibrary.load_asset(bp_path)
    if not bp:
        print(f"Error: {bp_path} not found")
        return False
        
    subsystem = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
    lib = unreal.SubobjectDataBlueprintFunctionLibrary
    
    handles = subsystem.k2_gather_subobject_data_for_blueprint(bp)
    print(f"Initial handles count: {len(handles)}")
    
    root_handle = None
    char_mesh_handle = None
    for h in handles:
        data = subsystem.k2_find_subobject_data_from_handle(h)
        name = str(lib.get_variable_name(data))
        obj = lib.get_associated_object(data)
        print(f"Handle: {name} -> {obj}")
        if name == "CapsuleComponent":
            root_handle = h
        elif name == "CharacterMesh0":
            char_mesh_handle = h

    # 1. Setup SkeletalMesh or StaticMesh on Golumolu
    mesh_asset = unreal.EditorAssetLibrary.load_asset("/Game/Meshes/Characters/SK_Golumolu")
    mat_asset = unreal.EditorAssetLibrary.load_asset("/Game/Materials/Characters/M_Golumolu_Fur")
    
    # Check if SpringArm already exists
    arm_handle = None
    for h in handles:
        data = subsystem.k2_find_subobject_data_from_handle(h)
        if "SpringArm" in str(lib.get_variable_name(data)):
            arm_handle = h
            break
            
    if not arm_handle and root_handle:
        params_arm = unreal.AddNewSubobjectParams()
        params_arm.parent_handle = root_handle
        params_arm.new_class = unreal.SpringArmComponent
        params_arm.blueprint_context = bp
        arm_handle, fail = subsystem.add_new_subobject(params_arm)
        print(f"Added SpringArm: fail={fail}")
        
    if arm_handle and lib.is_handle_valid(arm_handle):
        arm_data = subsystem.k2_find_subobject_data_from_handle(arm_handle)
        arm_comp = lib.get_associated_object(arm_data)
        if arm_comp:
            arm_comp.set_editor_property("target_arm_length", 1200.0)
            arm_comp.set_editor_property("do_collision_test", False)
            arm_comp.set_editor_property("inherit_pitch", False)
            arm_comp.set_editor_property("inherit_yaw", False)
            arm_comp.set_editor_property("inherit_roll", False)
            arm_comp.set_relative_rotation(unreal.Rotator(-55.0, 0.0, 0.0), False, False)
            print("Configured SpringArm: length=1200, pitch=-55")
            
        # Add Camera attached to SpringArm
        cam_handle = None
        for h in subsystem.k2_gather_subobject_data_for_blueprint(bp):
            data = subsystem.k2_find_subobject_data_from_handle(h)
            if "Camera" in str(lib.get_variable_name(data)):
                cam_handle = h
                break
        if not cam_handle:
            params_cam = unreal.AddNewSubobjectParams()
            params_cam.parent_handle = arm_handle
            params_cam.new_class = unreal.CameraComponent
            params_cam.blueprint_context = bp
            cam_handle, fail = subsystem.add_new_subobject(params_cam)
            print(f"Added Camera: fail={fail}")
            
        if cam_handle and lib.is_handle_valid(cam_handle):
            cam_data = subsystem.k2_find_subobject_data_from_handle(cam_handle)
            cam_comp = lib.get_associated_object(cam_data)
            if cam_comp:
                cam_comp.set_editor_property("field_of_view", 55.0)
                print("Configured CameraComponent FOV=55")

    # Add visual mesh if CharacterMesh0 is skeletal mesh or add a static mesh
    mesh_handle = None
    for h in subsystem.k2_gather_subobject_data_for_blueprint(bp):
        data = subsystem.k2_find_subobject_data_from_handle(h)
        if str(lib.get_variable_name(data)) == "GolumoluVisual":
            mesh_handle = h
            break
            
    if not mesh_handle and root_handle:
        params_sm = unreal.AddNewSubobjectParams()
        params_sm.parent_handle = root_handle
        params_sm.new_class = unreal.StaticMeshComponent
        params_sm.blueprint_context = bp
        mesh_handle, fail = subsystem.add_new_subobject(params_sm)
        if lib.is_handle_valid(mesh_handle):
            subsystem.rename_subobject(mesh_handle, "GolumoluVisual")
            
    if mesh_handle and lib.is_handle_valid(mesh_handle):
        m_data = subsystem.k2_find_subobject_data_from_handle(mesh_handle)
        m_comp = lib.get_associated_object(m_data)
        if m_comp:
            sm = unreal.EditorAssetLibrary.load_asset("/Game/Meshes/Characters/SK_Golumolu")
            mat = unreal.EditorAssetLibrary.load_asset("/Game/Materials/Characters/M_Golumolu_Fur")
            m_comp.set_static_mesh(sm)
            if mat:
                m_comp.set_material(0, mat)
            m_comp.set_relative_location(unreal.Vector(0, 0, -45.0), False, False)
            m_comp.set_relative_scale3d(unreal.Vector(0.55, 0.55, 0.55))
            print("Configured GolumoluVisual static mesh component")

    # Compile Blueprint!
    unreal.KismetCompilerLibrary.compile_blueprint(bp)
    unreal.EditorAssetLibrary.save_asset(bp_path)
    print("SUCCESS: BP_GolumoluCharacter compiled and saved!")

if __name__ == "__main__":
    configure_golumolu()
