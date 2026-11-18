import unreal

with open("D:/Projects/MOMO MAZE/UnrealProject/mesh_mats.txt", "w") as f:
    sm = unreal.EditorAssetLibrary.load_asset("/Game/Meshes/Characters/SK_Golumolu")
    f.write(f"SK_Golumolu: {sm}\n")
    if sm:
        mats = sm.get_editor_property("static_materials")
        f.write(f"static_materials count: {len(mats)}\n")
        for i, m in enumerate(mats):
            f.write(f"  slot {i}: {m.material_slot_name} -> {m.material_interface}\n")
