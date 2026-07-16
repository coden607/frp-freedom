#!/usr/bin/env python3
"""
Device Manager for FRP Freedom
Handles device detection, communication, and information gathering
"""

import subprocess
import re
import logging
import sys
import os
import shutil
import time
import threading
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass
import serial.tools.list_ports


@dataclass
class DeviceInfo:
    """Device information container"""

    serial: str
    model: str
    manufacturer: str
    android_version: str
    sdk_version: str
    bootloader_version: str
    frp_status: str
    connection_type: str  # adb, fastboot, download, modem
    chipset: str = "unknown"
    imei: str = ""
    brand: str = "unknown"
    bootloader_status: str = "unknown"
    root_status: str = "unknown"
    security_patch: str = "unknown"
    encryption_status: str = "unknown"
    api_level: str = "unknown"
    build_id: str = "unknown"
    product: str = "unknown"
    device: str = "unknown"
    modem_port: str = ""  # Associated modem port for exploit access

    def to_dict(self) -> Dict:
        return {
            "serial": self.serial,
            "model": self.model,
            "manufacturer": self.manufacturer,
            "android_version": self.android_version,
            "sdk_version": self.sdk_version,
            "bootloader_version": self.bootloader_version,
            "frp_status": self.frp_status,
            "connection_type": self.connection_type,
            "chipset": self.chipset,
            "imei": (
                self.imei[:4] + "****" + self.imei[-4:]
                if len(self.imei) >= 8
                else "unknown"
            ),
            "brand": self.brand,
            "bootloader_status": self.bootloader_status,
            "root_status": self.root_status,
        }


