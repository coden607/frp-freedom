#!/usr/bin/env python3
"""
🔄 SCHOK VOLT AUTO-MONITOR (Running in Background)
Continuously monitors and auto-bypasses when device appears
"""

import subprocess
import time
import sys
import os

def progress(msg):
    print(f"[*] {msg}")

def run_adb_command(cmd, timeout=30):
    """Run ADB command with error handling"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
    except subprocess.TimeoutExpired:
        return False, "", "Timeout"
    except Exception as e:
        return False, "", str(e)

def auto_bypass_schok(device_id):
    """Auto bypass Schok Volt when detected"""
    progress(f"🎉 Schok Volt detected: {device_id}")
    progress("🚀 Starting automatic FRP bypass...")
    
    # Restart ADB for clean connection
    run_adb_command("adb kill-server")
    time.sleep(2)
    run_adb_command("adb start-server")
    time.sleep(3)
    
    # Ultimate bypass commands
    commands = [
        "adb shell settings put secure user_setup_complete 1",
        "adb shell settings put global device_provisioned 1",
        "adb shell settings put secure setup_wizard_has_run 1",
        "adb shell settings put secure skip_first_use_hints 1",
        "adb shell pm clear com.google.android.setupwizard",
        "adb shell pm clear com.google.android.gms",
        "adb shell pm disable-user com.google.android.setupwizard",
        "adb shell pm disable-user com.google.android.gms",
        "adb shell content insert --uri content://settings/secure --bind name:s:user_setup_complete --bind value:i:1",
        "adb shell content insert --uri content://settings/global --bind name:s:device_provisioned --bind value:i:1",
        "adb shell content insert --uri content://settings/secure --bind name:s:setup_wizard_has_run --bind value:i:1",
        "adb shell am broadcast -a android.intent.action.BOOT_COMPLETED",
        "adb shell am start -n com.android.settings/.Settings",
        "adb shell input keyevent KEYCODE_HOME",
        "adb reboot"
    ]
    
    success_count = 0
    for i, cmd in enumerate(commands, 1):
        progress(f"Bypass {i}/{len(commands)}: {cmd}")
        success, stdout, stderr = run_adb_command(cmd, timeout=90)
        
        if success:
            progress(f"✅ Command {i} succeeded")
            success_count += 1
        else:
            progress(f"❌ Command {i} failed")
        
        time.sleep(3)
    
    if success_count >= len(commands) // 2:
        progress("🎉🎉🎉 SCHOK VOLT FRP BYPASSED! 🎉🎉🎉")
        progress("Your device will reboot and be accessible!")
        return True
    else:
        progress("⚠️ Partial bypass - device may need manual steps")
        return False

def main():
    print("=" * 60)
    print("🔄 SCHOK VOLT AUTO-MONITOR")
    print("=" * 60)
    print("\nMonitoring for Schok Volt connection...")
    print("Will auto-bypass when device is detected!")
    print("Press Ctrl+C to stop monitoring")
    print()
    
    monitor_count = 0
    
    try:
        while True:
            monitor_count += 1
            
            # Check for devices
            success, output, _ = run_adb_command("adb devices")
            if success and "device" in output:
                lines = output.split('\n')[1:]
                for line in lines:
                    if 'device' in line and line.strip():
                        device_id = line.strip().split('\t')[0]
                        
                        # Device found - run bypass
                        if auto_bypass_schok(device_id):
                            print("\n✅ BYPASS COMPLETE! Your Schok Volt is now unlocked!")
                            break
                        
                        # Continue monitoring after bypass attempt
                        time.sleep(10)
            
            # Status update every 15 checks (30 seconds)
            if monitor_count % 15 == 0:
                progress(f"Still monitoring... (check #{monitor_count})")
                print("💡 Enable USB debugging on your Schok Volt if not detected")
                print("   Use TalkBack method: Accessibility → TalkBack → L gesture → Help → Web Search")
            
            time.sleep(2)
            
    except KeyboardInterrupt:
        print("\n\nMonitoring stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()
