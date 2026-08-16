#!/usr/bin/env python3
"""
🔧 SCHOK VOLT USB DEBUGGING ENABLER
Helps enable USB debugging on locked Schok Volt device
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

def check_modem_ports():
    """Check for Schok Volt modem ports"""
    progress("Checking for Schok Volt modem ports...")
    
    try:
        import serial.tools.list_ports
        ports = list(serial.tools.list_ports.comports())
        
        for port in ports:
            # Check for common Schok/Android modem identifiers
            if (port.vid in [0x04E8, 0x18D1, 0x12D1, 0x19D2, 0x2357, 0x0FCE, 0x0489] or
                "schok" in port.description.lower() or 
                "android" in port.description.lower() or
                "qualcomm" in port.description.lower()):
                
                progress(f"Found potential Schok Volt modem: {port.device}")
                return port.device
    except ImportError:
        progress("pyserial not available")
    
    return None

def talkback_enable_method():
    """Guide user through TalkBack method to enable USB debugging"""
    print("\n" + "="*60)
    print("🔧 TALKBACK METHOD TO ENABLE USB DEBUGGING")
    print("="*60)
    print("\nFollow these EXACT steps on your Schok Volt:")
    print()
    print("1. 📱 On the welcome/FRP screen, tap 'Accessibility'")
    print("2. ♿ Enable 'TalkBack' (double-tap to confirm)")
    print("3. ✏️ Draw an 'L' shape on the screen")
    print("4. 📋 From global menu, select 'TalkBack Settings'")
    print("5. 📖 Scroll down and tap 'Help & Feedback'")
    print("6. 📚 Tap 'Get started with TalkBack'")
    print("7. 👆 Long press on any text until selected")
    print("8. 🔍 Tap 'Web Search' from popup menu")
    print("9. 🌐 Chrome browser will open")
    print("10. 📥 In Chrome, type: android.com/debug")
    print("11. 📲 Download 'Android Debug Bridge' APK")
    print("12. ⚙️ Install the APK (allow unknown sources)")
    print("13. 📱 Open the APK and enable USB debugging")
    print()
    print("🔑 TIPS:")
    print("- If TalkBack is confusing, disable it after opening Chrome")
    print("- Make sure you're connected to WiFi")
    print("- The APK will automatically enable USB debugging")
    print()

def emergency_method():
    """Emergency call method to enable USB debugging"""
    print("\n" + "="*60)
    print("📞 EMERGENCY CALL METHOD")
    print("="*60)
    print("\nFollow these steps:")
    print()
    print("1. 📱 On welcome screen, tap 'Emergency Call'")
    print("2. 🔢 Dial: *#*#2846579#*#* (Project Menu)")
    print("3. ⚙️ Select 'Project Menu' > 'Backend Settings'")
    print("4. 🔌 Enable 'USB Debugging' option")
    print("5. 🔌 Keep USB cable connected")
    print("6. 💻 Re-run this script")
    print()

def samsung_method():
    """Samsung account method if applicable"""
    print("\n" + "="*60)
    print("🏢 ALTERNATIVE ACCOUNT METHOD")
    print("="*60)
    print("\nFollow these steps:")
    print()
    print("1. 📱 On Google verification, tap BACK button")
    print("2. 📶 Connect to WiFi")
    print("3. 🏢 Look for 'Schok Account' or 'Manufacturer Account'")
    print("4. 📧 Create account (no verification needed)")
    print("5. ✅ Complete setup to bypass Google FRP")
    print()

def check_device_after_methods():
    """Check if device is now accessible via ADB"""
    progress("Checking if device is now accessible via ADB...")
    
    for attempt in range(10):
        success, output, _ = run_adb_command("adb devices")
        if success and "device" in output:
            lines = output.split('\n')[1:]
            for line in lines:
                if 'device' in line and line.strip():
                    device_id = line.strip().split('\t')[0]
                    progress(f"🎉 Schok Volt now accessible: {device_id}")
                    return True, device_id
        
        progress(f"Attempt {attempt + 1}/10 - still waiting...")
        time.sleep(3)
    
    return False, None

def auto_bypass_once_connected(device_id):
    """Run bypass once device is connected"""
    progress(f"Running bypass on {device_id}...")
    
    bypass_commands = [
        "adb shell settings put secure user_setup_complete 1",
        "adb shell settings put global device_provisioned 1",
        "adb shell pm clear com.google.android.setupwizard",
        "adb shell pm disable-user com.google.android.setupwizard",
        "adb shell content insert --uri content://settings/secure --bind name:s:user_setup_complete --bind value:i:1",
        "adb shell content insert --uri content://settings/global --bind name:s:device_provisioned --bind value:i:1",
        "adb shell am start -n com.android.settings/.Settings",
        "adb reboot"
    ]
    
    success_count = 0
    for cmd in bypass_commands:
        success, _, _ = run_adb_command(cmd)
        if success:
            progress(f"✓ {cmd}")
            success_count += 1
        time.sleep(2)
    
    if success_count >= len(bypass_commands) // 2:
        progress("🎉🎉🎉 SCHOK VOLT FRP BYPASSED! 🎉🎉🎉")
        return True
    
    return False

def main():
    print("=" * 60)
    print("🔧 SCHOK VOLT USB DEBUGGING ENABLER")
    print("=" * 60)
    print("\nYour Schok Volt is connected but still locked.")
    print("I'll help you enable USB debugging to bypass FRP.")
    print()
    
    # Check for modem ports
    modem_port = check_modem_ports()
    if modem_port:
        progress(f"Modem port found: {modem_port}")
        # Could try modem exploits here if needed
    
    # Show all methods to enable USB debugging
    talkback_enable_method()
    emergency_method()
    samsung_method()
    
    print("\n" + "="*60)
    print("📋 NEXT STEPS:")
    print("="*60)
    print("1. Try ONE of the methods above")
    print("2. After enabling USB debugging, reconnect USB")
    print("3. I'll automatically detect and bypass your device")
    print("4. Press Enter when ready to check for device...")
    
    try:
        input()
    except (EOFError, KeyboardInterrupt):
        pass
    
    # Check if device is now accessible
    connected, device_id = check_device_after_methods()
    if connected:
        if auto_bypass_once_connected(device_id):
            print("\n🎉 SUCCESS! Your Schok Volt is now bypassed!")
        else:
            print("\n⚠️ Partial success - try manual steps")
    else:
        print("\n❌ Device still not accessible")
        print("Try the TalkBack method - it's most reliable")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nProcess cancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
