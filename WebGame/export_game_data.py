import json
import os

with open("d:/Projects/MOMO MAZE/LEVEL_CONFIG_25.json", "r", encoding="utf-8") as f:
    levels_data = json.load(f)

with open("d:/Projects/MOMO MAZE/UnrealProject/Content/MazeData_31x31.json", "r", encoding="utf-8") as f:
    maze_31_data = json.load(f)

output_js = f"""// Game Data for MOMO MAZE Browser Edition
export const CAMPAIGN_LEVELS = {json.dumps(levels_data['campaign'], indent=2)};

export const MASTER_MAZE_31X31 = {json.dumps(maze_31_data, indent=2)};
"""

with open("d:/Projects/MOMO MAZE/WebGame/js/game_data.js", "w", encoding="utf-8") as f:
    f.write(output_js)

print("game_data.js generated successfully! Size:", os.path.getsize("d:/Projects/MOMO MAZE/WebGame/js/game_data.js"))
