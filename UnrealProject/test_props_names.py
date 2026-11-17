import unreal

bp_golu = unreal.EditorAssetLibrary.load_asset("/Game/Blueprints/Core/BP_GolumoluCharacter")
subsystem = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
lib = unreal.SubobjectDataBlueprintFunctionLibrary

with open("D:/Projects/MOMO MAZE/UnrealProject/test_props_names.txt", "w") as f:
    handles = subsystem.k2_gather_subobject_data_for_blueprint(bp_golu)
    for h in handles:
        data = subsystem.k2_find_subobject_data_from_handle(h)
        name = lib.get_variable_name(data)
        obj = lib.get_associated_object(data)
        if str(name) == "CharacterMovement":
            f.write(f"CharacterMovement has orient_rotation_to_movement: {hasattr(obj, 'orient_rotation_to_movement')}\n")
            f.write(f"CharacterMovement has b_orient_rotation_to_movement: {hasattr(obj, 'b_orient_rotation_to_movement')}\n")
