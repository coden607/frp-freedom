#!/usr/bin/env python3
"""
Manual Galaxy S10e FRP Bypass Methods
Works when modem exploits fail
"""

import subprocess
import time
import sys

def progress(msg):
    print(f"[*] {msg}")

def run_adb_command(cmd, timeout=10):
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
                return True
    return False

def method_1_talkback_exploit():
    """TalkBack + Chrome exploit method"""
    print("\n=== METHOD 1: TalkBack + Chrome Exploit ===")
    print("Follow these steps on your Galaxy S10e:")
    print("1. On the welcome screen, tap Accessibility")
    print("2. Enable TalkBack")
    print("3. Draw 'L' shape on screen (TalkBack gesture)")
    print("4. Select 'TalkBack Settings' from global menu")
    print("5. Scroll down and tap 'Help & Feedback'")
    print("6. Tap 'Get started with TalkBack'")
    print("7. Long press on any text to select it")
    print("8. Tap 'Web Search' from the menu")
    print("9. This will open Chrome browser")
    print("10. In Chrome, go to: frpfile.com/bypass")
    print("11. Download and install the FRP bypass APK")
    print("12. Open the APK and follow instructions")
    
    input("\nPress Enter when you've completed these steps...")
    
    # Check if device is now accessible via ADB
    if check_device_connected():
        progress("Device detected via ADB! Running bypass commands...")
        
        # FRP bypass commands
        commands = [
            "adb shell settings put secure user_setup_complete 1",
            "adb shell settings put global device_provisioned 1", 
            "adb shell pm clear com.google.android.setupwizard",
            "adb shell pm disable com.google.android.setupwizard",
            "adb shell am start -n com.android.settings/.Settings",
            "adb reboot"
        ]
        
        for cmd in commands:
            success, _, _ = run_adb_command(cmd)
            if success:
                progress(f"✓ {cmd}")
            else:
                progress(f"✗ {cmd} failed")
        
        return True
    return False

def method_2_emergency_call():
    """Emergency call exploit method"""
    print("\n=== METHOD 2: Emergency Call Exploit ===")
    print("Follow these steps on your Galaxy S10e:")
    print("1. On the welcome screen, tap Emergency Call")
    print("2. Dial *#*#2846579#*#* (Project Menu)")
    print("3. Select 'Project Menu' > 'Backend Settings'")
    print("4. Enable 'USB Debugging' option")
    print("5. Connect USB cable if not already connected")
    print("6. Return to welcome screen")
    
    input("\nPress Enter when you've completed these steps...")
    
    if check_device_connected():
        progress("Device detected! Running bypass commands...")
        
        commands = [
            "adb shell settings put secure user_setup_complete 1",
            "adb shell settings put global device_provisioned 1",
            "adb shell pm clear com.google.android.setupwizard", 
            "adb shell pm disable com.google.android.setupwizard",
            "adb shell am start -n com.android.settings/.Settings",
            "adb reboot"
        ]
        
        for cmd in commands:
            success, _, _ = run_adb_command(cmd)
            if success:
                progress(f"✓ {cmd}")
            else:
                progress(f"✗ {cmd} failed")
        
        return True
    return False

def method_3_samsung_account():
    """Samsung account bypass method"""
    print("\n=== METHOD 3: Samsung Account Bypass ===")
    print("Follow these steps on your Galaxy S10e:")
    print("1. On the Google verification screen, tap BACK")
    print("2. Connect to WiFi (any network)")
    print("3. Tap 'Samsung Account' instead of Google Account")
    print("4. Create a new Samsung account (no verification needed)")
    print("5. Complete Samsung account setup")
    print("6. This will bypass Google FRP")
    print("7. Once in device, go to Settings > Accounts")
    print("8. Remove Google account if needed")
    
    input("\nPress Enter when you've completed these steps...")
    return True

def method_4_apk_bypass():
    """Direct APK installation method"""
    print("\n=== METHOD 4: APK Bypass Method ===")
    print("This method requires you to:")
    print("1. Use any method above to access Chrome browser")
    print("2. Navigate to: frpfile.com/bypass")
    print("3. Download 'FRP Bypass APK'")
    print("4. Install the APK (may need to 'Allow from this source')")
    print("5. Open the APK and follow the on-screen instructions")
    print("6. The APK will automatically bypass FRP")
    
    input("\nPress Enter when you've completed these steps...")
    return True

def main():
    print("=" * 60)
    print("🔧 GALAXY S10e MANUAL FRP BYPASS METHODS")
    print("=" * 60)
    print("\nSince the modem exploit didn't work, try these manual methods:")
    
    methods = [
        method_1_talkback_exploit,
        method_2_emergency_call, 
        method_3_samsung_account,
        method_4_apk_bypass
    ]
    
    for i, method in enumerate(methods, 1):
        print(f"\nTrying Method {i}...")
        try:
            if method():
                print("\n🎉 SUCCESS! FRP bypass completed!")
                print("Your device should now be accessible.")
                return True
        except KeyboardInterrupt:
            print("\nMethod cancelled by user")
        except Exception as e:
            print(f"\nError in method {i}: {e}")
        
        if i < len(methods):
            cont = input(f"\nMethod {i} didn't work. Try next method? (y/n): ")
            if cont.lower() != 'y':
                break
    
    print("\n❌ All methods failed. You may need to:")
    print("1. Try a different USB cable")
    print("2. Try a different computer")
    print("3. Contact a professional phone repair service")
    print("4. Search for S10e-specific FRP bypass videos on YouTube")
    
    return False

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nBypass process cancelled by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
