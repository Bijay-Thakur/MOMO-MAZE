import unreal

with open("D:/Projects/MOMO MAZE/UnrealProject/mesh_mats_val.txt", "w") as f:
    sm = unreal.EditorAssetLibrary.load_asset("/Game/MomoMaze/Meshes/Characters/golumolu_validated")
    f.write(f"golumolu_validated: {sm}\n")
    if sm:
        mats = sm.get_editor_property("static_materials")
        f.write(f"static_materials count: {len(mats)}\n")
        for i, m in enumerate(mats):
            f.write(f"  slot {i}: {m.material_slot_name} -> {m.material_interface}\n")
