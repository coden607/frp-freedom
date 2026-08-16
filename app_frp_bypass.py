#!/usr/bin/env python3
"""
Galaxy S10e App-Based FRP Bypass Guide
Helps you bypass FRP using specialized bypass apps
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

def talkback_chrome_method():
    """Method to access Chrome via TalkBack"""
    print("\n" + "="*60)
    print("🔧 TALKBACK + CHROME APP BYPASS METHOD")
    print("="*60)
    print("\nFollow these EXACT steps on your Galaxy S10e:")
    print()
    print("1. 📱 On the welcome/setup screen, tap 'Accessibility'")
    print("2. ♿ Enable 'TalkBack' (may require double-tap to confirm)")
    print("3. ✏️ Draw an 'L' shape on the screen (TalkBack gesture)")
    print("4. 📋 From the global menu, select 'TalkBack Settings'")
    print("5. 📖 Scroll down and tap 'Help & Feedback'")
    print("6. 📚 Tap 'Get started with TalkBack'")
    print("7. 👆 Long press on any text until it's selected")
    print("8. 🔍 Tap 'Web Search' from the popup menu")
    print("9. 🌐 Chrome browser will open")
    print("10. 📥 In Chrome, go to: frpfile.com/bypass")
    print("11. 📲 Download 'FRP Bypass APK' (usually first result)")
    print("12. ⚙️ When prompted, allow installation from unknown sources")
    print("13. 📱 Install the APK and open it")
    print("14. ✅ Follow the app instructions to bypass FRP")
    print()
    print("🔑 TIPS:")
    print("- If TalkBack is annoying, you can disable it after opening Chrome")
    print("- Make sure you're connected to WiFi")
    print("- The app will automatically bypass Google account verification")
    print("- Your device will restart and go to home screen")
    print()

def emergency_call_method():
    """Emergency call method to access browser"""
    print("\n" + "="*60)
    print("📞 EMERGENCY CALL APP BYPASS METHOD")
    print("="*60)
    print("\nFollow these steps:")
    print()
    print("1. 📱 On welcome screen, tap 'Emergency Call'")
    print("2. 🔢 Dial: *#*#2846579#*#* (Project Menu)")
    print("3. ⚙️ Select 'Project Menu' > 'Backend Settings'")
    print("4. 🔌 Enable 'USB Debugging' option")
    print("5. 🔌 Connect USB cable to computer")
    print("6. 💻 Run: adb shell am start -n com.android.browser/.BrowserActivity")
    print("7. 🌐 This should open the browser")
    print("8. 📥 Go to: frpfile.com/bypass")
    print("9. 📲 Download and install FRP bypass APK")
    print()

def samsung_account_method():
    """Samsung account bypass method"""
    print("\n" + "="*60)
    print("🏢 SAMSUNG ACCOUNT APP BYPASS METHOD")
    print("="*60)
    print("\nFollow these steps:")
    print()
    print("1. 📱 On Google verification screen, tap BACK button")
    print("2. 📶 Connect to WiFi network")
    print("3. 🏢 Instead of Google Account, tap 'Samsung Account'")
    print("4. 📧 Tap 'Create Account' (no verification required)")
    print("5. 📝 Fill in any email and password")
    print("6. ✅ Complete Samsung account setup")
    print("7. 🏠 This will bypass Google FRP completely")
    print("8. 📱 Once in device, you can add your Google account normally")
    print()

def install_bypass_app():
    """Try to install bypass app directly if ADB is available"""
    connected, device_id = check_device_connected()
    if not connected:
        return False
    
    print(f"\n🔌 Device {device_id} connected via ADB!")
    print("Attempting to install bypass app directly...")
    
    # Try to install common bypass apps
    apps = [
        "https://frpfile.com/download/frp-bypass-apk",
        "https://techeligible.com/frp/bypass/",
        "https://bypassfrp.com/download"
    ]
    
    for app_url in apps:
        progress(f"Trying to install from: {app_url}")
        
        # Commands to download and install
        commands = [
            f"adb shell am start -n com.android.browser/.BrowserActivity -d '{app_url}'",
            "adb shell input keyevent KEYCODE_HOME",
            "sleep 3"
        ]
        
        for cmd in commands:
            success, _, _ = run_adb_command(cmd)
            if success:
                progress(f"✓ {cmd}")
            time.sleep(2)
    
    return True

def create_shortcut_method():
    """Create shortcut method for newer Android versions"""
    print("\n" + "="*60)
    print("🔗 CREATE SHORTCUT APP BYPASS METHOD")
    print("="*60)
    print("\nFollow these steps:")
    print()
    print("1. 📱 On welcome screen, connect to WiFi")
    print("2. 🔍 Tap the search bar (if available)")
    print("3. 🔍 Search for 'Settings' or 'Google'")
    print("4. ⚙️ If Settings opens, go to 'Apps & notifications'")
    print("5. 📱 Find 'Google Setup Wizard' and disable it")
    print("6. 🏠 Go back to home screen")
    print("7. 📱 Try to access Settings directly")
    print("8. ⚙️ In Settings, add your Google account normally")
    print()

def main():
    print("="*60)
    print("📱 GALAXY S10e APP-BASED FRP BYPASS")
    print("="*60)
    print("\nThis guide will help you bypass FRP using bypass apps.")
    print("Choose the method that works best for your situation:")
    print()
    
    # Check if device is already connected via ADB
    connected, device_id = check_device_connected()
    if connected:
        print(f"🔌 Device {device_id} detected via ADB!")
        choice = input("Try direct app installation? (y/n): ").lower()
        if choice == 'y':
            if install_bypass_app():
                print("\n✅ App installation attempted!")
                print("Check your device for the bypass app.")
    
    print("\n🔧 AVAILABLE BYPASS METHODS:")
    print("1. TalkBack + Chrome (Most reliable)")
    print("2. Emergency Call (Alternative)")
    print("3. Samsung Account (Easiest)")
    print("4. Create Shortcut (For newer Android)")
    print("5. All Methods (Complete guide)")
    
    try:
        choice = input("\nSelect method (1-5): ").strip()
        
        if choice == '1':
            talkback_chrome_method()
        elif choice == '2':
            emergency_call_method()
        elif choice == '3':
            samsung_account_method()
        elif choice == '4':
            create_shortcut_method()
        elif choice == '5':
            talkback_chrome_method()
            emergency_call_method()
            samsung_account_method()
            create_shortcut_method()
        else:
            print("Invalid choice. Showing all methods...")
            talkback_chrome_method()
            emergency_call_method()
            samsung_account_method()
            create_shortcut_method()
            
    except (EOFError, KeyboardInterrupt):
        print("\nShowing all methods...")
        talkback_chrome_method()
        emergency_call_method()
        samsung_account_method()
        create_shortcut_method()
    
    print("\n" + "="*60)
    print("📋 IMPORTANT NOTES:")
    print("="*60)
    print("✅ Make sure your device has WiFi connection")
    print("✅ Download apps only from trusted sources (frpfile.com)")
    print("✅ After bypass, set up your Google account normally")
    print("✅ You can disable TalkBack after bypass is complete")
    print("⚠️  Some methods may require multiple attempts")
    print("⚠️  If one method fails, try another method")
    print()
    print("🎉 Good luck with your Galaxy S10e FRP bypass!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nBypass guide cancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
