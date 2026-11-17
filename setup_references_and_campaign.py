import os
import shutil
import json
from PIL import Image

workspace = r"D:\Projects\MOMO MAZE"

# 1. Setup directories
screen_ref_dir = os.path.join(workspace, "01_Screen_References")
art_ref_dir = os.path.join(workspace, "02_Original_Art_References")
overview_dir = os.path.join(workspace, "03_Approved_AB_Overview")

for d in [screen_ref_dir, art_ref_dir, overview_dir]:
    os.makedirs(d, exist_ok=True)

# 2. Crop 19 screens
img_path = os.path.join(workspace, "Refrence image", "MOMO_MAZE_ALL_19_SCREEN_INDEX.jpg")
index_img = Image.open(img_path)

screen_names = [
    "01_A_Splash.png",
    "02_B_Main_Menu.png",
    "03_B_Play_Menu.png",
    "04_B_Garden_Level_Map.png",
    "05_B_Level_Preview.png",
    "06_B_Loading.png",
    "07_A_Tutorial.png",
    "08_A_Gameplay_HUD.png",
    "09_B_Map_Overlay.png",
    "10_B_Pause.png",
    "11_A_Victory.png",
    "12_A_Defeat.png",
    "13_B_Chapter_Complete.png",
    "14_B_Golumolu_Closet.png",
    "15_B_Spirit_Book.png",
    "16_B_Sticker_Collection.png",
    "17_B_Custom_Play.png",
    "18_B_Settings.png",
    "19_B_Credits.png"
]

row_ranges = [(70, 333), (358, 627), (652, 921), (946, 1215), (1240, 1509)]
col_ranges = [(29, 506), (525, 1002), (1021, 1498), (1517, 1994)]

name_idx = 0
for r_idx, (y1, y2) in enumerate(row_ranges):
    num_cols = 3 if r_idx == 4 else 4
    for c_idx in range(num_cols):
        x1, x2 = col_ranges[c_idx]
        crop_box = (x1, y1, x2, y2)
        screen_crop = index_img.crop(crop_box)
        out_name = screen_names[name_idx]
        out_path = os.path.join(screen_ref_dir, out_name)
        screen_crop.save(out_path, format="PNG")
        print(f"Saved screen {name_idx+1}: {out_name} {crop_box}")
        name_idx += 1

# 3. Copy Original Art References
art_mappings = [
    ("ChatGPT Image Nov 16, 2026, 08_55_52 PM-1.png", "01_Environment_Maze_Concept.png"),
    ("ChatGPT Image Nov 16, 2026, 08_56_06 PM-2.png", "02_Golumolu_Character_Concept.png"),
    ("ChatGPT Image Nov 16, 2026, 08_56_21 PM-3.png", "03_Ghosts_Spirits_Concept.png"),
    ("ChatGPT Image Nov 16, 2026, 08_56_30 PM-4.png", "04_Props_Gates_Concept.png")
]

for src_name, dst_name in art_mappings:
    src_p = os.path.join(workspace, "Refrence image", src_name)
    dst_p = os.path.join(art_ref_dir, dst_name)
    shutil.copy2(src_p, dst_p)
    print(f"Copied art reference: {dst_name}")

# 4. Copy Overview Board
shutil.copy2(img_path, os.path.join(overview_dir, "01_Approved_AB_Overview_Grid.jpg"))
print("Saved overview board.")

