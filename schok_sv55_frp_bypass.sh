#!/bin/bash

# Schok Volt SV55 FRP Bypass Automation Script
# For Android 11
# Requires: ADB installed, USB debugging enabled (or via recovery)
# FULLY AUTOMATED VERSION

set -e

DEVICE_ID=""
SCREEN_WIDTH=1080
SCREEN_HEIGHT=2340

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Check if ADB is installed
check_adb() {
    if ! command -v adb &> /dev/null; then
        print_error "ADB is not installed. Install it with: sudo apt install android-tools-adb"
        exit 1
    fi
    print_info "ADB found"
}

# Wait for device connection
wait_for_device() {
    print_info "Waiting for device connection..."
    print_warning "Make sure USB debugging is enabled on your device"
    print_info "If device is locked, you may need to enable USB debugging via recovery"
    
    adb wait-for-device
    DEVICE_ID=$(adb get-serialno)
    print_info "Device connected: $DEVICE_ID"
}

# Get screen dimensions
get_screen_dimensions() {
    local wm_size=$(adb shell wm size)
    SCREEN_WIDTH=$(echo $wm_size | grep -oP '\d+(?=x)')
    SCREEN_HEIGHT=$(echo $wm_size | grep -oP '(?<=x)\d+')
    print_info "Screen dimensions: ${SCREEN_WIDTH}x${SCREEN_HEIGHT}"
}

# Calculate tap coordinates based on screen size
calc_x() {
    local percentage=$1
    echo $(($SCREEN_WIDTH * $percentage / 100))
}

calc_y() {
    local percentage=$2
    echo $(($SCREEN_HEIGHT * $percentage / 100))
}

# Tap at coordinates
tap() {
    local x=$1
    local y=$2
    print_info "Tapping at ($x, $y)"
    adb shell input tap $x $y
    sleep 0.8
}

# Tap at percentage coordinates
tap_pct() {
    local x_pct=$1
    local y_pct=$2
    local x=$(calc_x $x_pct)
    local y=$(calc_y $y_pct)
    tap $x $y
}

# Swipe gesture
swipe() {
    local x1=$1
    local y1=$2
    local x2=$3
    local y2=$4
    local duration=${5:-300}
    print_info "Swiping from ($x1,$y1) to ($x2,$y2)"
    adb shell input swipe $x1 $y1 $x2 $y2 $duration
    sleep 0.5
}

# Send text input
type_text() {
    local text=$1
    adb shell input text "$text"
    sleep 0.3
}

# Press back button
press_back() {
    print_info "Pressing back"
    adb shell input keyevent KEYCODE_BACK
    sleep 0.5
}

# Press home button
press_home() {
    print_info "Pressing home"
    adb shell input keyevent KEYCODE_HOME
    sleep 0.5
}

# Press enter
press_enter() {
    adb shell input keyevent KEYCODE_ENTER
    sleep 0.3
}

# Enable TalkBack via ADB
enable_talkback() {
    print_info "Enabling TalkBack..."
    adb shell settings put secure enabled_accessibility_services com.google.android.marvin.talkback/com.google.android.marvin.talkback.TalkBackService
    adb shell settings put secure accessibility_enabled 1
    sleep 2
    print_info "TalkBack enabled"
}

# Disable TalkBack via ADB
disable_talkback() {
    print_info "Disabling TalkBack..."
    adb shell settings put secure accessibility_enabled 0
    sleep 1
    print_info "TalkBack disabled"
}

# Launch specific settings
launch_settings() {
    local activity=$1
    print_info "Launching: $activity"
    adb shell am start -a android.intent.action.MAIN -n $activity
    sleep 2
}

# Force stop an app
force_stop_app() {
    local package=$1
    print_info "Force stopping: $package"
    adb shell am force-stop $package
    sleep 1
}

# Disable an app
disable_app() {
    local package=$1
    print_info "Disabling: $package"
    adb shell pm disable-user $package 2>/dev/null || true
    sleep 1
}

# Enable an app
enable_app() {
    local package=$1
    print_info "Enabling: $package"
    adb shell pm enable $package 2>/dev/null || true
    sleep 1
}

# Clear app data
clear_app_data() {
    local package=$1
    print_info "Clearing data for: $package"
    adb shell pm clear $package 2>/dev/null || true
    sleep 1
}

# Wait for UI element (basic implementation)
wait_for_ui() {
    local seconds=$1
    print_info "Waiting $seconds seconds for UI..."
    sleep $seconds
}

