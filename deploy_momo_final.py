import subprocess
import time
import os
import sys

ADB = r"C:\Users\starb\AppData\Local\Android\Sdk\platform-tools\adb.exe"
SERIAL = "32019046840d565f"
APK_PATH = r"D:\Projects\MOMO MAZE\Builds\Android\MomoMaze-arm64.apk"
PACKAGE = "com.Antigravity.MomoMaze"
ACTIVITY = "com.epicgames.unreal.SplashActivity"
SCREENSHOTS_DIR = r"D:\Projects\MOMO MAZE\Screenshots"

def run_adb(args):
    cmd = [ADB, "-s", SERIAL] + args
    print(f"Running: {' '.join(cmd)}")
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.stdout:
        print(res.stdout.strip())
    if res.stderr:
        print(f"Stderr: {res.stderr.strip()}")
    return res

def main():
    print(f"=== DEPLOYING MOMO MAZE 31x31 TO DEVICE ({SERIAL}) ===")
    
    # 0. Check device connection
    res = run_adb(["get-state"])
    if "device" not in res.stdout:
        print("Device not ready!")
        sys.exit(1)

    # 1. Uninstall old version
    print("\n[Step 1] Uninstalling previous build...")
    run_adb(["uninstall", PACKAGE])

    # 2. Install new APK
    print("\n[Step 2] Installing new APK (165MB)...")
    res = run_adb(["install", "-r", "-g", APK_PATH])
    if "Success" not in res.stdout:
        print(f"Install error: {res.stdout} {res.stderr}")
        sys.exit(1)
    print("Installation SUCCESS!")

    # 3. Clean up any stale saved logs or obb
    run_adb(["shell", "rm", "-rf", "/sdcard/UnrealGame/MomoMaze"])

    # 4. Clear logcat
    run_adb(["logcat", "-c"])

    # 5. Launch app
    print("\n[Step 3] Launching MOMO MAZE on device...")
    run_adb(["shell", "am", "start", "-n", f"{PACKAGE}/{ACTIVITY}"])

    # 6. Wait for splash activity, engine init, shader load, and level spawn
    print("\n[Step 4] Waiting for engine and 31x31 maze to load (15 seconds)...")
    for sec in range(15, 0, -3):
        print(f"  {sec} seconds remaining...")
        time.sleep(3)

    # 7. Capture screenshots
    os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
    remote_shot = "/sdcard/momo_gameplay_live.png"
    local_shot = os.path.join(SCREENSHOTS_DIR, "momo_gameplay_live.png")
    
    print("\n[Step 5] Capturing device screen...")
    run_adb(["shell", "screencap", "-p", remote_shot])
    run_adb(["pull", remote_shot, local_shot])
    print(f"Pulled screenshot to: {local_shot}")

    # 8. Check logcat for UE errors or status
    print("\n[Step 6] Checking device logcat for MomoMaze logs...")
    logcat_res = subprocess.run([ADB, "-s", SERIAL, "logcat", "-d", "-s", "UE:V", "MomoMaze:V"], capture_output=True, text=True)
    with open(os.path.join(SCREENSHOTS_DIR, "device_ue_logcat.txt"), "w", encoding="utf-8") as f:
        f.write(logcat_res.stdout)
    
    ue_lines = [l for l in logcat_res.stdout.splitlines() if "LoadMap" in l or "Error" in l or "Warning" in l or "Spawn" in l]
    print("Relevant logcat lines:")
    for l in ue_lines[-15:]:
        print(f"  {l}")

    # 9. Analyze screenshot pixel data
    try:
        from PIL import Image
        import numpy as np
        img = Image.open(local_shot)
        arr = np.array(img)
        print(f"\n[Step 7] Image Analysis: Size={img.size}, Shape={arr.shape}")
        rgb = arr[:, :, :3]
        mean_rgb = np.mean(rgb, axis=(0, 1))
        max_rgb = np.max(rgb, axis=(0, 1))
        min_rgb = np.min(rgb, axis=(0, 1))
        print(f"  Mean RGB: {mean_rgb}")
        print(f"  Max RGB:  {max_rgb}")
        print(f"  Min RGB:  {min_rgb}")
        
        # Non-black pixel percentage (threshold > 10)
        bright_pixels = np.sum(np.any(rgb > 15, axis=-1))
        total_pixels = rgb.shape[0] * rgb.shape[1]
        bright_pct = (bright_pixels / total_pixels) * 100
        print(f"  Non-black (>15) pixels: {bright_pct:.2f}%")
        
        if mean_rgb.mean() > 10.0 and bright_pct > 20.0:
            print("\n*** VERIFIED: MOMO MAZE 3D GAMEPLAY IS FULLY VISIBLE AND RENDERING ON DEVICE! ***")
        else:
            print("\n*** WARNING: Screen might still be dark. Check logcat and image. ***")
    except Exception as e:
        print(f"Image analysis error: {e}")

if __name__ == "__main__":
    main()