# 5. Build LEVEL_CONFIG_25.json
campaign_levels = [
    # Chapter 1: The Little Meadow (L1-5)
    {"level_id": 1, "chapter": 1, "chapter_name": "The Little Meadow", "name": "First Bite", "grid_size": 15, "starting_spirits": 1, "target_momos": 6, "has_moving_gates": False, "intro_mechanic": "Basic Movement & Golden Momo"},
    {"level_id": 2, "chapter": 1, "chapter_name": "The Little Meadow", "name": "Follow the Flowers", "grid_size": 15, "starting_spirits": 1, "target_momos": 8, "has_moving_gates": False, "intro_mechanic": "Flower Trails"},
    {"level_id": 3, "chapter": 1, "chapter_name": "The Little Meadow", "name": "Two Little Spirits", "grid_size": 15, "starting_spirits": 1, "target_momos": 10, "has_moving_gates": False, "intro_mechanic": "Spirit Splitting at 60s"},
    {"level_id": 4, "chapter": 1, "chapter_name": "The Little Meadow", "name": "Momo Rescue", "grid_size": 17, "starting_spirits": 1, "target_momos": 12, "has_moving_gates": False, "intro_mechanic": "Banishment with Momo"},
    {"level_id": 5, "chapter": 1, "chapter_name": "The Little Meadow", "name": "The Golden Arch", "grid_size": 17, "starting_spirits": 1, "target_momos": 14, "has_moving_gates": True, "intro_mechanic": "Timed Leaf Gate"},

    # Chapter 2: The Blooming Garden (L6-10)
    {"level_id": 6, "chapter": 2, "chapter_name": "The Blooming Garden", "name": "Leafy Turns", "grid_size": 19, "starting_spirits": 1, "target_momos": 14, "has_moving_gates": False, "intro_mechanic": "Cutter Ghost Introduction"},
    {"level_id": 7, "chapter": 2, "chapter_name": "The Blooming Garden", "name": "Wiggle Wall", "grid_size": 19, "starting_spirits": 1, "target_momos": 16, "has_moving_gates": True, "intro_mechanic": "Swaying Hedges"},
    {"level_id": 8, "chapter": 2, "chapter_name": "The Blooming Garden", "name": "Petal Gate", "grid_size": 19, "starting_spirits": 1, "target_momos": 16, "has_moving_gates": True, "intro_mechanic": "Dual Timed Petal Gates"},
    {"level_id": 9, "chapter": 2, "chapter_name": "The Blooming Garden", "name": "Secret Shortcut", "grid_size": 21, "starting_spirits": 1, "target_momos": 18, "has_moving_gates": False, "intro_mechanic": "Magic Hedge Shortcuts"},
    {"level_id": 10, "chapter": 2, "chapter_name": "The Blooming Garden", "name": "Flower Clock", "grid_size": 21, "starting_spirits": 1, "target_momos": 20, "has_moving_gates": True, "intro_mechanic": "Rotating Gate Sequence"},

    # Chapter 3: The Whispering Hedges (L11-15)
    {"level_id": 11, "chapter": 3, "chapter_name": "The Whispering Hedges", "name": "Corner Trick", "grid_size": 23, "starting_spirits": 1, "target_momos": 20, "has_moving_gates": False, "intro_mechanic": "Wanderer Ghost Introduction"},
    {"level_id": 12, "chapter": 3, "chapter_name": "The Whispering Hedges", "name": "Two Trails", "grid_size": 23, "starting_spirits": 1, "target_momos": 22, "has_moving_gates": False, "intro_mechanic": "Branching Labyrinths"},
    {"level_id": 13, "chapter": 3, "chapter_name": "The Whispering Hedges", "name": "Safe Meadow", "grid_size": 23, "starting_spirits": 1, "target_momos": 24, "has_moving_gates": False, "intro_mechanic": "Safe Rest Clearings"},
    {"level_id": 14, "chapter": 3, "chapter_name": "The Whispering Hedges", "name": "Sway and Switch", "grid_size": 25, "starting_spirits": 1, "target_momos": 26, "has_moving_gates": True, "intro_mechanic": "Switching Hedge Portals"},
    {"level_id": 15, "chapter": 3, "chapter_name": "The Whispering Hedges", "name": "Lost in Bloom", "grid_size": 25, "starting_spirits": 1, "target_momos": 28, "has_moving_gates": True, "intro_mechanic": "Four-Way Gate Synchronization"},

    # Chapter 4: The Sparkling Grove (L16-20)
    {"level_id": 16, "chapter": 4, "chapter_name": "The Sparkling Grove", "name": "The Sleepy Spirit", "grid_size": 27, "starting_spirits": 1, "target_momos": 28, "has_moving_gates": False, "intro_mechanic": "Puff Dash Choke Points"},
    {"level_id": 17, "chapter": 4, "chapter_name": "The Sparkling Grove", "name": "Rush of Wind", "grid_size": 27, "starting_spirits": 1, "target_momos": 30, "has_moving_gates": True, "intro_mechanic": "Windy Corridors"},
    {"level_id": 18, "chapter": 4, "chapter_name": "The Sparkling Grove", "name": "Mushroom Loop", "grid_size": 27, "starting_spirits": 1, "target_momos": 32, "has_moving_gates": False, "intro_mechanic": "Double Loop Traps"},
    {"level_id": 19, "chapter": 4, "chapter_name": "The Sparkling Grove", "name": "Spirit Waltz", "grid_size": 29, "starting_spirits": 1, "target_momos": 34, "has_moving_gates": True, "intro_mechanic": "Synchronized Ghost Patrols"},
    {"level_id": 20, "chapter": 4, "chapter_name": "The Sparkling Grove", "name": "Sunset Escape", "grid_size": 29, "starting_spirits": 1, "target_momos": 36, "has_moving_gates": True, "intro_mechanic": "Triple Gate Cascade"},

    # Chapter 5: The Golden Garden (L21-25)
    {"level_id": 21, "chapter": 5, "chapter_name": "The Golden Garden", "name": "Golden Wind", "grid_size": 31, "starting_spirits": 1, "target_momos": 38, "has_moving_gates": True, "intro_mechanic": "Fast Ghost Pulse"},
    {"level_id": 22, "chapter": 5, "chapter_name": "The Golden Garden", "name": "Four Little Spirits", "grid_size": 31, "starting_spirits": 1, "target_momos": 40, "has_moving_gates": False, "intro_mechanic": "Quad Spirit Cap at 180s"},
    {"level_id": 23, "chapter": 5, "chapter_name": "The Golden Garden", "name": "Living Crossroads", "grid_size": 33, "starting_spirits": 1, "target_momos": 42, "has_moving_gates": True, "intro_mechanic": "Dynamic Quad Crossroads"},
    {"level_id": 24, "chapter": 5, "chapter_name": "The Golden Garden", "name": "The Long Garden", "grid_size": 33, "starting_spirits": 1, "target_momos": 45, "has_moving_gates": True, "intro_mechanic": "Endurance Maze"},
    {"level_id": 25, "chapter": 5, "chapter_name": "The Golden Garden", "name": "The Grand Golden Momo", "grid_size": 35, "starting_spirits": 1, "target_momos": 50, "has_moving_gates": True, "intro_mechanic": "The Final Grand Gate & Celebration"}
]

config_path = os.path.join(workspace, "LEVEL_CONFIG_25.json")
with open(config_path, "w", encoding="utf-8") as f:
    json.dump({"game": "MOMO MAZE", "campaign": campaign_levels}, f, indent=2)

print(f"Generated {len(campaign_levels)} campaign levels in {config_path}")
