"""
rebuild_and_deploy_android.py
=============================
Step 1: Runs the fix_and_rebuild_android.py via UE Editor (Python exec)
Step 2: Packages the Android APK via UAT (BuildCookRun)
Step 3: Deploys the new APK to the connected device via ADB
Step 4: Launches the game and captures a screenshot

Run from command line:
  python rebuild_and_deploy_android.py

Requires:
  - Unreal Engine 5.8 installed at C:/Program Files/Epic Games/UE_5.8
  - Android SDK/NDK at C:/Users/starb/AppData/Local/Android/Sdk
  - Device 32019046840d565f connected via USB with Developer Options enabled
"""

import subprocess
import time
import os
import sys

# ── Paths ──────────────────────────────────────────────────────────────────────
UE_ROOT = r"C:\Program Files\Epic Games\UE_5.8"
UAT_PATH = os.path.join(UE_ROOT, r"Engine\Build\BatchFiles\RunUAT.bat")
UE_EDITOR = os.path.join(UE_ROOT, r"Engine\Binaries\Win64\UnrealEditor.exe")
PROJECT_PATH = r"D:\Projects\MOMO MAZE\UnrealProject\MomoMaze.uproject"
FIX_SCRIPT = r"D:\Projects\MOMO MAZE\UnrealProject\fix_and_rebuild_android.py"
OUTPUT_APK = r"D:\Projects\MOMO MAZE\Builds\Android\MomoMaze-arm64.apk"
BINARIES_APK = r"D:\Projects\MOMO MAZE\UnrealProject\Binaries\Android\MomoMaze-arm64.apk"

ADB = r"C:\Users\starb\AppData\Local\Android\Sdk\platform-tools\adb.exe"
DEVICE = "32019046840d565f"
PACKAGE = "com.Antigravity.MomoMaze"
ACTIVITY = "com.epicgames.unreal.SplashActivity"
SCREENSHOTS_DIR = r"D:\Projects\MOMO MAZE\Screenshots"

LOG_PATH = r"D:\Projects\MOMO MAZE\UnrealProject\rebuild_deploy_log.txt"

def log(msg):
    print(f"[RebuildDeploy] {msg}")
    with open(LOG_PATH, "a") as f:
        f.write(msg + "\n")

def run(cmd, timeout=None, shell=False):
    log(f"  CMD: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout, shell=shell
        )
        if result.stdout.strip():
            log(f"  STDOUT: {result.stdout.strip()[:500]}")
        if result.stderr.strip():
            log(f"  STDERR: {result.stderr.strip()[:300]}")
        return result
    except subprocess.TimeoutExpired:
        log(f"  TIMEOUT after {timeout}s")
        return None

def adb(args, timeout=30):
    return run([ADB, "-s", DEVICE] + args, timeout=timeout)

# ── STEP 1: Run fix script inside UE Editor (headless) ─────────────────────────
def step1_fix_in_editor():
    log("\n=== STEP 1: Running fix script in UE Editor (headless) ===")
    cmd = [
        UE_EDITOR,
        PROJECT_PATH,
        "-ExecPython", FIX_SCRIPT,
        "-stdout", "-FullStdOutLogOutput",
        "-Unattended", "-NullRHI",
        "-log"
    ]
    log("Running UE Editor with fix script (this takes ~60-90 seconds)...")
    result = run(cmd, timeout=180)
    if result and result.returncode == 0:
        log("Editor fix script completed successfully.")
    else:
        log(f"Editor returned code: {result.returncode if result else 'TIMEOUT'}")
        log("Continuing anyway (manual fix may be needed)...")

# ── STEP 2: Package Android APK via UAT ────────────────────────────────────────
def step2_package_android():
    log("\n=== STEP 2: Packaging Android APK via UAT ===")

    if not os.path.exists(UAT_PATH):
        log(f"ERROR: UAT not found at {UAT_PATH}")
        sys.exit(1)

    # Clean old APK first
    for apk in [OUTPUT_APK, BINARIES_APK]:
        if os.path.exists(apk):
            os.rename(apk, apk + ".backup")
            log(f"Backed up old APK: {apk}.backup")

    cmd = [
        UAT_PATH,
        "BuildCookRun",
        f"-project={PROJECT_PATH}",
        "-noP4",
        "-platform=Android",
        "-clientconfig=Development",
        "-cook",
        "-allmaps",
        "-build",
        "-stage",
        "-pak",
        "-archive",
        f"-archivedirectory={os.path.dirname(OUTPUT_APK)}",
        "-package",
        "-distribution",
        "-CookFlavor=ASTC",
        "-prereqs",
        "-nodebuginfo",
        "-Unattended",
    ]

    log("Running UAT BuildCookRun (this takes 10-30 minutes)...")
    log("Full package log will appear in UE Saved/Logs/...")

    result = run(cmd, timeout=3600)  # 60 min max
    if result and result.returncode == 0:
        log("UAT packaging SUCCESS!")
        return True
    else:
        rc = result.returncode if result else "TIMEOUT"
        log(f"UAT packaging FAILED (rc={rc}). Check Saved/Logs/ for details.")
        return False

