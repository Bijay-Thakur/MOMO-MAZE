import unreal

matches = [attr for attr in dir(unreal) if "node" in attr.lower() or "graph" in attr.lower() or "input" in attr.lower()]
with open("D:/Projects/MOMO MAZE/UnrealProject/graph_api.txt", "w") as f:
    f.write("\n".join(matches))
