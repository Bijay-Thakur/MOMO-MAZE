import unreal

def fix_cream():
    mat_path = "/Game/Materials/UI/M_UI_Cream"
    mat = unreal.EditorAssetLibrary.load_asset(mat_path)
    if mat:
        mat.set_editor_property("two_sided", True)
        unreal.MaterialEditingLibrary.delete_all_material_expressions(mat)
        
        # Base Color
        col_node = unreal.MaterialEditingLibrary.create_material_expression(mat, unreal.MaterialExpressionConstant3Vector, -400, 0)
        col_node.set_editor_property("constant", unreal.LinearColor(1.0, 0.96, 0.91, 1.0)) # Warm Cream
        unreal.MaterialEditingLibrary.connect_material_property(col_node, "", unreal.MaterialProperty.MP_BASE_COLOR)
        
        # Roughness
        rough_node = unreal.MaterialEditingLibrary.create_material_expression(mat, unreal.MaterialExpressionConstant, -400, 150)
        rough_node.set_editor_property("r", 0.40)
        unreal.MaterialEditingLibrary.connect_material_property(rough_node, "", unreal.MaterialProperty.MP_ROUGHNESS)
        
        # Subtle warm emissive to stay luminous on mobile
        emis_node = unreal.MaterialEditingLibrary.create_material_expression(mat, unreal.MaterialExpressionConstant3Vector, -400, 300)
        emis_node.set_editor_property("constant", unreal.LinearColor(0.08, 0.075, 0.07, 1.0))
        unreal.MaterialEditingLibrary.connect_material_property(emis_node, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
        
        unreal.MaterialEditingLibrary.recompile_material(mat)
        unreal.EditorAssetLibrary.save_loaded_asset(mat)
        print("M_UI_Cream successfully recompiled and saved!")
        
    # Also update SM_UI_CardFrame and SM_UI_ButtonSecondary_Pill
    for p in ["/Game/Meshes/UI/SM_UI_CardFrame", "/Game/Meshes/UI/SM_UI_ButtonSecondary_Pill", "/Game/Meshes/UI/SM_UI_LevelNode"]:
        sm = unreal.EditorAssetLibrary.load_asset(p)
        if sm and mat:
            sm.set_material(0, mat)
            unreal.EditorAssetLibrary.save_loaded_asset(sm)
            print(f"Assigned M_UI_Cream to {p}")

if __name__ == "__main__":
    fix_cream()
