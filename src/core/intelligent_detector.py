#!/usr/bin/env python3
"""
Intelligent Device Detection and Mode Optimization System
Automatically detects devices and switches them to optimal bypass modes
"""

import logging
import subprocess
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from .device_manager import DeviceInfo, DeviceManager
from .config import Config

@dataclass
class BypassMode:
    """Bypass mode with success rate and requirements"""
    name: str
    connection_type: str
    success_rate: float
    priority: int
    description: str
    requires_boot: bool = False
    best_methods: List[str] = None

class IntelligentDetector:
    """Intelligent device detection and mode optimization system"""
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.device_manager = DeviceManager(config)
        
        # Define bypass modes with success rates and priorities
        self.bypass_modes = {
            'adb_setup_wizard': BypassMode(
                name='ADB Setup Wizard',
                connection_type='adb',
                success_rate=0.85,
                priority=1,
                description='Setup wizard ADB exploit',
                best_methods=['adb_setup_wizard', 'samsung_setup_wizard_2025']
            ),
            'adb_talkback_chrome': BypassMode(
                name='TalkBack + Chrome',
                connection_type='adb',
                success_rate=0.92,
                priority=2,
                description='TalkBack + Chrome navigation',
                best_methods=['adb_talkback_chrome', 'chrome_intent_exploit']
            ),
            'fastboot_exploit': BypassMode(
                name='Fastboot Exploit',
                connection_type='fastboot',
                success_rate=0.78,
                priority=3,
                description='Fastboot-based bypass',
                best_methods=['persist_partition_edit', 'framework_patch_android15']
            ),
            'download_mode': BypassMode(
                name='Download Mode',
                connection_type='download',
                success_rate=0.95,
                priority=4,
                description='Samsung download mode exploit',
                best_methods=['samsung_setup_wizard_2025', 'accounts_db_modification']
            ),
            'modem_exploit': BypassMode(
                name='Modem Exploit',
                connection_type='modem',
                success_rate=0.88,
                priority=5,
                description='Samsung modem exploit',
                best_methods=['samsung_setup_wizard_2025']
            )
        }
    
    def aggressive_device_scan(self) -> List[DeviceInfo]:
        """Perform aggressive device scanning with multiple methods"""
        self.logger.info("Starting aggressive device scan...")
        devices = []
        
        # Method 1: Standard scan
        devices.extend(self.device_manager.scan_devices())
        
        # Method 2: Force ADB detection
        adb_devices = self._force_adb_detection()
        devices.extend(adb_devices)
        
        # Method 3: Force Fastboot detection
        fastboot_devices = self._force_fastboot_detection()
        devices.extend(fastboot_devices)
        
        # Method 4: USB device scanning
        usb_devices = self._scan_usb_devices()
        devices.extend(usb_devices)
        
        # Remove duplicates
        unique_devices = self._deduplicate_devices(devices)
        
        self.logger.info(f"Aggressive scan found {len(unique_devices)} devices")
        return unique_devices
    
    def _force_adb_detection(self) -> List[DeviceInfo]:
        """Force ADB device detection with multiple attempts"""
        devices = []
        
        try:
            # Restart ADB server
            subprocess.run(['adb', 'kill-server'], capture_output=True, timeout=5)
            subprocess.run(['adb', 'start-server'], capture_output=True, timeout=5)
            time.sleep(2)
            
            # Try multiple ADB commands
            commands = [
                ['adb', 'devices'],
                ['adb', 'devices', '-l'],
                ['adb', 'get-serialno'],
                ['adb', 'get-state']
            ]
            
            for cmd in commands:
                try:
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                    if result.stdout.strip():
                        # Parse output for device info
                        device_info = self._parse_adb_output(result.stdout)
                        if device_info:
                            devices.extend(device_info)
                except Exception as e:
                    self.logger.debug(f"ADB command {cmd} failed: {e}")
                    
        except Exception as e:
            self.logger.error(f"Force ADB detection failed: {e}")
        
        return devices
    
    def _force_fastboot_detection(self) -> List[DeviceInfo]:
        """Force Fastboot device detection"""
        devices = []
        
        try:
            # Try fastboot with different options
            commands = [
                ['fastboot', 'devices'],
                ['fastboot', 'devices', '-l'],
                ['fastboot', 'getvar', 'all']
            ]
            
            for cmd in commands:
                try:
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                    if result.stdout.strip() or result.stderr.strip():
                        device_info = self._parse_fastboot_output(result.stdout + result.stderr)
                        if device_info:
                            devices.extend(device_info)
                except Exception as e:
                    self.logger.debug(f"Fastboot command {cmd} failed: {e}")
                    
        except Exception as e:
            self.logger.error(f"Force Fastboot detection failed: {e}")
        
        return devices
    
    def _scan_usb_devices(self) -> List[DeviceInfo]:
        """Scan USB devices for Android devices"""
        devices = []
        
        try:
            result = subprocess.run(['lsusb'], capture_output=True, text=True, timeout=10)
            usb_lines = result.stdout.split('\n')
            
            # Android vendor IDs
            android_vendors = {
                '04e8': 'Samsung',
                '18d1': 'Google',
                '22b8': 'Motorola',
                '0489': 'Foxconn (Fox)',
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
            
            for line in usb_lines:
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 6:
                        vendor_id = parts[5].split(':')[0]
                        if vendor_id in android_vendors:
                            manufacturer = android_vendors[vendor_id]
                            device_info = DeviceInfo(
                                serial=f"usb_{vendor_id}_{parts[5].split(':')[1]}",
                                model="Unknown USB Device",
                                manufacturer=manufacturer,
                                android_version="Unknown",
                                sdk_version="Unknown",
                                bootloader_version="Unknown",
                                frp_status="Unknown",
                                connection_type="usb_detected",
                                brand=manufacturer
                            )
                            devices.append(device_info)
                            self.logger.info(f"Found Android USB device: {manufacturer} ({vendor_id})")
                            
        except Exception as e:
            self.logger.error(f"USB device scanning failed: {e}")
        
        return devices
    
    def _parse_adb_output(self, output: str) -> List[DeviceInfo]:
        """Parse ADB output for device information"""
        devices = []
        lines = output.strip().split('\n')
        
        for line in lines:
            if '\t' in line and not line.startswith('List of devices'):
                parts = line.split('\t')
                if len(parts) >= 2:
                    serial = parts[0]
                    status = parts[1]
                    
                    # Extract additional info from extended output
                    metadata = {}
                    if len(parts) > 2:
                        for part in parts[2:]:
                            if ':' in part:
                                key, value = part.split(':', 1)
                                metadata[key] = value
                    
                    device_info = DeviceInfo(
                        serial=serial,
                        model=metadata.get('model', 'Unknown'),
                        manufacturer=metadata.get('manufacturer', 'Unknown'),
                        android_version='Unknown',
                        sdk_version='Unknown',
                        bootloader_version='Unknown',
                        frp_status='Unknown',
                        connection_type='adb' if status == 'device' else f'adb_{status}',
                        brand=metadata.get('manufacturer', 'Unknown')
                    )
                    devices.append(device_info)
        
        return devices
    
    def _parse_fastboot_output(self, output: str) -> List[DeviceInfo]:
        """Parse Fastboot output for device information"""
        devices = []
        lines = output.strip().split('\n')
        
        for line in lines:
            if '\t' in line or 'fastboot' in line.lower():
                parts = line.split('\t')
                if len(parts) >= 1:
                    serial = parts[0].strip()
                    if serial and serial != 'fastboot':
                        device_info = DeviceInfo(
                            serial=serial,
                            model='Fastboot Device',
                            manufacturer='Unknown',
                            android_version='Unknown',
                            sdk_version='Unknown',
                            bootloader_version='Unknown',
                            frp_status='Unknown',
                            connection_type='fastboot',
                            brand='Unknown'
                        )
                        devices.append(device_info)
        
        return devices
    
    def _deduplicate_devices(self, devices: List[DeviceInfo]) -> List[DeviceInfo]:
        """Remove duplicate devices based on serial numbers"""
        seen = set()
        unique_devices = []
        
        for device in devices:
            if device.serial not in seen:
                seen.add(device.serial)
                unique_devices.append(device)
        
        return unique_devices
    
    def get_optimal_mode_for_device(self, device: DeviceInfo) -> BypassMode:
        """Determine the optimal bypass mode for a device"""
        # Get available modes for this device's connection type
        available_modes = []
        for mode_name, mode in self.bypass_modes.items():
            if mode.connection_type == device.connection_type:
                available_modes.append(mode)
            elif device.connection_type.startswith(mode.connection_type):
                available_modes.append(mode)
        
        # If no exact match, try to switch to better mode
        if not available_modes:
            optimal_mode = self._find_best_alternative_mode(device)
        else:
            # Sort by success rate and priority
            available_modes.sort(key=lambda m: (m.success_rate, m.priority), reverse=True)
            optimal_mode = available_modes[0]
        
        self.logger.info(f"Optimal mode for {device.serial}: {optimal_mode.name} ({optimal_mode.success_rate:.1%} success rate)")
        return optimal_mode
    
    def _find_best_alternative_mode(self, device: DeviceInfo) -> BypassMode:
        """Find the best alternative mode and suggest switching"""
        # Sort all modes by success rate
        all_modes = list(self.bypass_modes.values())
        all_modes.sort(key=lambda m: m.success_rate, reverse=True)
        
        best_mode = all_modes[0]
        self.logger.info(f"Best alternative mode for {device.serial}: {best_mode.name} (requires mode switch)")
        return best_mode
    
    def switch_device_to_optimal_mode(self, device: DeviceInfo, target_mode: BypassMode) -> bool:
        """Attempt to switch device to optimal bypass mode"""
        self.logger.info(f"Attempting to switch {device.serial} to {target_mode.name} mode...")
        
        try:
            if target_mode.connection_type == 'adb' and device.connection_type == 'fastboot':
                return self._switch_fastboot_to_adb(device)
            elif target_mode.connection_type == 'fastboot' and device.connection_type == 'adb':
                return self._switch_adb_to_fastboot(device)
            elif target_mode.connection_type == 'download':
                return self._switch_to_download_mode(device)
            else:
                self.logger.warning(f"Cannot switch from {device.connection_type} to {target_mode.connection_type}")
                return False
                
        except Exception as e:
            self.logger.error(f"Mode switch failed: {e}")
            return False
    
    def _switch_fastboot_to_adb(self, device: DeviceInfo) -> bool:
        """Switch device from fastboot to ADB mode"""
        try:
            # Try to boot the device
            result = subprocess.run(['fastboot', '-s', device.serial, 'boot'], 
                                  capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                self.logger.info(f"Successfully booted device {device.serial}")
                time.sleep(10)  # Wait for device to boot
                return True
            else:
                self.logger.error(f"Failed to boot device {device.serial}: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Fastboot to ADB switch failed: {e}")
            return False
    
    def _switch_adb_to_fastboot(self, device: DeviceInfo) -> bool:
        """Switch device from ADB to fastboot mode"""
        try:
            # Try to reboot to bootloader
            result = subprocess.run(['adb', '-s', device.serial, 'reboot', 'bootloader'], 
                                  capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                self.logger.info(f"Successfully rebooted {device.serial} to bootloader")
                time.sleep(5)  # Wait for fastboot mode
                return True
            else:
                self.logger.error(f"Failed to reboot {device.serial} to bootloader: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"ADB to Fastboot switch failed: {e}")
            return False
    
    def _switch_to_download_mode(self, device: DeviceInfo) -> bool:
        """Switch device to download mode (Samsung specific)"""
        try:
            if device.connection_type == 'adb':
                # Try to reboot to download mode
                result = subprocess.run(['adb', '-s', device.serial, 'reboot', 'download'], 
                                      capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0:
                    self.logger.info(f"Successfully rebooted {device.serial} to download mode")
                    time.sleep(5)
                    return True
            elif device.connection_type == 'fastboot':
                # Try to reboot to download mode from fastboot
                result = subprocess.run(['fastboot', '-s', device.serial, 'reboot-download'], 
                                      capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0:
                    self.logger.info(f"Successfully rebooted {device.serial} to download mode")
                    time.sleep(5)
                    return True
                    
        except Exception as e:
            self.logger.error(f"Download mode switch failed: {e}")
            return False
        
        return False
    
    def optimize_all_devices(self) -> Tuple[List[DeviceInfo], Dict[str, BypassMode]]:
        """Optimize all connected devices for best bypass success rates"""
        # Perform aggressive scan
        devices = self.aggressive_device_scan()
        
        optimized_devices = []
        device_modes = {}
        
        for device in devices:
            # Get optimal mode
            optimal_mode = self.get_optimal_mode_for_device(device)
            
            # Try to switch to optimal mode if needed
            if optimal_mode.connection_type != device.connection_type:
                if self.switch_device_to_optimal_mode(device, optimal_mode):
                    # Rescan to get updated device info
                    time.sleep(2)
                    updated_devices = self.aggressive_device_scan()
                    for updated_device in updated_devices:
                        if updated_device.serial == device.serial:
                            device = updated_device
                            break
            
            optimized_devices.append(device)
            device_modes[device.serial] = optimal_mode
        
        self.logger.info(f"Optimized {len(optimized_devices)} devices for FRP bypass")
        return optimized_devices, device_modes
