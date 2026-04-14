#!/usr/bin/env python3
"""
Device Connection Verification Tool
Helps troubleshoot USB connection issues with Android devices
"""

import subprocess
import time
import sys
from pathlib import Path

# Add the src directory to the Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def run_command(cmd, timeout=10):
    """Run a command and return output"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except Exception as e:
        return False, "", str(e)

def check_usb_devices():
    """Check all USB devices"""
    print("=== USB DEVICE CHECK ===")
    success, output, error = run_command("lsusb")
    if success:
        print("USB Devices Found:")
        for line in output.split('\n'):
            if line.strip():
                print(f"  {line}")
    else:
        print(f"USB scan failed: {error}")

def check_adb_status():
    """Check ADB status and restart if needed"""
    print("\n=== ADB STATUS CHECK ===")
    
    # Check ADB version
    success, output, error = run_command("adb version")
    if success:
        print(f"ADB Version: {output.split()[2] if len(output.split()) > 2 else 'Unknown'}")
    else:
        print("ADB not found or not working")
        return False
    
    # Restart ADB server
    print("Restarting ADB server...")
    run_command("adb kill-server")
    time.sleep(2)
    run_command("adb start-server")
    time.sleep(3)
    
    # Check devices
    success, output, error = run_command("adb devices")
    if success:
        print(f"ADB Devices: {output}")
        return "device" in output or "unauthorized" in output or "recovery" in output
    else:
        print(f"ADB device check failed: {error}")
        return False

def check_fastboot_status():
    """Check Fastboot status"""
    print("\n=== FASTBOOT STATUS CHECK ===")
    
    # Check Fastboot version
    success, output, error = run_command("fastboot --version")
    if success:
        print(f"Fastboot available")
    else:
        print("Fastboot not found")
        return False
    
    # Check devices
    success, output, error = run_command("fastboot devices")
    if success:
        print(f"Fastboot Devices: {output}")
        return "fastboot" in output.lower() and len(output.strip().split('\n')) > 1
    else:
        print(f"Fastboot device check failed: {error}")
        return False

def check_android_vendor_ids():
    """Check for Android vendor IDs in USB devices"""
    print("\n=== ANDROID VENDOR ID CHECK ===")
    
    android_vendors = {
        '04e8': 'Samsung',
        '18d1': 'Google',
        '22b8': 'Motorola',
        '0489': 'Foxconn',
        '0bb4': 'HTC',
        '1004': 'LG',
        '12d1': 'Huawei',
        '1949': 'Amazon',
        '2717': 'Xiaomi',
        '2a70': 'OnePlus',
        '0fce': 'Sony',
        '2931': 'ZTE',
        '2257': 'OPPO',
        '2187': 'Vivo',
        '0bda': 'Realme'
    }
    
    success, output, error = run_command("lsusb")
    if success:
        found_android = False
        for line in output.split('\n'):
            if line.strip():
                parts = line.split()
                if len(parts) >= 6:
                    vendor_id = parts[5].split(':')[0]
                    if vendor_id in android_vendors:
                        print(f"📱 ANDROID DEVICE FOUND: {android_vendors[vendor_id]} ({vendor_id})")
                        print(f"   Full line: {line}")
                        found_android = True
        
        if not found_android:
            print("No Android vendor IDs found in USB devices")
            print("This suggests no Android devices are connected via USB")
    else:
        print(f"USB vendor check failed: {error}")

def check_system_logs():
    """Check system logs for USB connection events"""
    print("\n=== SYSTEM LOGS CHECK ===")
    
    # Check recent USB events
    success, output, error = run_command("dmesg | grep -i usb | tail -10")
    if success and output.strip():
        print("Recent USB events:")
        for line in output.split('\n'):
            if line.strip():
                print(f"  {line}")
    else:
        print("No recent USB events found")

def check_permissions():
    """Check USB permissions"""
    print("\n=== PERMISSIONS CHECK ===")
    
    # Check if user is in plugdev group
    success, output, error = run_command("groups $USER")
    if success:
        groups = output.strip().split()
        if 'plugdev' in groups:
            print("✓ User is in plugdev group")
        else:
            print("✗ User is NOT in plugdev group")
            print("  Run: sudo usermod -a -G plugdev $USER")
            print("  Then logout and login again")
    
    # Check USB device permissions
    success, output, error = run_command("ls -la /dev/bus/usb/*/* 2>/dev/null | head -5")
    if success and output.strip():
        print("USB device permissions:")
        for line in output.split('\n'):
            if line.strip():
                print(f"  {line}")

def provide_troubleshooting_tips():
    """Provide troubleshooting tips"""
    print("\n=== TROUBLESHOOTING TIPS ===")
    print("If no Android devices are detected, try these steps:")
    print()
    print("1. PHYSICAL CONNECTION:")
    print("   - Use a different USB cable (some cables are charge-only)")
    print("   - Try different USB ports (prefer rear motherboard ports)")
    print("   - Connect directly to computer, not through USB hub")
    print("   - Ensure cable is firmly connected at both ends")
    print()
    print("2. DEVICE SETTINGS:")
    print("   - Enable USB Debugging in Developer Options")
    print("   - Enable OEM Unlocking (if available)")
    print("   - Accept USB debugging authorization on device screen")
    print("   - Try different device modes (ADB, Fastboot, Download)")
    print()
    print("3. DEVICE MODES:")
    print("   - ADB Mode: Settings → Developer Options → USB Debugging")
    print("   - Fastboot Mode: Power off → Volume Down + Power")
    print("   - Download Mode (Samsung): Power off → Volume Down + Bixby + Power")
    print("   - Recovery Mode: Power off → Volume Up + Power")
    print()
    print("4. SYSTEM FIXES:")
    print("   - Restart ADB server: adb kill-server && adb start-server")
    print("   - Check USB drivers on Windows")
    print("   - Add user to plugdev group on Linux")
    print("   - Try different computer if available")

def main():
    """Main device connection check"""
    print("🔍 ANDROID DEVICE CONNECTION VERIFICATION")
    print("=" * 50)
    
    # Run all checks
    check_usb_devices()
    check_android_vendor_ids()
    check_adb_status()
    check_fastboot_status()
    check_permissions()
    check_system_logs()
    provide_troubleshooting_tips()
    
    print("\n" + "=" * 50)
    print("Device connection check completed")

if __name__ == "__main__":
    main()
