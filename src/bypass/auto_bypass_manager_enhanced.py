#!/usr/bin/env python3
"""
Enhanced Auto Bypass Manager for FRP Freedom
Automatically detects devices, switches modes, and executes best bypass methods
"""

import logging
import time
from typing import Dict, List, Optional, Callable, Any
from threading import Thread

from ..core.device_manager import DeviceManager, DeviceInfo
from ..core.config import Config
from .bypass_manager import BypassManager, BypassMethod
from .types import BypassResult

class AutoBypassManager:
    """Automatically detects devices and executes best bypass methods"""

    def __init__(self, config: Config, device_manager: DeviceManager, bypass_manager: BypassManager):
        self.config = config
        self.device_manager = device_manager
        self.bypass_manager = bypass_manager
        self.logger = logging.getLogger(__name__)

        self.auto_mode_enabled = self.config.get('auto_bypass.enabled', False)
        self.running = False
        self.auto_thread: Optional[Thread] = None
        self.progress_callback: Optional[Callable[[str, int], None]] = None

    def start_auto_bypass(self, progress_callback: Optional[Callable[[str, int], None]] = None) -> Dict[str, Any]:
        """Start automatic bypass process"""
        self.progress_callback = progress_callback
        self.running = True

        self._update_progress("Starting automatic bypass process", 5)

        try:
            # Step 1: Detect devices
            devices = self._auto_detect_devices()
            if not devices:
                return {
                    'result': BypassResult.FAILED,
                    'message': 'No devices detected',
                    'details': {}
                }

            self._update_progress(f"Found {len(devices)} device(s)", 15)

            # Step 2: Process each device
            results = []
            for device in devices:
                self.logger.info(f"Processing device: {device.brand} {device.model}")
                result = self._process_device(device)
                results.append(result)

            # Return overall result
            success_count = sum(1 for r in results if r['result'] == BypassResult.SUCCESS)

            return {
                'result': BypassResult.SUCCESS if success_count > 0 else BypassResult.FAILED,
                'message': f'Processed {len(devices)} device(s), {success_count} successful',
                'details': {'results': results}
            }

        except Exception as e:
            self.logger.error(f"Auto bypass failed: {e}")
            return {
                'result': BypassResult.FAILED,
                'message': f'Auto bypass error: {str(e)}',
                'details': {'error': str(e)}
            }
        finally:
            self.running = False

    def _auto_detect_devices(self) -> List[DeviceInfo]:
        """Auto-detect connected devices"""
        self._update_progress("Scanning for devices...", 10)

        # Get all connected devices
        devices = self.device_manager.scan_devices()

        if not devices:
            self.logger.warning("No devices detected in current mode")
            return []

        # Try alternative detection methods if no devices found
        if not devices:
            self.logger.info("Trying alternative device detection methods...")
            # Try fastboot devices
            fastboot_devices = self.device_manager.scan_fastboot_devices()
            if fastboot_devices:
                devices.extend(fastboot_devices)
            # Try brom devices
            brom_devices = self.device_manager.scan_brom_devices()
            if brom_devices:
                devices.extend(brom_devices)
            # Try edl devices
            edl_devices = self.device_manager.scan_edl_devices()
            if edl_devices:
                devices.extend(edl_devices)

        self.logger.info(f"Detected {len(devices)} device(s)")
        for device in devices:
            self.logger.info(f"  - {device.brand} {device.model} ({device.connection_type})")

        return devices

    def _process_device(self, device: DeviceInfo) -> Dict[str, Any]:
        """Process a single device: switch mode if needed, then bypass"""
        self._update_progress(f"Processing {device.brand} {device.model}", 20)

        # Step 1: Determine if mode switching is needed
        optimal_mode = self._determine_optimal_mode(device)

        if optimal_mode != device.connection_type:
            self.logger.info(f"Device in {device.connection_type} mode, switching to {optimal_mode}")
            self._update_progress(f"Switching to {optimal_mode} mode", 25)

            switched_device = self._switch_device_mode(device, optimal_mode)
            if not switched_device:
                return {
                    'result': BypassResult.FAILED,
                    'message': f'Failed to switch to {optimal_mode} mode',
                    'details': {'device': device.serial}
                }
            device = switched_device
        else:
            self.logger.info(f"Device already in optimal mode: {optimal_mode}")

        # Step 2: Get best bypass method
        self._update_progress("Selecting best bypass method", 40)
        best_method = self._select_best_bypass_method(device)

        if not best_method:
            return {
                'result': BypassResult.FAILED,
                'message': 'No compatible bypass method found',
                'details': {'device': device.serial}
            }

        self.logger.info(f"Selected method: {best_method.name} (success rate: {best_method.success_rate:.1%})")
        self._update_progress(f"Executing {best_method.name}", 50)

        # Step 3: Execute bypass
        result = self.bypass_manager.execute_bypass(device, best_method.name, self.progress_callback)

        # Step 4: If failed, try next best method
        if result['result'] != BypassResult.SUCCESS:
            self.logger.warning(f"Method {best_method.name} failed, trying next best")
            self._update_progress("Primary method failed, trying alternative", 60)

            alternative_methods = self.bypass_manager.get_recommended_methods(device)
            alternative_methods = [m for m in alternative_methods if m.name != best_method.name]

            for alt_method in alternative_methods[:2]:  # Try up to 2 alternatives
                self.logger.info(f"Trying alternative: {alt_method.name}")
                self._update_progress(f"Trying {alt_method.name}", 65)

                result = self.bypass_manager.execute_bypass(device, alt_method.name, self.progress_callback)
                if result['result'] == BypassResult.SUCCESS:
                    break

        return result

    def _determine_optimal_mode(self, device: DeviceInfo) -> str:
        """Determine the optimal mode for bypass based on device"""
        self.logger.info(f"Determining optimal mode for {device.serial} ({device.connection_type})")

        # Handle unauthorized devices (FRP locked) - prioritize interface methods
        if device.connection_type == 'adb_unauthorized':
            self.logger.info("Device is unauthorized - prioritizing interface bypass methods")
            return 'adb'  # Try to work with ADB first

        # Handle restricted devices - prioritize interface methods
        if device.connection_type == 'adb_restricted':
            self.logger.info("Device has restricted access - prioritizing interface bypass methods")
            return 'adb'

        # Handle Fastboot mode - stay in Fastboot for hardware bypass
        if device.connection_type == 'fastboot':
            self.logger.info("Device in Fastboot mode - staying for hardware bypass methods")
            return 'fastboot'

        # Handle Download mode - stay in download mode for MediaTek/Samsung
        if device.connection_type == 'download':
            self.logger.info("Device in Download mode - staying for MediaTek/Samsung bypass")
            return 'download'

        # Handle Modem mode - try to switch to ADB
        if device.connection_type == 'modem':
            self.logger.info("Device in Modem mode - attempting to switch to ADB")
            return 'adb'

        # MediaTek devices: download mode is best
        if device.chipset == 'mediatek':
            self.logger.info("MediaTek device - download mode is optimal")
            if device.connection_type != 'download':
                return 'download'
            return 'download'

        # Samsung devices: download mode or ADB
        if device.manufacturer.lower() == 'samsung':
            self.logger.info("Samsung device - download mode or ADB is optimal")
            if device.connection_type == 'adb':
                # Check if we can work with ADB
                return 'adb'
            else:
                return 'download'

        # Moto G devices: brom mode or bootloader mode is best
        if 'motorola' in device.model.lower() or 'moto g' in device.model.lower() or device.manufacturer.lower() == 'motorola':
            self.logger.info("Moto G device detected - brom mode or bootloader mode is optimal")
            if device.connection_type == 'brom':
                return 'brom'
            elif device.connection_type == 'fastboot':
                return 'fastboot'
            elif device.connection_type == 'mtp':
                return 'fastboot'  # Try to switch to Fastboot first from MTP
            return 'brom'

        # Qualcomm devices: EDL mode is best, fallback to fastboot
        if device.chipset == 'qualcomm':
            self.logger.info("Qualcomm device - EDL mode is optimal")
            if device.connection_type == 'edl':
                return 'edl'
            elif device.connection_type == 'fastboot':
                return 'edl'
            elif device.connection_type == 'adb':
                return 'edl'
            return 'edl'  # Default to EDL for Qualcomm

        # Google Pixel devices: fastboot is best, but MTP can try interface methods
        if device.manufacturer.lower() == 'google' or 'google' in device.model.lower() or 'pixel' in device.model.lower():
            self.logger.info("Google Pixel device detected")
            if device.connection_type == 'fastboot':
                return 'fastboot'
            elif device.connection_type == 'mtp':
                return 'adb'  # Try interface methods from MTP
            return 'fastboot'

        # For other devices, try to use current mode if it's ADB
        if device.connection_type == 'adb':
            self.logger.info("Using current ADB connection")
            return 'adb'

        # Default: try to switch to ADB mode
        self.logger.info("Defaulting to ADB mode for bypass")
        return 'adb'

    def _switch_device_mode(self, device: DeviceInfo, target_mode: str) -> Optional[DeviceInfo]:
        """Switch device to target mode"""
        try:
            self.logger.info(f"Attempting to switch {device.serial} to {target_mode} mode")

            # MediaTek: switch to download mode
            if target_mode == 'download' and device.chipset == 'mediatek':
                if device.connection_type == 'adb':
                    # Try ADB reboot to download
                    success, _ = self.device_manager.execute_adb_command(
                        device.serial, ['reboot', 'download']
                    )
                    if success:
                        time.sleep(5)
                        # Re-scan for device in new mode
                        new_devices = self.device_manager.scan_devices()
                        for new_device in new_devices:
                            if new_device.serial == device.serial and new_device.connection_type == 'download':
                                return new_device

            # Samsung: switch to download mode
            if target_mode == 'download' and device.manufacturer.lower() == 'samsung':
                if device.connection_type == 'adb':
                    success, _ = self.device_manager.execute_adb_command(
                        device.serial, ['reboot', 'download']
                    )
                    if success:
                        time.sleep(5)
                        # Re-scan for device in new mode
                        new_devices = self.device_manager.scan_devices()
                        for new_device in new_devices:
                            if new_device.serial == device.serial and new_device.connection_type == 'download':
                                return new_device
                elif device.connection_type == 'fastboot':
                    success, _ = self.device_manager.execute_fastboot_command(
                        device.serial, ['reboot-download']
                    )
                    if success:
                        time.sleep(5)
                        new_devices = self.device_manager.scan_devices()
                        for new_device in new_devices:
                            if new_device.serial == device.serial and new_device.connection_type == 'download':
                                return new_device

            # MTP to ADB mode - requires manual user action
            if target_mode == 'adb' and device.connection_type == 'mtp':
                self.logger.warning("Device in MTP mode - requires manual switch to ADB")
                self._update_progress("Device in MTP mode - enable USB Debugging in Developer Options", 25)
                return None

            # Fastboot to EDL mode
            if target_mode == 'edl' and device.connection_type == 'fastboot':
                self.logger.info(f"Switching to EDL mode")
                success, _ = self.device_manager.execute_fastboot_command(device.serial, ['oem', 'edl'])
                if success:
                    time.sleep(10)
                    new_devices = self.device_manager.scan_devices()
                    for new_device in new_devices:
                        if new_device.connection_type == 'edl':
                            return new_device

            # Fastboot to Android mode (for interface bypass methods)
            if target_mode == 'adb' and device.connection_type == 'fastboot':
                self.logger.info(f"Booting device from Fastboot to Android mode")
                success, _ = self.device_manager.execute_fastboot_command(
                    device.serial, ['reboot']
                )
                if success:
                    self.logger.info(f"Successfully sent reboot command to device")
                    self._update_progress("Device booting to Android mode...", 30)
                    time.sleep(15)  # Wait for device to boot
                    # Re-scan for device in ADB mode
                    new_devices = self.device_manager.scan_devices()
                    for new_device in new_devices:
                        if new_device.connection_type == 'adb':
                            self.logger.info(f"Device detected in ADB mode: {new_device.serial}")
                            return new_device
                    self.logger.warning("Device not detected in ADB mode after reboot")
                else:
                    self.logger.error("Failed to reboot device from Fastboot")

            # Moto G: switch to brom mode
            if target_mode == 'brom' and device.manufacturer.lower() == 'motorola' and 'moto g' in device.model.lower():
                self.logger.info(f"Switching Moto G device to brom mode")
                if device.connection_type == 'adb':
                    # Try ADB reboot to brom
                    success, _ = self.device_manager.execute_adb_command(
                        device.serial, ['reboot', 'brom']
                    )
                    if success:
                        time.sleep(5)
                        # Re-scan for device in brom mode
                        new_devices = self.device_manager.scan_devices()
                        for new_device in new_devices:
                            if new_device.serial == device.serial and new_device.connection_type == 'brom':
                                return new_device
                elif device.connection_type == 'fastboot':
                    # Try fastboot reboot to brom
                    success, _ = self.device_manager.execute_fastboot_command(
                        device.serial, ['reboot', 'brom']
                    )
                    if success:
                        time.sleep(5)
                        new_devices = self.device_manager.scan_devices()
                        for new_device in new_devices:
                            if new_device.serial == device.serial and new_device.connection_type == 'brom':
                                return new_device

            # If switching failed, return None
            self.logger.warning(f"Failed to switch device to {target_mode} mode")
            return None

        except Exception as e:
            self.logger.error(f"Error switching device mode: {e}")
            return None

    def _select_best_bypass_method(self, device: DeviceInfo) -> Optional[BypassMethod]:
        """Select the best bypass method for the device"""
        # Get AI-recommended methods
        recommended = self.bypass_manager.get_recommended_methods(device)

        if not recommended:
            self.logger.warning("No recommended methods found")
            return None

        # Return the top recommended method
        best_method = recommended[0]
        self.logger.info(f"Best method: {best_method.name} (success rate: {best_method.success_rate:.1%})")

        return best_method

    def _update_progress(self, message: str, percentage: int):
        """Update progress callback if available"""
        if self.progress_callback:
            self.progress_callback(message, percentage)
        self.logger.info(f"Progress: {percentage}% - {message}")

    def start_background_auto_bypass(self, progress_callback: Optional[Callable[[str, int], None]] = None):
        """Start auto bypass in background thread"""
        if self.auto_thread and self.auto_thread.is_alive():
            self.logger.warning("Auto bypass already running")
            return

        self.auto_thread = Thread(target=self.start_auto_bypass, args=(progress_callback,), daemon=True)
        self.auto_thread.start()

    def stop_auto_bypass(self):
        """Stop auto bypass process"""
        self.running = False
        if self.auto_thread:
            self.auto_thread.join(timeout=5)
