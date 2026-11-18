import unreal

with open("D:/Projects/MOMO MAZE/UnrealProject/inspect_mat_fur.txt", "w") as f:
    mat = unreal.EditorAssetLibrary.load_asset("/Game/Materials/Characters/M_Golumolu_Fur")
    f.write(f"M_Golumolu_Fur: {mat}\n")
    if mat:
        props = [p for p in dir(mat) if not p.startswith("_")]
        f.write(f"props: {props}\n")
