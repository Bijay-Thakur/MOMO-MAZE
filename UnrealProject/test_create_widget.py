import unreal

with open("D:/Projects/MOMO MAZE/UnrealProject/test_widget_creation.txt", "w") as f:
    try:
        asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
        factory = unreal.WidgetBlueprintFactory()
        factory.set_editor_property("parent_class", unreal.UserWidget)
        
        pkg_path = "/Game/UI"
        asset_name = "WBP_TestWidget"
        
        # Check if exists
        existing = unreal.EditorAssetLibrary.load_asset(f"{pkg_path}/{asset_name}")
        if existing:
            unreal.EditorAssetLibrary.delete_asset(f"{pkg_path}/{asset_name}")
            
        widget_bp = asset_tools.create_asset(asset_name, pkg_path, unreal.WidgetBlueprint, factory)
        f.write(f"Created WidgetBlueprint: {widget_bp}\n")
        
        # Check widget_tree
        tree = widget_bp.get_editor_property("widget_tree")
        f.write(f"WidgetTree: {tree}\n")
        f.write(f"Root widget: {tree.get_editor_property('root_widget')}\n")
        
        # Create root canvas
        root_canvas = unreal.WidgetTree.construct_widget(unreal.CanvasPanel, tree) if hasattr(unreal.WidgetTree, 'construct_widget') else None
        f.write(f"Constructed canvas: {root_canvas}\n")
        
        unreal.EditorAssetLibrary.save_asset(f"{pkg_path}/{asset_name}")
        f.write("Saved successfully!\n")
    except Exception as e:
        import traceback
        f.write(f"Error: {e}\n{traceback.format_exc()}\n")
