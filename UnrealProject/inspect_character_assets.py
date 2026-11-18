import unreal

def inspect_assets():
    with open("D:/Projects/MOMO MAZE/UnrealProject/inspect_character_assets_out.txt", "w", encoding="utf-8") as f:
        sk = unreal.EditorAssetLibrary.load_asset("/Game/Meshes/Characters/SK_Golumolu")
        f.write(f"SK_Golumolu: {sk} (Class: {sk.get_class().get_name() if sk else None})\n")
        
        gv = unreal.EditorAssetLibrary.load_asset("/Game/MomoMaze/Meshes/Characters/golumolu_validated")
        f.write(f"golumolu_validated: {gv} (Class: {gv.get_class().get_name() if gv else None})\n")
        
        mat = unreal.EditorAssetLibrary.load_asset("/Game/Materials/Characters/M_Golumolu_Fur")
        f.write(f"M_Golumolu_Fur: {mat} (Class: {mat.get_class().get_name() if mat else None})\n")

        # Check BP_MomoPlayerController
        pc_bp = unreal.EditorAssetLibrary.load_asset("/Game/Blueprints/Core/BP_MomoPlayerController")
        f.write(f"BP_MomoPlayerController: {pc_bp}\n")
        if pc_bp:
            pc_cdo = unreal.get_default_object(pc_bp.generated_class())
            f.write(f"  PC CDO: {pc_cdo}\n")
            f.write(f"  show_mouse_cursor: {getattr(pc_cdo, 'show_mouse_cursor', None)}\n")
            f.write(f"  enable_click_events: {getattr(pc_cdo, 'enable_click_events', None)}\n")
            f.write(f"  enable_touch_events: {getattr(pc_cdo, 'enable_touch_events', None)}\n")

if __name__ == "__main__":
    inspect_assets()
