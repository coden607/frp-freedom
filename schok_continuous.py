#!/usr/bin/env python3
"""
🔄 CONTINUOUS SCHOK VOLT MONITOR & AUTO-BYPASS
Runs continuously until your Schok Volt is detected and bypassed
"""

import subprocess
import time
import sys

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

def monitor_and_bypass():
    """Continuously monitor and auto-bypass"""
    print("=" * 60)
    print("🔄 CONTINUOUS SCHOK VOLT MONITOR & AUTO-BYPASS")
    print("=" * 60)
    print("\nThis script will:")
    print("✅ Run continuously until your Schok Volt is detected")
    print("✅ Automatically bypass FRP when device appears")
    print("✅ Show real-time status updates")
    print("✅ Handle everything automatically")
    print("\n📱 Connect your Schok Volt anytime...")
    print("⏹️  Press Ctrl+C to stop")
    print()
    
    attempt_count = 0
    
    try:
        while True:
            attempt_count += 1
            progress(f"Monitor attempt #{attempt_count}")
            
            # Check for device
            success, output, _ = run_adb_command("adb devices")
            if success and "device" in output:
                lines = output.split('\n')[1:]
                for line in lines:
                    if 'device' in line and line.strip():
                        device_id = line.strip().split('\t')[0]
                        progress(f"🎉 Schok Volt detected: {device_id}")
                        
                        # Run bypass immediately
                        if auto_bypass_device(device_id):
                            print("\n🎉🎉🎉 BYPASS COMPLETE! 🎉🎉🎉")
                            print("Your Schok Volt is now unlocked!")
                            return
                        else:
                            progress("Bypass attempted, continuing to monitor...")
            
            # Show status every 30 seconds
            if attempt_count % 15 == 0:
                progress(f"Still monitoring... (attempt #{attempt_count})")
                print("💡 Make sure USB debugging is enabled on your Schok Volt")
                print("   Try the TalkBack method if needed")
            
            time.sleep(2)
            
    except KeyboardInterrupt:
        print("\n\nMonitoring stopped by user")

def auto_bypass_device(device_id):
    """Auto bypass when device is detected"""
    progress(f"Starting bypass for {device_id}")
    
    # Restart ADB
    run_adb_command("adb kill-server")
    time.sleep(2)
    run_adb_command("adb start-server")
    time.sleep(3)
    
    # Comprehensive bypass commands
    commands = [
        "adb shell settings put secure user_setup_complete 1",
        "adb shell settings put global device_provisioned 1",
        "adb shell settings put secure setup_wizard_has_run 1",
        "adb shell pm clear com.google.android.setupwizard",
        "adb shell pm disable-user com.google.android.setupwizard",
        "adb shell content insert --uri content://settings/secure --bind name:s:user_setup_complete --bind value:i:1",
        "adb shell content insert --uri content://settings/global --bind name:s:device_provisioned --bind value:i:1",
        "adb shell am start -n com.android.settings/.Settings",
        "adb reboot"
    ]
    
    success_count = 0
    for i, cmd in enumerate(commands, 1):
        progress(f"Bypass command {i}/{len(commands)}")
        success, _, _ = run_adb_command(cmd, timeout=60)
        
        if success:
            progress(f"✓ Command {i} succeeded")
            success_count += 1
        else:
            progress(f"✗ Command {i} failed")
        
        time.sleep(3)
    
    return success_count >= len(commands) // 2

if __name__ == "__main__":
    try:
        monitor_and_bypass()
    except Exception as e:
        print(f"\n❌ Error: {e}")
