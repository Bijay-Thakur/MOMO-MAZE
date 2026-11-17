import subprocess
import time
import os

ADB = r"C:\Users\starb\AppData\Local\Android\Sdk\platform-tools\adb.exe"
SERIAL = "32019046840d565f"
PKG = "com.Antigravity.MomoMaze"
ACT = "com.epicgames.unreal.SplashActivity"
SHOTS_DIR = r"D:\Projects\MOMO MAZE\Screenshots"

def adb(args):
    cmd = [ADB, "-s", SERIAL] + args
    res = subprocess.run(cmd, capture_output=True, text=True)
    return res.stdout.strip(), res.stderr.strip()

def main():
    print("=== LIVE ON-DEVICE TEST EXECUTION ===")
    
    # Force stop first
    print("1. Force-stopping any running instance...")
    adb(["shell", "am", "force-stop", PKG])
    time.sleep(1)
    
    # Launch app
    print("2. Starting MOMO MAZE on device...")
    out, err = adb(["shell", "am", "start", "-n", f"{PKG}/{ACT}"])
    print(f"Launch output: {out}")
    
    # Wait for engine initialization and level load
    print("3. Waiting 12 seconds for engine boot into LVL_MomoMaze_Game...")
    time.sleep(12)
    
    os.makedirs(SHOTS_DIR, exist_ok=True)
    
    # Screenshot 1: Boot/Menu
    print("4. Capturing Screenshot 1 (Live Screen)...")
    adb(["shell", "screencap", "-p", "/sdcard/live_screen_1.png"])
    adb(["pull", "/sdcard/live_screen_1.png", os.path.join(SHOTS_DIR, "live_screen_1.png")])
    
    # Touch input on Play button (1170, 540)
    print("5. Sending touch tap on Play button (X=1170, Y=540)...")
    adb(["shell", "input", "tap", "1170", "540"])
    time.sleep(4)
    
    # Screenshot 2: Post-tap
    print("6. Capturing Screenshot 2 (Post-Interaction)...")
    adb(["shell", "screencap", "-p", "/sdcard/live_screen_2.png"])
    adb(["pull", "/sdcard/live_screen_2.png", os.path.join(SHOTS_DIR, "live_screen_2.png")])
    
    # Diagnostics
    print("7. Process Diagnostics:")
    mem, _ = adb(["shell", "dumpsys", "meminfo", PKG])
    for line in mem.splitlines()[:20]:
        print(f"  {line}")
        
    bat, _ = adb(["shell", "dumpsys", "battery"])
    for line in bat.splitlines():
        if "temperature" in line or "level" in line:
            print(f"  {line}")
            
    print("=== LIVE TEST COMPLETED ===")

if __name__ == "__main__":
    main()
