import subprocess
import time
import os

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
    print(f"=== Deploying MOMO MAZE to Connected Device ({SERIAL}) ===")
    
    # 1. Install APK
    print("Installing APK...")
    res = run_adb(["install", "-r", APK_PATH])
    if "Success" not in res.stdout:
        print("Install warning or retry needed!")
        
    # 2. Force-stop previous instance if any
    run_adb(["shell", "am", "force-stop", PACKAGE])
    time.sleep(1)
    
    # 3. Launch App
    print("Launching MOMO MAZE on device...")
    run_adb(["shell", "am", "start", "-n", f"{PACKAGE}/{ACTIVITY}"])
    
    # 4. Wait for engine boot and level load
    print("Waiting 10s for game to boot into LVL_MomoMaze_Game...")
    time.sleep(10)
    
    # 5. Capture Boot / Main Menu Screen
    os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
    remote_shot = "/sdcard/device_momo_menu_live.png"
    local_shot = os.path.join(SCREENSHOTS_DIR, "device_momo_menu_live.png")
    run_adb(["shell", "screencap", "-p", remote_shot])
    run_adb(["pull", remote_shot, local_shot])
    print(f"Saved live screenshot to {local_shot}")
    
    # 6. Simulate Touch Input on Play Button
    # Center of screen on 2340x1080 landscape: X=1170, Y=540 (approx Play button location)
    print("Simulating Touch Input tap on 'Play' button (1170, 540)...")
    run_adb(["shell", "input", "tap", "1170", "540"])
    time.sleep(3)
    
    # 7. Capture After Touch Interaction
    remote_shot2 = "/sdcard/device_momo_play_live.png"
    local_shot2 = os.path.join(SCREENSHOTS_DIR, "device_momo_play_live.png")
    run_adb(["shell", "screencap", "-p", remote_shot2])
    run_adb(["pull", remote_shot2, local_shot2])
    print(f"Saved interactive screenshot to {local_shot2}")
    
    # 8. Check RAM and Battery status
    print("\n--- Physical Device Diagnostics ---")
    mem = run_adb(["shell", "dumpsys", "meminfo", PACKAGE])
    for line in mem.stdout.splitlines()[:15]:
        print(f"  {line}")
        
    bat = run_adb(["shell", "dumpsys", "battery"])
    for line in bat.stdout.splitlines():
        if "temperature" in line or "level" in line:
            print(f"  Battery: {line.strip()}")
            
    print("\n=== DEPLOYMENT AND ON-DEVICE TESTING COMPLETED! ===")

if __name__ == "__main__":
    main()
