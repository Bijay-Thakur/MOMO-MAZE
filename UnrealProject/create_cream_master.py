import unreal

def create_cream_master():
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    mat_factory = unreal.MaterialFactoryNew()
    mat = asset_tools.create_asset("M_UI_Cream_Master", "/Game/Materials/UI", unreal.Material, mat_factory)
    if not mat:
        print("Failed to create M_UI_Cream_Master")
        return
        
    mat.set_editor_property("two_sided", True)
    
    col_node = unreal.MaterialEditingLibrary.create_material_expression(mat, unreal.MaterialExpressionConstant3Vector, -400, 0)
    col_node.set_editor_property("constant", unreal.LinearColor(1.0, 0.96, 0.91, 1.0)) # Warm Cream
    unreal.MaterialEditingLibrary.connect_material_property(col_node, "", unreal.MaterialProperty.MP_BASE_COLOR)
    
    rough_node = unreal.MaterialEditingLibrary.create_material_expression(mat, unreal.MaterialExpressionConstant, -400, 150)
    rough_node.set_editor_property("r", 0.40)
    unreal.MaterialEditingLibrary.connect_material_property(rough_node, "", unreal.MaterialProperty.MP_ROUGHNESS)
    
    emis_node = unreal.MaterialEditingLibrary.create_material_expression(mat, unreal.MaterialExpressionConstant3Vector, -400, 300)
    emis_node.set_editor_property("constant", unreal.LinearColor(0.12, 0.11, 0.10, 1.0)) # luminous on mobile
    unreal.MaterialEditingLibrary.connect_material_property(emis_node, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    
    unreal.MaterialEditingLibrary.recompile_material(mat)
    unreal.EditorAssetLibrary.save_loaded_asset(mat)
    print("M_UI_Cream_Master successfully compiled and saved!")
    
    for p in ["/Game/Meshes/UI/SM_UI_CardFrame", "/Game/Meshes/UI/SM_UI_ButtonSecondary_Pill", "/Game/Meshes/UI/SM_UI_LevelNode", "/Game/Meshes/UI/SM_UI_ChoiceChip", "/Game/Meshes/UI/SM_UI_Tab_Pill"]:
        sm = unreal.EditorAssetLibrary.load_asset(p)
        if sm:
            sm.set_material(0, mat)
            unreal.EditorAssetLibrary.save_loaded_asset(sm)
            print(f"Assigned M_UI_Cream_Master to {p}")

if __name__ == "__main__":
    create_cream_master()
