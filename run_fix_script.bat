@echo off
"C:\Program Files\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor.exe" "D:\Projects\MOMO MAZE\UnrealProject\MomoMaze.uproject" -ExecPython "D:\Projects\MOMO MAZE\UnrealProject\fix_and_rebuild_android.py" -stdout -FullStdOutLogOutput -Unattended -NullRHI -log
echo Exit code: %ERRORLEVEL%
