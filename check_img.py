import bpy
import os

ref_dir = r"D:\Projects\MOMO MAZE\Refrence image"
for f in os.listdir(ref_dir):
    if f.endswith(".png"):
        img = bpy.data.images.load(os.path.join(ref_dir, f))
        print(f"{f}: {img.size[0]} x {img.size[1]}")
