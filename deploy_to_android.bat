@echo off
echo === MOMO MAZE Deploy to Android Device ===
set ADB=C:\Users\starb\AppData\Local\Android\Sdk\platform-tools\adb.exe
set DEVICE=32019046840d565f
set PACKAGE=com.Antigravity.MomoMaze
set ACTIVITY=com.epicgames.unreal.SplashActivity
set APK=D:\Projects\MOMO MAZE\Builds\Android\MomoMaze-arm64.apk

echo Checking device connection...
"%ADB%" -s %DEVICE% get-state
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Device not connected!
    pause
    exit /b 1
)

echo.
echo Uninstalling old build...
"%ADB%" -s %DEVICE% uninstall %PACKAGE%

echo.
echo Clearing stale data...
"%ADB%" -s %DEVICE% shell rm -rf /sdcard/UnrealGame/MomoMaze
"%ADB%" -s %DEVICE% shell rm -rf /sdcard/Android/obb/%PACKAGE%

echo.
echo Installing APK: %APK%
"%ADB%" -s %DEVICE% install -r -g "%APK%"
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: APK install failed!
    pause
    exit /b 1
)

echo.
echo Granting permissions...
"%ADB%" -s %DEVICE% shell pm grant %PACKAGE% android.permission.READ_EXTERNAL_STORAGE >nul 2>&1
"%ADB%" -s %DEVICE% shell pm grant %PACKAGE% android.permission.WRITE_EXTERNAL_STORAGE >nul 2>&1

echo.
echo Clearing logcat...
"%ADB%" -s %DEVICE% logcat -c

echo.
echo Launching MOMO MAZE...
"%ADB%" -s %DEVICE% shell am force-stop %PACKAGE%
timeout /t 1 /nobreak >nul
"%ADB%" -s %DEVICE% shell am start -n %PACKAGE%/%ACTIVITY%

echo.
echo Waiting 20 seconds for game to boot...
timeout /t 20 /nobreak

echo.
echo Capturing screenshot...
"%ADB%" -s %DEVICE% shell screencap -p /sdcard/momo_final_deploy.png
"%ADB%" -s %DEVICE% pull /sdcard/momo_final_deploy.png "D:\Projects\MOMO MAZE\Screenshots\momo_final_deploy.png"

echo.
echo Checking UE logcat for errors...
"%ADB%" -s %DEVICE% logcat -d -s UE 2>&1 | findstr /i "NavMesh Error Fatal crash LoadMap"

echo.
echo === Deploy Complete! ===
echo Screenshot saved to: D:\Projects\MOMO MAZE\Screenshots\momo_final_deploy.png
pause
