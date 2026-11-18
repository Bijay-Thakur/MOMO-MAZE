import unreal

matches = [attr for attr in dir(unreal) if "compiler" in attr.lower() or "compile" in attr.lower() or "blueprint" in attr.lower()]
with open("D:/Projects/MOMO MAZE/UnrealProject/bp_methods.txt", "w") as f:
    f.write("\n".join(matches))