# Main FRP bypass process - FULLY AUTOMATED
main_frp_bypass() {
    print_info "Starting FULLY AUTOMATED FRP bypass process for Schok Volt SV55"
    
    echo ""
    print_step "STEP 1: Initial Setup - Tap Start and connect to WiFi"
    print_warning "MANUAL: Please tap 'Start' on device and connect to WiFi, then go back to Welcome screen"
    read -p "Press Enter when device is on Welcome screen with WiFi connected..."
    
    echo ""
    print_step "STEP 2: Navigate to Vision Settings"
    # Tap on accessibility/vision settings area
    tap_pct 50 85
    wait_for_ui 2
    
    # Navigate to TalkBack
    tap_pct 50 50
    wait_for_ui 2
    
    print_step "STEP 3: Enable TalkBack"
    enable_talkback
    wait_for_ui 3
    
    print_step "STEP 4: Access TalkBack Settings"
    # Double tap to select TalkBack Settings
    tap_pct 50 50
    sleep 0.3
    tap_pct 50 50
    wait_for_ui 2
    
    print_step "STEP 5: Draw 'L' gesture to open TalkBack menu"
    # Simulate L gesture with swipe
    local center_x=$(calc_x 50)
    local center_y=$(calc_y 50)
    local start_x=$(calc_x 30)
    local start_y=$(calc_y 30)
    local mid_x=$(calc_x 30)
    local mid_y=$(calc_y 70)
    
    # Draw L: down then right
    swipe $start_x $start_y $mid_x $mid_y 200
    sleep 0.2
    swipe $mid_x $mid_y $center_x $mid_y 200
    wait_for_ui 2
    
    # Tap on TalkBack Settings
    tap_pct 50 50
    wait_for_ui 2
    
    print_step "STEP 6: Suspend TalkBack"
    disable_talkback
    wait_for_ui 2
    
    print_step "STEP 7: Navigate to Braille Keyboard"
    # Scroll down to find Braille Keyboard
    for i in {1..3}; do
        swipe $(calc_x 50) $(calc_y 80) $(calc_x 50) $(calc_y 20) 300
        sleep 0.5
    done
    
    # Tap on Braille Keyboard
    tap_pct 50 60
    wait_for_ui 2
    
    # Tap on Set up Braille Keyboard
    tap_pct 50 70
    wait_for_ui 2
    
    print_step "STEP 8: Select Gboard"
    tap_pct 50 50
    wait_for_ui 2
    
    # Tap on Gboard text/link
    tap_pct 50 60
    wait_for_ui 3
    
    print_step "STEP 9: Navigate to Play Store Settings"
    # Tap 3 dots (top-right)
    tap_pct 95 5
    wait_for_ui 2
    
    # Tap Settings
    tap_pct 50 40
    wait_for_ui 2
    
    # Tap General
    tap_pct 50 30
    wait_for_ui 2
    
    # Tap Notifications
    tap_pct 50 40
    wait_for_ui 2
    
    # Tap Account
    tap_pct 50 50
    wait_for_ui 2
    
    print_step "STEP 10: Access Device Settings via Play Store"
    # Tap Google Play icon
    tap_pct 50 20
    wait_for_ui 2
    
    # Tap Permissions
    tap_pct 50 40
    wait_for_ui 2
    
    # Tap Search icon
    tap_pct 95 10
    wait_for_ui 2
    
    # Type "Settings"
    type_text "Settings"
    wait_for_ui 2
    
    # Tap on Settings app from results
    tap_pct 50 50
    wait_for_ui 3
    
    print_step "STEP 11: Force Stop Android Setup"
    # Navigate to Apps & Notifications
    tap_pct 50 30
    wait_for_ui 2
    
    # Tap See All Apps
    tap_pct 50 60
    wait_for_ui 2
    
    # Tap 3 dots menu
    tap_pct 95 5
    wait_for_ui 2
    
    # Tap Show System
    tap_pct 50 50
    wait_for_ui 2
    
    # Search for Android Setup
    tap_pct 95 10
    type_text "Android Setup"
    wait_for_ui 2
    
    # Tap on Android Setup
    tap_pct 50 50
    wait_for_ui 2
    
    # Tap Force Stop
    tap_pct 50 70
    wait_for_ui 1
    
    # Confirm Force Stop
    tap_pct 50 60
    wait_for_ui 1
    
    # ADB force stop as backup
    force_stop_app "com.google.android.setupwizard"
    
    print_step "STEP 12: Disable Google Play Services"
    press_back
    wait_for_ui 1
    
    # Search for Google Play Services
    tap_pct 95 10
    type_text "Google Play Services"
    wait_for_ui 2
    
    # Tap on Google Play Services
    tap_pct 50 50
    wait_for_ui 2
    
    # Tap Disable
    tap_pct 50 60
    wait_for_ui 1
    
    # Confirm Disable
    tap_pct 50 60
    wait_for_ui 1
    
    # ADB disable as backup
    disable_app "com.google.android.gms"
    force_stop_app "com.google.android.gms"
    
    print_step "STEP 13: Return to Welcome Screen"
    # Press back multiple times
    for i in {1..5}; do
        press_back
        wait_for_ui 1
    done
    
    print_step "STEP 14: Re-enable TalkBack"
    enable_talkback
    wait_for_ui 3
    
    # Navigate to Vision Settings again
    tap_pct 50 85
    wait_for_ui 2
    tap_pct 50 50
    wait_for_ui 2
    
    # Access TalkBack Settings
    tap_pct 50 50
    sleep 0.3
    tap_pct 50 50
    wait_for_ui 2
    
    # Draw L gesture again
    swipe $start_x $start_y $mid_x $mid_y 200
    sleep 0.2
    swipe $mid_x $mid_y $center_x $mid_y 200
    wait_for_ui 2
    
    tap_pct 50 50
    wait_for_ui 2
    
    disable_talkback
    wait_for_ui 2
    
    print_step "STEP 15: Re-access Google Play via Braille Keyboard"
    # Navigate to Braille Keyboard again
    for i in {1..3}; do
        swipe $(calc_x 50) $(calc_y 80) $(calc_x 50) $(calc_y 20) 300
        sleep 0.5
    done
    
    tap_pct 50 60
    wait_for_ui 2
    tap_pct 50 70
    wait_for_ui 2
    tap_pct 50 50
    wait_for_ui 2
    tap_pct 50 60
    wait_for_ui 3
    
    print_step "STEP 16: Navigate to Settings Again"
    # 3 dots > Settings > General > Notifications > Account
    tap_pct 95 5
    wait_for_ui 2
    tap_pct 50 40
    wait_for_ui 2
    tap_pct 50 30
    wait_for_ui 2
    tap_pct 50 40
    wait_for_ui 2
    tap_pct 50 50
    wait_for_ui 2
    
    # Google Play icon > Permissions > Search > Settings
    tap_pct 50 20
    wait_for_ui 2
    tap_pct 50 40
    wait_for_ui 2
    tap_pct 95 10
    wait_for_ui 2
    type_text "Settings"
    wait_for_ui 2
    tap_pct 50 50
    wait_for_ui 3
    
    print_step "STEP 17: Re-enable Google Play Services"
    # Navigate to Apps
    tap_pct 50 30
    wait_for_ui 2
    tap_pct 50 60
    wait_for_ui 2
    tap_pct 95 5
    wait_for_ui 2
    tap_pct 50 50
    wait_for_ui 2
    
    # Search for Google Play Services
    tap_pct 95 10
    type_text "Google Play Services"
    wait_for_ui 2
    tap_pct 50 50
    wait_for_ui 2
    
    # Tap Enable
    tap_pct 50 60
    wait_for_ui 2
    
    # ADB enable as backup
    enable_app "com.google.android.gms"
    
    print_step "STEP 18: Complete Setup"
    # Return to Welcome screen
    for i in {1..5}; do
        press_back
        wait_for_ui 1
    done
    
    # Tap Start
    tap_pct 50 50
    wait_for_ui 3
    
    # On Copy Apps & Data, tap Back
    press_back
    wait_for_ui 2
    
    # On Connect to WiFi, tap Set up Offline
    tap_pct 50 70
    wait_for_ui 2
    tap_pct 50 60
    wait_for_ui 2
    
    print_info "FRP bypass automation complete!"
    print_warning "Please complete the remaining setup steps on the device"
    print_info "If the bypass was successful, you should now have access to the device"
}

