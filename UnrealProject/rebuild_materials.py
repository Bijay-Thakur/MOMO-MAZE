import unreal

def configure_material(asset_path, base_color, roughness=0.35, emissive_color=None, emissive_strength=0.0):
    package_name, asset_name = asset_path.rsplit("/", 1)
    
    mat = unreal.EditorAssetLibrary.load_asset(asset_path)
    if not mat:
        asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
        mat_factory = unreal.MaterialFactoryNew()
        mat = asset_tools.create_asset(asset_name, package_name, unreal.Material, mat_factory)
        
    if not mat:
        print(f"Failed to obtain material {asset_path}")
        return None
        
    mat.set_editor_property("two_sided", True)
    
    # Clean previous expressions
    unreal.MaterialEditingLibrary.delete_all_material_expressions(mat)
    
    # 1. Base Color
    col_node = unreal.MaterialEditingLibrary.create_material_expression(mat, unreal.MaterialExpressionConstant3Vector, -400, 0)
    col_node.set_editor_property("constant", unreal.LinearColor(base_color[0], base_color[1], base_color[2], 1.0))
    unreal.MaterialEditingLibrary.connect_material_property(col_node, "", unreal.MaterialProperty.MP_BASE_COLOR)
    
    # 2. Roughness
    rough_node = unreal.MaterialEditingLibrary.create_material_expression(mat, unreal.MaterialExpressionConstant, -400, 150)
    rough_node.set_editor_property("r", roughness)
    unreal.MaterialEditingLibrary.connect_material_property(rough_node, "", unreal.MaterialProperty.MP_ROUGHNESS)
    
    # 3. Emissive
    if emissive_color and emissive_strength > 0.0:
        emis_node = unreal.MaterialEditingLibrary.create_material_expression(mat, unreal.MaterialExpressionConstant3Vector, -400, 300)
        emis_node.set_editor_property("constant", unreal.LinearColor(
            emissive_color[0] * emissive_strength,
            emissive_color[1] * emissive_strength,
            emissive_color[2] * emissive_strength,
            1.0
        ))
        unreal.MaterialEditingLibrary.connect_material_property(emis_node, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
        
    unreal.MaterialEditingLibrary.recompile_material(mat)
    unreal.EditorAssetLibrary.save_loaded_asset(mat)
    print(f"Configured & saved: {asset_path}")
    return mat

def main():
    mats = {
        "/Game/Materials/UI/M_UI_Gold": ((1.0, 0.78, 0.28), 0.25, (1.0, 0.8, 0.3), 0.25),
        "/Game/Materials/UI/M_UI_Cream": ((1.0, 0.96, 0.91), 0.40, (1.0, 0.95, 0.9), 0.05),
        "/Game/Materials/UI/M_UI_ToastBrown": ((0.35, 0.18, 0.09), 0.35, None, 0.0),
        "/Game/Materials/UI/M_UI_Orange": ((0.96, 0.55, 0.20), 0.30, (0.96, 0.55, 0.2), 0.15),
        "/Game/Materials/UI/M_UI_LeafGreen": ((0.45, 0.72, 0.20), 0.40, (0.45, 0.72, 0.2), 0.05),
        "/Game/Materials/UI/M_UI_CoralHeart": ((0.95, 0.35, 0.40), 0.25, (0.95, 0.35, 0.4), 0.2),
        "/Game/Materials/UI/M_UI_SpiritWhite": ((1.0, 0.99, 0.96), 0.20, (1.0, 0.98, 0.95), 0.35),
        "/Game/Materials/Environment/M_Hedge_Foliage": ((0.35, 0.65, 0.22), 0.45, (0.35, 0.65, 0.22), 0.08),
        "/Game/Materials/Environment/M_Grass_Path": ((0.62, 0.78, 0.32), 0.55, (0.62, 0.78, 0.32), 0.08),
        "/Game/Materials/Environment/M_Leaf_Gate": ((0.78, 0.55, 0.35), 0.40, (1.0, 0.8, 0.2), 0.2),
        "/Game/Materials/Environment/M_Momo_Dough": ((1.0, 0.95, 0.88), 0.30, (1.0, 0.85, 0.4), 0.25),
        "/Game/Materials/Characters/M_Golumolu_Fur": ((1.0, 0.85, 0.70), 0.45, (1.0, 0.85, 0.7), 0.05),
        "/Game/Materials/Characters/M_Ghost_Master": ((1.0, 0.98, 0.95), 0.15, (1.0, 0.95, 0.88), 0.45)
    }
    
    for path, (base, rough, emis_col, emis_str) in mats.items():
        configure_material(path, base, rough, emis_col, emis_str)

    # Re-assign default materials to static meshes
    mesh_material_mapping = {
        "/Game/Meshes/UI/SM_UI_ButtonPrimary_Pill": "/Game/Materials/UI/M_UI_Gold",
        "/Game/Meshes/UI/SM_UI_ButtonSecondary_Pill": "/Game/Materials/UI/M_UI_Cream",
        "/Game/Meshes/UI/SM_UI_ButtonIcon": "/Game/Materials/UI/M_UI_Cream",
        "/Game/Meshes/UI/SM_UI_Tab_Pill": "/Game/Materials/UI/M_UI_Cream",
        "/Game/Meshes/UI/SM_UI_ChoiceChip": "/Game/Materials/UI/M_UI_Cream",
        "/Game/Meshes/UI/SM_UI_LevelNode": "/Game/Materials/UI/M_UI_Cream",
        "/Game/Meshes/UI/SM_UI_ToggleTrack": "/Game/Materials/UI/M_UI_ToastBrown",
        "/Game/Meshes/UI/SM_UI_ToggleKnob": "/Game/Materials/UI/M_UI_Gold",
        "/Game/Meshes/UI/SM_UI_SliderTrack": "/Game/Materials/UI/M_UI_ToastBrown",
        "/Game/Meshes/UI/SM_UI_SliderKnob": "/Game/Materials/UI/M_UI_Gold",
        "/Game/Meshes/UI/SM_UI_CardFrame": "/Game/Materials/UI/M_UI_Cream",
        "/Game/Meshes/UI/SM_UI_HeaderRibbon": "/Game/Materials/UI/M_UI_ToastBrown",
        "/Game/Meshes/UI/SM_UI_LeafPair": "/Game/Materials/UI/M_UI_LeafGreen",
        "/Game/Meshes/UI/SM_UI_FlowerCorner": "/Game/Materials/UI/M_UI_SpiritWhite",
        "/Game/Meshes/UI/SM_UI_Star": "/Game/Materials/UI/M_UI_Gold",
        "/Game/Meshes/UI/SM_UI_Heart": "/Game/Materials/UI/M_UI_CoralHeart",
        "/Game/Meshes/UI/SM_UI_PauseIcon": "/Game/Materials/UI/M_UI_ToastBrown",
        "/Game/Meshes/UI/SM_UI_MapIcon": "/Game/Materials/UI/M_UI_Gold",
        "/Game/Meshes/UI/SM_UI_MomoIcon": "/Game/Materials/Environment/M_Momo_Dough",
        "/Game/Meshes/UI/SM_UI_SpiritIcon": "/Game/Materials/Characters/M_Ghost_Master",
        "/Game/Meshes/Environment/SM_Hedge_Straight": "/Game/Materials/Environment/M_Hedge_Foliage",
        "/Game/Meshes/Environment/SM_Hedge_Corner": "/Game/Materials/Environment/M_Hedge_Foliage",
        "/Game/Meshes/Environment/SM_Path_Tile": "/Game/Materials/Environment/M_Grass_Path",
        "/Game/Meshes/Environment/SM_Leaf_Gate": "/Game/Materials/Environment/M_Leaf_Gate",
        "/Game/Meshes/Environment/SM_Momo_Collectible": "/Game/Materials/Environment/M_Momo_Dough",
        "/Game/Meshes/Characters/SK_Golumolu": "/Game/Materials/Characters/M_Golumolu_Fur",
        "/Game/Meshes/Characters/SK_Ghost_Follower": "/Game/Materials/Characters/M_Ghost_Master",
        "/Game/Meshes/Characters/SK_Ghost_Cutter": "/Game/Materials/Characters/M_Ghost_Master",
        "/Game/Meshes/Characters/SK_Ghost_Wanderer": "/Game/Materials/Characters/M_Ghost_Master"
    }

    for mesh_path, mat_path in mesh_material_mapping.items():
        mesh = unreal.EditorAssetLibrary.load_asset(mesh_path)
        mat = unreal.EditorAssetLibrary.load_asset(mat_path)
        if mesh and mat:
            mesh.set_material(0, mat)
            unreal.EditorAssetLibrary.save_loaded_asset(mesh)

    print("All materials and meshes successfully configured and saved!")

if __name__ == "__main__":
    main()