# ── STEP 3: Deploy APK to device ───────────────────────────────────────────────
def step3_deploy():
    log("\n=== STEP 3: Deploying APK to device ===")

    # Find the APK
    apk_to_install = None
    for candidate in [OUTPUT_APK, BINARIES_APK]:
        if os.path.exists(candidate):
            apk_to_install = candidate
            size_mb = os.path.getsize(candidate) / (1024*1024)
            log(f"Found APK: {candidate} ({size_mb:.1f} MB)")
            break

    if not apk_to_install:
        log("ERROR: No APK found to install!")
        return False

    # Check device
    res = adb(["get-state"])
    if not res or "device" not in res.stdout:
        log("ERROR: Device not connected or not ready!")
        return False

    # Uninstall old version
    log("Uninstalling old version...")
    adb(["uninstall", PACKAGE])

    # Clean stale data
    adb(["shell", "rm", "-rf", "/sdcard/UnrealGame/MomoMaze"])
    adb(["shell", "rm", "-rf", f"/sdcard/Android/obb/{PACKAGE}"])

    # Install new APK
    log("Installing new APK (-r -g)...")
    res = adb(["install", "-r", "-g", apk_to_install], timeout=120)
    if not res or "Success" not in res.stdout:
        log(f"INSTALL FAILED: {res.stdout if res else 'no output'}")
        return False

    log("APK installed successfully!")

    # Grant storage permissions
    adb(["shell", "pm", "grant", PACKAGE, "android.permission.READ_EXTERNAL_STORAGE"])
    adb(["shell", "pm", "grant", PACKAGE, "android.permission.WRITE_EXTERNAL_STORAGE"])
    log("Storage permissions granted.")
    return True

# ── STEP 4: Launch and capture screenshot ──────────────────────────────────────
def step4_launch_and_verify():
    log("\n=== STEP 4: Launching game and verifying ===")

    # Clear logcat
    adb(["logcat", "-c"])

    # Force stop any old instance
    adb(["shell", "am", "force-stop", PACKAGE])
    time.sleep(1)

    # Launch
    res = adb(["shell", "am", "start", "-n", f"{PACKAGE}/{ACTIVITY}"])
    log(f"Launch result: {res.stdout if res else 'failed'}")

    # Wait for engine to boot and render first frame
    log("Waiting 20 seconds for engine boot + map load + NavMesh check...")
    for i in range(20, 0, -5):
        log(f"  {i}s remaining...")
        time.sleep(5)

    # Capture screenshot
    os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
    adb(["shell", "screencap", "-p", "/sdcard/momo_fixed.png"])
    local_shot = os.path.join(SCREENSHOTS_DIR, "momo_fixed_final.png")
    adb(["pull", "/sdcard/momo_fixed.png", local_shot])
    log(f"Screenshot pulled to: {local_shot}")

    # Dump key logcat lines
    logcat_res = run([ADB, "-s", DEVICE, "logcat", "-d", "-s", "UE"], timeout=15)
    if logcat_res:
        ue_lines = [l for l in logcat_res.stdout.splitlines()
                    if any(k in l for k in ["NavMesh", "Error", "Fatal", "LoadMap",
                                            "Spawn", "Warning", "material", "crash"])]
        log("\nKey UE logcat lines:")
        for line in ue_lines[-20:]:
            log(f"  {line}")

    # Check foreground activity
    act_res = run([ADB, "-s", DEVICE, "shell", "dumpsys", "activity", "top"], timeout=10)
    if act_res and "MomoMaze" in act_res.stdout:
        log("\n✓ MOMO MAZE is in the FOREGROUND — game is running!")
    else:
        log("\n✗ MOMO MAZE not in foreground — may have crashed")

    return local_shot


# ── MAIN ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    with open(LOG_PATH, "w") as f:
        f.write("=== MOMO MAZE Full Android Rebuild & Deploy ===\n\n")

    args = sys.argv[1:]
    skip_editor = "--skip-editor" in args
    skip_package = "--skip-package" in args
    deploy_only = "--deploy-only" in args

    if deploy_only:
        step3_deploy()
        step4_launch_and_verify()
    else:
        if not skip_editor:
            step1_fix_in_editor()
        if not skip_package:
            success = step2_package_android()
            if not success:
                log("\nPackaging failed — attempting deploy with existing APK anyway...")
        step3_deploy()
        step4_launch_and_verify()

    log("\n=== ALL DONE ===")
    log(f"Check screenshot in: {SCREENSHOTS_DIR}")
    log(f"Check full log at: {LOG_PATH}")
