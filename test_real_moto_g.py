import time
from src.bypass.auto_bypass_manager_enhanced import AutoBypassManager
from src.core.device_manager import DeviceManager, DeviceInfo
from src.core.config import Config
from src.bypass.bypass_manager import BypassManager

def main():
    print("Testing Moto G Bypass Workflow with Real Device")
    print("=" * 50)

    # Initialize components
    config = Config()
    device_manager = DeviceManager(config)
    bypass_manager = BypassManager(config, device_manager)
    auto_bypass = AutoBypassManager(config, device_manager, bypass_manager)

    print("Scanning for connected devices...")
    devices = device_manager.scan_devices()

    if not devices:
        print("No devices detected!")
        return

    print(f"Found {len(devices)} device(s):")
    for device in devices:
        print(f"  - {device.brand} {device.model} ({device.connection_type})")

    # Process each device
    for device in devices:
        if 'motorola' in device.model.lower() or 'moto g' in device.model.lower():
            print(f"\nProcessing Moto G device: {device.serial}")
            optimal_mode = auto_bypass._determine_optimal_mode(device)
            print(f"Optimal mode for this device: {optimal_mode}")

            if optimal_mode != device.connection_type:
                print(f"Switching from {device.connection_type} to {optimal_mode} mode...")
                switched_device = auto_bypass._switch_device_mode(device, optimal_mode)
                if switched_device:
                    print(f"Successfully switched to {optimal_mode} mode!")
                    print(f"New device state: {switched_device.connection_type}")
                else:
                    print("Failed to switch device mode")
            else:
                print(f"Device already in optimal mode: {optimal_mode}")

            # Scan again to see current state
            time.sleep(3)
            devices_after = device_manager.scan_devices()
            for d in devices_after:
                if d.serial == device.serial:
                    print(f"Current device state: {d.connection_type}")
                    break

if __name__ == '__main__':
    main()