import unreal

with open("D:/Projects/MOMO MAZE/UnrealProject/mat_test_log.txt", "w") as f:
    try:
        mat_path = "/Game/Materials/UI/M_TestLit"
        asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
        mat_factory = unreal.MaterialFactoryNew()
        mat = asset_tools.create_asset("M_TestLit", "/Game/Materials/UI", unreal.Material, mat_factory)
        
        # Test Constant3Vector expression
        node = unreal.MaterialEditingLibrary.create_material_expression(mat, unreal.MaterialExpressionConstant3Vector, -300, 0)
        node.set_editor_property("constant", unreal.LinearColor(1.0, 0.96, 0.91, 1.0))
        
        # Connect to BaseColor
        success = unreal.MaterialEditingLibrary.connect_material_property(node, "", unreal.MaterialProperty.MP_BASE_COLOR)
        f.write(f"Connected BaseColor: {success}\n")
        
        # Set Shading Model to DefaultLit or Unlit
        mat.set_editor_property("two_sided", True)
        
        unreal.MaterialEditingLibrary.update_material(mat)
        unreal.EditorAssetLibrary.save_asset(mat_path)
        f.write("Saved test material successfully!\n")
    except Exception as e:
        import traceback
        f.write(f"Error: {e}\n{traceback.format_exc()}\n")