# Alternative: Quick ADB method (if device allows)
quick_adb_method() {
    print_info "Attempting quick ADB method..."
    
    # Try to bypass FRP via ADB commands
    print_info "Disabling setup wizard..."
    adb shell pm disable-user com.google.android.setupwizard
    
    print_info "Enabling Google Play Services..."
    adb shell pm enable com.google.android.gms
    
    print_info "Clearing Google Play Services data..."
    adb shell pm clear com.google.android.gms
    
    print_info "Attempting to launch home screen..."
    adb shell am start -a android.intent.action.MAIN -c android.intent.category.HOME
    
    print_warning "If this worked, you should be on the home screen."
    print_warning "If not, proceed with the manual method above."
}

# Main execution
main() {
    echo "=========================================="
    echo "  Schok Volt SV55 FRP Bypass Tool"
    echo "  Android 11 - Linux ADB Automation"
    echo "=========================================="
    echo ""
    
    check_adb
    wait_for_device
    get_screen_dimensions
    
    echo ""
    echo "Choose method:"
    echo "1) Full manual automation (recommended)"
    echo "2) Quick ADB method (may not work on all devices)"
    read -p "Enter choice (1 or 2): " choice
    
    if [ "$choice" = "2" ]; then
        quick_adb_method
    else
        main_frp_bypass
    fi
    
    echo ""
    print_info "Script completed!"
    print_warning "If FRP is not bypassed, you may need to repeat the process"
    print_warning "or try alternative methods like UnlockTool"
}

main "$@"
