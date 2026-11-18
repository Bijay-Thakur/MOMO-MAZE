@echo off
echo === Running UE Python Fix Script via Commandlet ===
"C:\Program Files\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe" "D:\Projects\MOMO MAZE\UnrealProject\MomoMaze.uproject" -run=pythonscript -script="D:\Projects\MOMO MAZE\UnrealProject\fix_materials_commandlet.py" -stdout -FullStdOutLogOutput -Unattended -log
echo Commandlet exit code: %ERRORLEVEL%
