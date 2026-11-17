import unreal

mat = unreal.EditorAssetLibrary.load_asset("/Game/Materials/UI/M_UI_Cream")
with open("D:/Projects/MOMO MAZE/UnrealProject/mat_inspect.txt", "w") as f:
    f.write(f"Loaded mat: {mat}\n")
    if mat:
        # Check base color parameter or compile errors
        try:
            num_nodes = len(mat.get_editor_property('material_graph_nodes')) if hasattr(mat, 'material_graph_nodes') else -1
            f.write(f"Material graph nodes: {num_nodes}\n")
        except Exception as e:
            f.write(f"Error checking nodes: {e}\n")
