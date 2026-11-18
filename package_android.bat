@echo off
echo === MOMO MAZE Android Package Build ===
echo Started: %date% %time%

set UE_ROOT=C:\Program Files\Epic Games\UE_5.8
set PROJECT=D:\Projects\MOMO MAZE\UnrealProject\MomoMaze.uproject
set ARCHIVE=D:\Projects\MOMO MAZE\Builds\Android

echo Running UAT BuildCookRun...
"%UE_ROOT%\Engine\Build\BatchFiles\RunUAT.bat" BuildCookRun ^
    -project="%PROJECT%" ^
    -noP4 ^
    -platform=Android ^
    -clientconfig=Development ^
    -cook ^
    -allmaps ^
    -build ^
    -stage ^
    -pak ^
    -archive ^
    -archivedirectory="%ARCHIVE%" ^
    -package ^
    -CookFlavor=ASTC ^
    -prereqs ^
    -nodebuginfo ^
    -Unattended

echo.
echo UAT finished with exit code: %ERRORLEVEL%
echo Finished: %date% %time%
