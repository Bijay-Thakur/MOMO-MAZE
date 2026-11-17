import unreal

def create_material(asset_path, base_color, roughness=0.3, metallic=0.0, specular=0.5, emissive_color=(0.0, 0.0, 0.0), emissive_intensity=0.0):
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    package_name, asset_name = asset_path.rsplit("/", 1)
    
    # Create Material
    mat_factory = unreal.MaterialFactoryNew()
    mat = asset_tools.create_asset(asset_name, package_name, unreal.Material, mat_factory)
    
    # In UE5 Python, we can set material expressions or basic material properties
    # Set standard material attributes via material editing library if available
    try:
        # Base Color
        color_node = unreal.MaterialEditingLibrary.create_material_expression(mat, unreal.MaterialExpressionVectorParameter, -400, 0)
        color_node.parameter_name = "BaseColor"
        color_node.default_value = unreal.LinearColor(base_color[0], base_color[1], base_color[2], 1.0)
        unreal.MaterialEditingLibrary.connect_material_property(color_node, "", unreal.MaterialProperty.MP_BASE_COLOR)
        
        # Roughness
        rough_node = unreal.MaterialEditingLibrary.create_material_expression(mat, unreal.MaterialExpressionScalarParameter, -400, 200)
        rough_node.parameter_name = "Roughness"
        rough_node.default_value = roughness
        unreal.MaterialEditingLibrary.connect_material_property(rough_node, "", unreal.MaterialProperty.MP_ROUGHNESS)
        
        # Emissive
        if emissive_intensity > 0.0:
            emis_node = unreal.MaterialEditingLibrary.create_material_expression(mat, unreal.MaterialExpressionVectorParameter, -400, 400)
            emis_node.parameter_name = "EmissiveColor"
            emis_node.default_value = unreal.LinearColor(emissive_color[0] * emissive_intensity, emissive_color[1] * emissive_intensity, emissive_color[2] * emissive_intensity, 1.0)
            unreal.MaterialEditingLibrary.connect_material_property(emis_node, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
            
        unreal.MaterialEditingLibrary.update_material(mat)
    except Exception as e:
        print(f"Note on expression setup for {asset_name}: {e}")
        
    unreal.EditorAssetLibrary.save_asset(asset_path)
    print(f"Created material: {asset_path}")
    return mat

def build_materials():
    # 1. UI Materials
    mats = {
        "/Game/Materials/UI/M_UI_Gold": ((1.0, 0.78, 0.28), 0.22, 0.0, 0.5, (1.0, 0.75, 0.25), 0.2), # #FFC747
        "/Game/Materials/UI/M_UI_Cream": ((1.0, 0.96, 0.91), 0.38, 0.0, 0.5, (0.0, 0.0, 0.0), 0.0), # #FFF5E8
        "/Game/Materials/UI/M_UI_ToastBrown": ((0.35, 0.18, 0.09), 0.35, 0.0, 0.5, (0.0, 0.0, 0.0), 0.0), # #5A2E17
        "/Game/Materials/UI/M_UI_Orange": ((0.96, 0.55, 0.20), 0.28, 0.0, 0.5, (0.96, 0.55, 0.20), 0.1), # #F58C33
        "/Game/Materials/UI/M_UI_LeafGreen": ((0.45, 0.72, 0.20), 0.40, 0.0, 0.5, (0.0, 0.0, 0.0), 0.0), # #73B833
        "/Game/Materials/UI/M_UI_CoralHeart": ((0.95, 0.35, 0.40), 0.25, 0.0, 0.5, (0.95, 0.35, 0.40), 0.15), # #F25966
        "/Game/Materials/UI/M_UI_SpiritWhite": ((1.0, 0.99, 0.96), 0.20, 0.0, 0.5, (1.0, 0.98, 0.95), 0.3), # Glow white
        # Environment & Characters
        "/Game/Materials/Environment/M_Hedge_Foliage": ((0.35, 0.65, 0.22), 0.45, 0.0, 0.4, (0.0, 0.0, 0.0), 0.0),
        "/Game/Materials/Environment/M_Grass_Path": ((0.62, 0.78, 0.32), 0.55, 0.0, 0.3, (0.0, 0.0, 0.0), 0.0),
        "/Game/Materials/Environment/M_Leaf_Gate": ((0.78, 0.55, 0.35), 0.40, 0.0, 0.5, (1.0, 0.8, 0.2), 0.2),
        "/Game/Materials/Environment/M_Momo_Dough": ((1.0, 0.95, 0.88), 0.30, 0.0, 0.5, (1.0, 0.85, 0.4), 0.25),
        "/Game/Materials/Characters/M_Golumolu_Fur": ((1.0, 0.85, 0.70), 0.45, 0.0, 0.4, (0.0, 0.0, 0.0), 0.0),
        "/Game/Materials/Characters/M_Ghost_Master": ((1.0, 0.98, 0.95), 0.15, 0.0, 0.6, (1.0, 0.95, 0.88), 0.5)
    }
    
    created = {}
    for path, (col, rough, met, spec, emis_col, emis_int) in mats.items():
        mat = create_material(path, col, rough, met, spec, emis_col, emis_int)
        created[path] = mat

    # 2. Assign default materials to imported static meshes
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
            # Set material on slot 0
            mesh.set_material(0, mat)
            unreal.EditorAssetLibrary.save_asset(mesh_path)
            print(f"Assigned {mat_path} -> {mesh_path}")

    print("Material generation and assignment completed!")

if __name__ == "__main__":
    build_materials()
