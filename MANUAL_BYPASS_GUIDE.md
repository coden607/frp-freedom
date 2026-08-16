# Manual FRP Bypass Guide for TCL Devices

This guide walks you through manually bypassing FRP on your TCL device when the automated system cannot do it automatically.

## When to Use This Guide

Use this guide when:
- The auto_bypass.py script detects your device but fails to bypass
- The system reports "ADB not enabled" or "MTP device requires manual ADB enablement"
- Emergency call exploits fail automatically

## Prerequisites

- TCL device connected via USB
- Device in MTP mode (file transfer)
- Computer with adb tools installed (included in this project)
- Patience - manual bypass requires careful timing

---

## Method 1: Enable USB Debugging Manually

### Step 1: Access Emergency Dialer
1. On your TCL device, go to the lock screen or setup wizard
2. Tap "Emergency" or "Emergency Call"
3. The dialer will open

### Step 2: Use Service Menu Codes
**Note:** Many modern TCL devices block service menu codes from the emergency dialer. If you see "not an emergency number", skip to Method 3 (TalkBack).

Try these codes one at a time by dialing them:

```
*#*#4636#*#*    (Testing menu)
*#*#7378423#*#*  (Service menu)
*#0*#            (Service menu)
```

If these don't work (show "not an emergency number"), proceed to Method 3.

### Step 3: Enable Developer Options
If a service menu opens:
1. Look for "Developer Options" or "USB Debugging"
2. Enable "USB Debugging" or "ADB Debugging"
3. Accept the authorization prompt on your device

### Step 4: Verify ADB Connection
Run this command on your computer:
```bash
adb devices
```

You should see your device listed as "device" (not "unauthorized").

---

## Method 2: Emergency Call Bypass (Manual)

### Step 1: Open Emergency Dialer
1. On the lock screen, tap "Emergency"
2. Dial: `*#*#4636#*#*`

### Step 2: Navigate to Settings
1. In the testing menu, look for "Settings" or "System"
2. Tap to access device settings

### Step 3: Remove Google Account
1. Go to Settings > Accounts
2. Select the Google account
3. Tap "Remove account"
4. Confirm removal

### Step 4: Restart Device
1. Power off the device
2. Power it back on
3. Complete setup without adding a Google account

---

## Method 3: TalkBack Bypass (Manual)

### Step 1: Enable TalkBack
1. On the lock screen, tap the emergency button
2. Tap the emergency call button multiple times (7-10 times)
3. TalkBack should be enabled

### Step 2: Use TalkBack to Access Settings
1. With TalkBack enabled, swipe down with two fingers
2. Tap "Settings" when it appears
3. Navigate to Accessibility > TalkBack
4. Use gestures to navigate through menus

### Step 3: Enable USB Debugging via TalkBack
1. Navigate to Settings > About Phone
2. Tap "Build Number" 7 times to enable Developer Options
3. Go back to Settings > Developer Options
4. Enable "USB Debugging"
5. Accept the authorization prompt

### Step 4: Run Auto Bypass
Once USB debugging is enabled, run:
```bash
python3 auto_bypass.py
```

The system will now be able to execute the TCL-specific bypass methods.

---

## Method 4: FRP Bypass APK (Manual)

### Step 1: Download FRP Bypass APK
Download a compatible FRP bypass APK for TCL devices from a trusted source.

### Step 2: Enable USB Debugging
Follow Method 1 or Method 3 to enable USB debugging.

### Step 3: Install APK via ADB
```bash
adb install frp_bypass.apk
```

### Step 4: Run the APK
1. On your device, open the FRP Bypass app
2. Follow the on-screen instructions
3. The app will attempt to bypass FRP

---

## After Manual Steps: Run Auto Bypass

Once you've enabled USB debugging manually, run the automated system:

```bash
cd /home/coden607/Projects/frp-freedom
python3 auto_bypass.py
```

The system will now:
- Detect your device via ADB
- Apply TCL-specific bypass methods
- Attempt to remove FRP lock

---

## Troubleshooting

### Device shows as "unauthorized"
- Check your device screen for authorization prompt
- Tap "Allow" or "OK" on the device
- Re-run `adb devices` to verify

### Service menu codes don't work
- Try different codes from the list
- Some TCL models use different codes
- Check online for your specific model's service menu code

### TalkBack not enabling
- Ensure you're tapping emergency call button rapidly (7-10 times)
- Try different tap patterns
- Some devices require different methods to enable TalkBack

### ADB commands fail
- Ensure USB debugging is enabled
- Check USB cable (use original if possible)
- Try different USB port
- Restart adb server: `adb kill-server && adb start-server`

---

## TCL-Specific Tips

- TCL devices often respond to `*#*#4636#*#*` for testing menu
- Some TCL models require you to be in setup wizard for emergency exploits
- The "T & A Mobile Phones" vendor ID indicates a TCL/Alcatel device
- Alcatel devices (owned by TCL) use similar bypass methods

---

## Next Steps After Successful Bypass

1. **Remove Google Account**: Go to Settings > Accounts and remove the FRP-locked account
2. **Factory Reset**: Perform a factory reset to clean the device
3. **Set Up Fresh**: Complete setup with your own Google account
4. **Disable FRP**: If you want to avoid FRP in the future, you can disable it (not recommended for security)

---

## Contact/Support

If these methods don't work for your specific TCL model:
- Check your exact model number in Settings > About Phone
- Search for "[Your Model] FRP bypass" online
- Some newer Android versions may require different methods

---

**Note**: This guide is for educational purposes and for devices you own. Only bypass FRP on devices you have legitimate access to.
