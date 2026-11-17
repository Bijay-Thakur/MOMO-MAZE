import bpy
import os

fbx_dir = r"D:\Projects\MOMO MAZE\BlenderSources\exports\fbx"
files = [f for f in os.listdir(fbx_dir) if f.endswith("_validated.fbx") or f.startswith("SM_")]

print("\n=== FBX INVENTORY ===")
for f in sorted(files):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    full_path = os.path.join(fbx_dir, f)
    bpy.ops.import_scene.fbx(filepath=full_path)
    
    meshes = [o for o in bpy.data.objects if o.type == 'MESH']
    armatures = [o for o in bpy.data.objects if o.type == 'ARMATURE']
    total_verts = sum(len(m.data.vertices) for m in meshes)
    total_faces = sum(len(m.data.polygons) for m in meshes)
    materials = list(bpy.data.materials.keys())
    
    print(f"\n[File: {f}]")
    print(f"  Meshes ({len(meshes)}): {[m.name for m in meshes]}")
    print(f"  Armatures ({len(armatures)}): {[a.name for a in armatures]}")
    print(f"  Vertices: {total_verts}, Polygons: {total_faces}")
    print(f"  Materials ({len(materials)}): {materials}")
print("\n=== END INVENTORY ===")