class DeviceManager:
    """Manages device detection and communication"""

    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.adb_path = self._find_adb_binary()
        self.fastboot_path = self._find_fastboot_binary()
        self.connected_devices: List[DeviceInfo] = []
        self._scan_lock = threading.RLock()
        self._scan_paused = False
        self._last_scan_time = 0.0
        self._pause_check_interval = 3.0
        self._paused_device_serial = ""

    def _find_adb_binary(self) -> Optional[Path]:
        """Find ADB binary in system PATH or bundled tools"""
        # Check bundled tools first
        bundled_adb = Path(__file__).parent.parent.parent / "tools" / "adb"
        if sys.platform == "win32":
            bundled_adb_exe = bundled_adb.with_suffix(".exe")
            if bundled_adb_exe.exists():
                return bundled_adb_exe
        if bundled_adb.exists():
            return bundled_adb

        # Use shutil.which() which works on Windows, macOS, and Linux
        adb_in_path = shutil.which("adb")
        if adb_in_path:
            self.logger.debug(f"Found ADB in PATH: {adb_in_path}")
            return Path(adb_in_path)

        # Windows-specific: Check common Android SDK locations
        if sys.platform == "win32":
            common_paths = [
                Path(os.environ.get("LOCALAPPDATA", ""))
                / "Android"
                / "Sdk"
                / "platform-tools"
                / "adb.exe",
                Path(os.environ.get("ProgramFiles", ""))
                / "Android"
                / "Sdk"
                / "platform-tools"
                / "adb.exe",
                Path(os.path.expanduser("~"))
                / "AppData"
                / "Local"
                / "Android"
                / "Sdk"
                / "platform-tools"
                / "adb.exe",
            ]
            for path in common_paths:
                if path.exists():
                    self.logger.debug(f"Found ADB at: {path}")
                    return path

        self.logger.warning(
            "ADB binary not found. Some features may not work."
        )
        return None

    def _find_fastboot_binary(self) -> Optional[Path]:
        """Find fastboot binary in system PATH or bundled tools"""
        # Check bundled tools first
        bundled_fastboot = (
            Path(__file__).parent.parent.parent / "tools" / "fastboot"
        )
        if sys.platform == "win32":
            bundled_fastboot_exe = bundled_fastboot.with_suffix(".exe")
            if bundled_fastboot_exe.exists():
                return bundled_fastboot_exe
        if bundled_fastboot.exists():
            return bundled_fastboot

        # Use shutil.which() which works on Windows, macOS, and Linux
        fastboot_in_path = shutil.which("fastboot")
        if fastboot_in_path:
            self.logger.debug(f"Found fastboot in PATH: {fastboot_in_path}")
            return Path(fastboot_in_path)

        # Windows-specific: Check common Android SDK locations
        if sys.platform == "win32":
            common_paths = [
                Path(os.environ.get("LOCALAPPDATA", ""))
                / "Android"
                / "Sdk"
                / "platform-tools"
                / "fastboot.exe",
                Path(os.environ.get("ProgramFiles", ""))
                / "Android"
                / "Sdk"
                / "platform-tools"
                / "fastboot.exe",
                Path(os.path.expanduser("~"))
                / "AppData"
                / "Local"
                / "Android"
                / "Sdk"
                / "platform-tools"
                / "fastboot.exe",
            ]
            for path in common_paths:
                if path.exists():
                    self.logger.debug(f"Found fastboot at: {path}")
                    return path

        self.logger.warning(
            "Fastboot binary not found. Some features may not work."
        )
        return None

    def scan_devices(self) -> List[DeviceInfo]:
        """Scan for connected Android devices while pausing after a device is found."""
        if not self._scan_lock.acquire(blocking=False):
            return list(self.connected_devices)

        try:
            now = time.monotonic()

            if self._scan_paused:
                if now - self._last_scan_time < self._pause_check_interval:
                    self.logger.debug(
                        "Scan paused while a device connection is active; waiting before checking again"
                    )
                    return list(self.connected_devices)

                if self._paused_device_serial and self._is_device_connected(
                    self._paused_device_serial
                ):
                    self.logger.debug(
                        f"Selected device {self._paused_device_serial} is still connected"
                    )
                    return list(self.connected_devices)

                self.logger.info(
                    "Previously selected device disappeared; resuming full discovery"
                )
                self._scan_paused = False
                self._paused_device_serial = ""
            else:
                self.logger.info("Scanning for connected devices...")

            devices = []

            # Scan ADB devices
            adb_devices = self._scan_adb_devices()
            devices.extend(adb_devices)

            # Scan fastboot devices
            fastboot_devices = self._scan_fastboot_devices()
            devices.extend(fastboot_devices)

            # Scan download mode devices (placeholder for future implementation)
            download_devices = self._scan_download_mode_devices()
            devices.extend(download_devices)

            # Update connected_devices BEFORE modem scan so matching works correctly
            self.connected_devices = devices

            # Scan Samsung modems (merged into existing devices if matched)
            modem_devices = self.scan_samsung_modems()
            devices.extend(modem_devices)

            # Final update with any new modem-only devices
            self.connected_devices = devices
            self._last_scan_time = now

            if devices:
                self._paused_device_serial = next(
                    (
                        device.serial
                        for device in devices
                        if getattr(device, "serial", "")
                    ),
                    "",
                )
                self.logger.info(
                    "Device connection detected; pausing further scans until it disconnects"
                )
                self._scan_paused = True
            else:
                self._paused_device_serial = ""
                self.logger.info("No connected device found; resuming discovery")
                self._scan_paused = False

            self.logger.info(f"Found {len(devices)} connected device(s)")

            return devices
        finally:
            self._scan_lock.release()

    def _scan_adb_devices(self) -> List[DeviceInfo]:
        """Scan for ADB-connected devices"""
        if not self.adb_path:
            self.logger.debug("No ADB path found")
            return []

        devices = []
        try:
            # Get device list
            result = subprocess.run(
                [str(self.adb_path), "devices", "-l"],
                capture_output=True,
                text=True,
                timeout=30,
            )

            self.logger.debug(f"ADB devices output: {result.stdout}")

            if result.returncode != 0:
                self.logger.error(
                    f"ADB devices command failed: {result.stderr}"
                )
                return []

            # Parse device list
            lines = result.stdout.strip().split("\n")[1:]  # Skip header
            self.logger.debug(f"Processing {len(lines)} device lines")

            for line in lines:
                self.logger.debug(f"Processing line: '{line}'")
                if line.strip():
                    # Parse device line: serial status [usb:X-Y] [product:X]
                    # [model:X] [device:X] [transport_id:X]
                    parts = line.split()
                    if len(parts) >= 2:
                        serial = parts[0]
                        status = parts[1]

                        # Extract metadata from the device line
                        metadata = {}
                        for part in parts[2:]:
                            if ":" in part:
                                key, value = part.split(":", 1)
                                metadata[key] = value

                        self.logger.debug(
                            f"Found device: serial={serial}, status={status}, metadata={metadata}"
                        )

                        if status in ["device", "recovery"]:
                            self.logger.debug(
                                f"Getting device info for authorized device: {serial}"
                            )
                            device_info = self._get_adb_device_info(
                                serial, metadata
                            )
                            if device_info:
                                self.logger.debug(
                                    f"Successfully got device info for {serial}"
                                )
                                devices.append(device_info)
                            else:
                                self.logger.warning(
                                    f"Failed to get device info for {serial}"
                                )
                        elif status == "unauthorized":
                            self.logger.debug(
                                f"Getting device info for unauthorized device: {serial}"
                            )
                            # Handle unauthorized devices for FRP bypass
                            # scenarios
                            device_info = self._get_unauthorized_device_info(
                                serial, metadata
                            )
                            if device_info:
                                self.logger.debug(
                                    f"Successfully got unauthorized device info for {serial}"
                                )
                                devices.append(device_info)
                            else:
                                self.logger.warning(
                                    f"Failed to get unauthorized device info for {serial}"
                                )
                    else:
                        self.logger.debug(
                            f"Skipping line with insufficient parts: {len(parts)}"
                        )

        except subprocess.TimeoutExpired:
            self.logger.error("ADB scan timeout")
        except Exception as e:
            self.logger.error(f"Error scanning ADB devices: {e}")

        self.logger.debug(f"Returning {len(devices)} devices")
        return devices

    def _scan_fastboot_devices(self) -> List[DeviceInfo]:
        """Scan for fastboot-connected devices"""
        if not self.fastboot_path:
            self.logger.debug("Fastboot binary not found")
            return []

        devices = []
        try:
            result = subprocess.run(
                [str(self.fastboot_path), "devices"],
                capture_output=True,
                text=True,
                timeout=30,
            )

            self.logger.debug(f"Fastboot devices output: {result.stdout}")
            self.logger.debug(f"Fastboot devices stderr: {result.stderr}")

            if result.returncode != 0:
                self.logger.error(f"Fastboot command failed: {result.stderr}")
                return []

            lines = result.stdout.strip().split("\n")
            self.logger.debug(f"Processing {len(lines)} fastboot device lines")

            for line in lines:
                line = line.strip()
                # Skip empty lines and headers
                if not line or line.startswith("*"):
                    continue

                # Handle both space and tab delimiters
                # Split by any whitespace and filter empty strings
                parts = line.split()
                if len(parts) >= 2:
                    serial = parts[0]
                    status = parts[1]

                    self.logger.debug(
                        f"Found fastboot device: serial={serial}, status={status}"
                    )

                    if status == "fastboot":  # Device is in fastboot mode
                        device_info = self._get_fastboot_device_info(serial)
                        if device_info:
                            devices.append(device_info)
                            self.logger.debug(
                                f"Added fastboot device: {serial}"
                            )
                        else:
                            self.logger.warning(
                                f"Failed to get info for fastboot device: {serial}"
                            )

        except Exception as e:
            self.logger.error(
                f"Error scanning fastboot devices: {e}", exc_info=True
            )

        self.logger.debug(f"Returning {len(devices)} fastboot devices")
        return devices

    def scan_samsung_modems(self) -> List[DeviceInfo]:
        """Scan for Samsung devices in modem mode"""
        self.logger.info("Scanning for Samsung modem devices...")
        new_devices = []

        try:
            ports = list(serial.tools.list_ports.comports())
            for port in ports:
                if port.vid == 0x04E8:  # Samsung VID
                    self.logger.debug(f"Found Samsung modem: {port.device}")

                    # Logic to prevent duplicates:
                    # Check if this modem corresponds to an existing connected device
                    # The modem port usually contains the serial number (e.g. /dev/cu.usbmodem<SERIAL> or COM<X>)
                    # On Mac/Linux, the serial is often in the device path. On
                    # Windows, we might need port.serial_number

                    matched_existing = False
                    target_device = None

                    # Try to get serial from port
                    port_serial = getattr(port, "serial_number", "") or ""
                    stable_serial = port_serial.strip()
                    device_serial = stable_serial or port.device

                    # Check against existing devices
                    for device in self.connected_devices:
                        # Check strict serial match if available
                        if stable_serial and device.serial == stable_serial:
                            self.logger.info(
                                f"Matched modem {port.device} to existing device {device.serial}"
                            )
                            device.modem_port = port.device
                            matched_existing = True
                            target_device = device
                            break

                        # Check fuzzy match in port name (common on Mac/Linux)
                        # e.g. device.serial = R5CW418JMSL, port.device =
                        # /dev/cu.usbmodemR5CW418JMSL2
                        if (
                            device.serial
                            and len(device.serial) > 5
                            and device.serial in port.device
                        ):
                            self.logger.info(
                                f"Fuzzy matched modem {port.device} to existing device {device.serial}"
                            )
                            device.modem_port = port.device
                            matched_existing = True
                            target_device = device
                            break

                    if matched_existing and target_device:
                        # Modem matched to existing device, just mark it
                        # Don't try to read info here as it can block the port
                        continue

                    for existing_device in new_devices:
                        if existing_device.serial == device_serial:
                            self.logger.debug(
                                f"Collapsed duplicate modem entry for {device_serial}"
                            )
                            existing_device.modem_port = port.device
                            break
                    else:
                        # If no match found, create a new device entry
                        # Don't read info during scan to avoid port blocking
                        device_info = DeviceInfo(
                            serial=device_serial,
                            model="Samsung Modem",
                            manufacturer="Samsung",
                            android_version="Unknown",
                            sdk_version="Unknown",
                            bootloader_version="Unknown",
                            frp_status="Unknown",
                            connection_type="modem",
                            chipset="Unknown",
                            brand="Samsung",
                            bootloader_status="Unknown",
                            root_status="Unknown",
                            device=port.description,
                            modem_port=port.device,
                        )
                        new_devices.append(device_info)
        except Exception as e:
            self.logger.error(f"Error scanning samsung modems: {e}")

        return new_devices

    def _scan_download_mode_devices(self) -> List[DeviceInfo]:
        """Scan for devices in download mode (placeholder)"""
        # This would implement detection for Samsung Download Mode,
        # MediaTek Download Mode, Qualcomm EDL mode, etc.
        # For now, return empty list
        return []

    def _is_device_connected(self, serial: str) -> bool:
        """Perform a lightweight connection check for a known device serial."""
        if not serial or not self.adb_path:
            return False

        try:
            result = subprocess.run(
                [str(self.adb_path), "-s", serial, "get-state"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            return result.returncode == 0 and result.stdout.strip().lower() in {
                "device",
                "recovery",
                "unauthorized",
            }
        except Exception:
            return False

    def _get_adb_device_info(
        self, serial: str, metadata: Dict[str, str] = None
    ) -> Optional[DeviceInfo]:
        """Get detailed information for an ADB device"""
        if metadata is None:
            metadata = {}

        try:
            self.logger.debug(f"Getting device properties for {serial}")
            # Get device properties via shell
            props = self._get_device_properties(serial)
            self.logger.debug(f"Got {len(props)} properties for {serial}")

            # If we got properties from shell, use them
            if props:
                # Check FRP status
                self.logger.debug(f"Checking FRP status for {serial}")
                frp_status = self._check_frp_status(serial)
                self.logger.debug(f"FRP status for {serial}: {frp_status}")

                manufacturer = props.get(
                    "ro.product.manufacturer",
                    metadata.get("manufacturer", "unknown"),
                )
                brand = props.get(
                    "ro.product.brand",
                    metadata.get("brand", manufacturer),
                )
                device_info = DeviceInfo(
                    serial=serial,
                    model=props.get(
                        "ro.product.model", metadata.get("model", "unknown")
                    ),
                    manufacturer=manufacturer,
                    android_version=props.get(
                        "ro.build.version.release",
                        metadata.get("android_version", "unknown"),
                    ),
                    sdk_version=props.get(
                        "ro.build.version.sdk",
                        metadata.get("sdk_version", "unknown"),
                    ),
                    bootloader_version=props.get(
                        "ro.bootloader",
                        metadata.get("bootloader_version", "unknown"),
                    ),
                    frp_status=frp_status,
                    connection_type="adb",
                    chipset=props.get(
                        "ro.hardware", metadata.get("chipset", "unknown")
                    ),
                    brand=brand,
                    bootloader_status="unknown",
                    root_status="unknown",
                    security_patch=props.get(
                        "ro.build.version.security_patch",
                        metadata.get("security_patch", "unknown"),
                    ),
                    api_level=props.get(
                        "ro.build.version.sdk",
                        metadata.get("api_level", "unknown"),
                    ),
                    build_id=props.get(
                        "ro.build.id", metadata.get("build_id", "unknown")
                    ),
                    product=props.get(
                        "ro.product.name", metadata.get("product", "unknown")
                    ),
                    device=props.get(
                        "ro.product.device", metadata.get("device", "unknown")
                    ),
                )

                self.logger.debug(
                f"Created device info for {serial}: {device_info.model} ({device_info.manufacturer})"
            )
            else:
                # Shell commands failed, use metadata fallback
                self.logger.warning(
                    f"Shell access restricted for {serial}, using metadata fallback"
                )
                device_info = self._create_fallback_device_info(
                    serial, metadata
                )

                if not device_info:
                    self.logger.error(
                        f"Failed to create fallback device info for {serial}"
                    )
                    return None

            # Try to get IMEI (may require root)
            try:
                imei = self._get_device_imei(serial)
                device_info.imei = imei
            except Exception:
                pass  # IMEI not accessible

            return device_info

        except Exception as e:
            self.logger.error(f"Error getting device info for {serial}: {e}")
            # Try fallback even on exception
            try:
                return self._create_fallback_device_info(serial, metadata)
            except BaseException:
                return None

    def _get_unauthorized_device_info(
        self, serial: str, metadata: Dict[str, str] = None
    ) -> Optional[DeviceInfo]:
        """Get basic device info for unauthorized devices (FRP bypass scenarios)"""
        if metadata is None:
            metadata = {}

        try:
            self.logger.info(
                f"Creating device info for unauthorized device: {serial}"
            )

            # Try to use metadata if available
            if metadata:
                return self._create_fallback_device_info(
                    serial, metadata, connection_type="adb_unauthorized"
                )

            # Create basic device info for FRP bypass
            device_info = DeviceInfo(
                serial=serial,
                model="Unknown (Unauthorized)",
                manufacturer="Unknown",
                android_version="Unknown",
                sdk_version="Unknown",
                bootloader_version="Unknown",
                frp_status="locked",  # Assume FRP is locked for unauthorized devices
                connection_type="adb_unauthorized",
                chipset="unknown",
                imei="",
                brand="Unknown",
                bootloader_status="Unknown",
                root_status="Unknown",
            )

            self.logger.info(
                f"Created unauthorized device info: {device_info.serial}"
            )
            return device_info

        except Exception as e:
            self.logger.error(
                f"Error creating unauthorized device info for {serial}: {e}"
            )
            return None

    def _create_fallback_device_info(
        self,
        serial: str,
        metadata: Dict[str, str],
        connection_type: str = "adb_restricted",
    ) -> Optional[DeviceInfo]:
        """Create device info from metadata when shell access is restricted"""
        try:
            # Extract model from metadata
            model = metadata.get("model", "unknown")
            product = metadata.get("product", "unknown")
            device = metadata.get("device", "unknown")
            build_id = metadata.get("build_id", "unknown")
            security_patch = metadata.get("security_patch", "unknown")
            api_level = metadata.get("api_level", "unknown")

            # Infer manufacturer from model name
            manufacturer = "unknown"
            brand = "unknown"

            if model != "unknown":
                model_upper = model.upper()
                # Samsung models typically start with SM-, GT-, or SCH-
                if model_upper.startswith(
                    ("SM-", "SM_", "GT-", "SCH-", "SPH-")
                ):
                    manufacturer = "Samsung"
                    brand = "Samsung"
                # Google Pixel devices
                elif "PIXEL" in model_upper or model_upper.startswith("G-"):
                    manufacturer = "Google"
                    brand = "Google"
                # Xiaomi/Redmi devices
                elif any(x in model_upper for x in ["REDMI", "MI ", "POCO"]):
                    manufacturer = "Xiaomi"
                    brand = "Xiaomi"
                # Huawei devices
                elif model_upper.startswith(("HUAWEI", "HONOR", "HW-", "H-")):
                    manufacturer = "Huawei"
                    brand = "Huawei"
                # OnePlus devices
                elif (
                    model_upper.startswith("ONEPLUS")
                    or "ONEPLUS" in model_upper
                ):
                    manufacturer = "OnePlus"
                    brand = "OnePlus"
                # Oppo devices
                elif model_upper.startswith(("OPPO", "CPH", "PCHM", "PCAM")):
                    manufacturer = "Oppo"
                    brand = "Oppo"
                # Vivo devices
                elif model_upper.startswith("VIVO") or model_upper.startswith(
                    "V"
                ):
                    manufacturer = "Vivo"
                    brand = "Vivo"
                # Realme devices
                elif model_upper.startswith(
                    "REALME"
                ) or model_upper.startswith("RMX"):
                    manufacturer = "Realme"
                    brand = "Realme"

            # Log the fallback creation
            self.logger.info(
                f"Creating fallback device info for {serial}: model={model}, manufacturer={manufacturer}"
            )

            device_info = DeviceInfo(
                serial=serial,
                model=model,
                manufacturer=manufacturer,
                android_version="unknown",  # Cannot determine without shell access
                sdk_version="unknown",
                bootloader_version="unknown",
                frp_status="likely_locked",  # Restricted access suggests FRP lock
                connection_type=connection_type,
                chipset="unknown",
                brand=brand,
                bootloader_status="unknown",
                root_status="unknown",
                build_id=build_id,
                security_patch=security_patch,
                api_level=api_level,
                product=product,
                device=device,
            )

            self.logger.info(
                f"Created fallback device info: {device_info.model} ({device_info.manufacturer})"
            )
            return device_info

        except Exception as e:
            self.logger.error(
                f"Error creating fallback device info for {serial}: {e}"
            )
            return None

    def _get_fastboot_device_info(self, serial: str) -> Optional[DeviceInfo]:
        """Get information for a fastboot device"""
        try:
            # Get basic fastboot variables
            variables = {}
            for var in ["product", "version-bootloader", "version-baseband"]:
                try:
                    result = subprocess.run(
                        [str(self.fastboot_path), "-s", serial, "getvar", var],
                        capture_output=True,
                        text=True,
                        timeout=5,
                    )
                    if result.returncode == 0:
                        # Fastboot outputs to stderr
                        output = result.stderr
                        if ":" in output:
                            variables[var] = output.split(":", 1)[1].strip()
                except Exception:
                    continue

            device_info = DeviceInfo(
                serial=serial,
                model=variables.get("product", "unknown"),
                manufacturer="unknown",  # Not easily available in fastboot
                android_version="unknown",
                sdk_version="unknown",
                bootloader_version=variables.get(
                    "version-bootloader", "unknown"
                ),
                frp_status="unknown",  # Cannot check in fastboot mode
                connection_type="fastboot",
                brand="unknown",
                bootloader_status="unlocked",  # In fastboot mode, bootloader is likely unlocked
                root_status="unknown",
            )

            return device_info

        except Exception as e:
            self.logger.error(
                f"Error getting fastboot device info for {serial}: {e}"
            )
            return None

    def _get_device_properties(self, serial: str) -> Dict[str, str]:
        """Get device properties via ADB"""
        props = {}
        try:
            result = subprocess.run(
                [str(self.adb_path), "-s", serial, "shell", "getprop"],
                capture_output=True,
                text=True,
                timeout=15,
            )

            if result.returncode == 0:
                for line in result.stdout.split("\n"):
                    if ":" in line and "[" in line and "]" in line:
                        # Parse property line: [key]: [value]
                        match = re.match(r"\[([^\]]+)\]:\s*\[([^\]]*)\]", line)
                        if match:
                            key, value = match.groups()
                            props[key] = value

        except Exception as e:
            self.logger.error(f"Error getting properties for {serial}: {e}")

        return props

    def _check_frp_status(self, serial: str) -> str:
        """Check FRP status of device"""
        try:
            # Try multiple methods to check FRP status.
            # These values are only proxy signals and are not authoritative FRP state.
            result = subprocess.run(
                [
                    str(self.adb_path),
                    "-s",
                    serial,
                    "shell",
                    "getprop",
                    "ro.frp.pst",
                ],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                _ = result.stdout.strip()

            result = subprocess.run(
                [
                    str(self.adb_path),
                    "-s",
                    serial,
                    "shell",
                    "sqlite3 /data/system/users/0/accounts.db 'SELECT count(*) FROM accounts'",
                ],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                _ = result.stdout.strip()

            result = subprocess.run(
                [
                    str(self.adb_path),
                    "-s",
                    serial,
                    "shell",
                    "settings get secure user_setup_complete",
                ],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                _ = result.stdout.strip()

        except Exception as e:
            self.logger.error(f"Error checking FRP status for {serial}: {e}")

        return "unknown"

    def _get_device_imei(self, serial: str) -> str:
        """Get device IMEI (requires appropriate permissions)"""
        try:
            # Try service call method
            result = subprocess.run(
                [
                    str(self.adb_path),
                    "-s",
                    serial,
                    "shell",
                    "service call iphonesubinfo 1",
                ],
                capture_output=True,
                text=True,
                timeout=5,
            )

            if result.returncode == 0:
                output = result.stdout
                decoded = []
                for fragment in re.findall(r"([0-9a-fA-F]{8})", output):
                    try:
                        value = int(fragment, 16)
                    except ValueError:
                        continue
                    low = value & 0xFFFF
                    high = (value >> 16) & 0xFFFF
                    if 0x30 <= low <= 0x39:
                        decoded.append(chr(low))
                    if 0x30 <= high <= 0x39:
                        decoded.append(chr(high))

                imei = "".join(decoded)
                if len(imei) == 15 and imei.isdigit():
                    return imei

        except Exception:
            pass

        return ""

    def execute_adb_command(
        self, serial: str, command: List[str]
    ) -> Tuple[bool, str]:
        """Execute ADB command on specific device"""
        if not self.adb_path:
            return False, "ADB not available"

        try:
            full_command = [str(self.adb_path), "-s", serial] + command
            result = subprocess.run(
                full_command, capture_output=True, text=True, timeout=30
            )

            return result.returncode == 0, result.stdout + result.stderr

        except subprocess.TimeoutExpired:
            return False, "Command timeout"
        except Exception as e:
            return False, f"Command failed: {e}"

    def execute_fastboot_command(
        self, serial: str, command: List[str]
    ) -> Tuple[bool, str]:
        """Execute fastboot command on specific device"""
        if not self.fastboot_path:
            return False, "Fastboot not available"

        try:
            full_command = [str(self.fastboot_path), "-s", serial] + command
            result = subprocess.run(
                full_command, capture_output=True, text=True, timeout=60
            )

            return result.returncode == 0, result.stdout + result.stderr

        except subprocess.TimeoutExpired:
            return False, "Command timeout"
        except Exception as e:
            return False, f"Command failed: {e}"

    def get_device_by_serial(self, serial: str) -> Optional[DeviceInfo]:
        """Get device info by serial number"""
        for device in self.connected_devices:
            if device.serial == serial:
                return device
        return None

    def refresh_device_info(self, serial: str) -> Optional[DeviceInfo]:
        """Refresh information for a specific device"""
        if not self._scan_lock.acquire(blocking=False):
            return self.get_device_by_serial(serial)

        try:
            device = self.get_device_by_serial(serial)
            if not device:
                return None

            if device.connection_type == "adb":
                metadata = {
                    "model": device.model,
                    "manufacturer": device.manufacturer,
                    "android_version": device.android_version,
                    "sdk_version": device.sdk_version,
                    "bootloader_version": device.bootloader_version,
                    "brand": device.brand,
                    "chipset": device.chipset,
                    "security_patch": device.security_patch,
                    "api_level": device.api_level,
                    "build_id": device.build_id,
                    "product": device.product,
                    "device": device.device,
                }
                updated_device = self._get_adb_device_info(serial, metadata)
            elif device.connection_type == "fastboot":
                updated_device = self._get_fastboot_device_info(serial)
            else:
                return device

            if updated_device:
                if device.modem_port:
                    updated_device.modem_port = device.modem_port
                # Update the device in the list
                for i, dev in enumerate(self.connected_devices):
                    if dev.serial == serial:
                        self.connected_devices[i] = updated_device
                        break
                return updated_device

            return device
        finally:
            self._scan_lock.release()
