import unreal

subsystem = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
with open("D:/Projects/MOMO MAZE/UnrealProject/subobject_help.txt", "w") as f:
    import io, sys
    buf = io.StringIO()
    sys.stdout = buf
    help(subsystem.add_new_subobject)
    sys.stdout = sys.__stdout__
    f.write(buf.getvalue())
