import bpy

img = bpy.data.images.load(r"D:\Projects\MOMO MAZE\Screenshots\momo_test.mp4")
print("Video dimensions:", img.size)
print("Video frame count:", img.frame_duration)
pixels = list(img.pixels[:20])
print("First 20 pixel values:", pixels)
