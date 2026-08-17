#!/usr/bin/env python3
"""
Legitimate iPhone erase/restore helper.

This module does not bypass passcodes or Activation Lock. It only detects Apple
USB recovery states and prepares the standard full erase restore command used by
libimobiledevice's idevicerestore.
"""

from __future__ import annotations

from dataclasses import dataclass
import re
import shutil
import subprocess
import time
from typing import Callable, Dict, List, Optional


APPLE_VENDOR_ID = "05ac"

IPHONE_13_MODELS = {
    "iPhone14,2": "iPhone 13 Pro",
    "iPhone14,3": "iPhone 13 Pro Max",
    "iPhone14,4": "iPhone 13 mini",
    "iPhone14,5": "iPhone 13",
}

IPHONE_13_RECOVERY_STEPS = [
    "Connect the iPhone 13 to this Linux computer with a data-capable USB cable.",
    "Quickly press and release Volume Up.",
    "Quickly press and release Volume Down.",
    "Hold the Side button. Keep holding past the Apple logo.",
    "Release the Side button only when the recovery screen shows a cable/computer icon.",
    "Return to this app and use Scan iPhone, then Erase and Restore Latest iOS.",
]

APPLE_ACCOUNT_RECOVERY_STEPS = [
    "Erasing removes the local passcode, but it does not bypass Activation Lock.",
    "If setup asks for the linked Apple Account, use Apple's account recovery or reset the password.",
    "If you bought the phone and cannot contact the previous owner, request Activation Lock support from Apple with proof of purchase.",
]


@dataclass
class IPhoneDevice:
    serial: str
    mode: str
    product_id: str
    description: str
    ecid: Optional[str] = None
    model_identifier: Optional[str] = None

    @property
    def marketing_name(self) -> str:
        if self.model_identifier in IPHONE_13_MODELS:
            return IPHONE_13_MODELS[self.model_identifier]
        return self.model_identifier or self.description

    @property
    def is_iphone_13_family(self) -> bool:
        return self.model_identifier in IPHONE_13_MODELS


@dataclass
class RestoreToolStatus:
    idevicerestore: Optional[str]
    ideviceinfo: Optional[str]
    ideviceenterrecovery: Optional[str]
    idevicepair: Optional[str]
    usbmuxd: Optional[str]
    lsusb: Optional[str]

    @property
    def can_restore(self) -> bool:
        return bool(self.idevicerestore)


class IPhoneRecoveryManager:
    """Detect Apple devices and run a legitimate erase restore."""

    _USB_RE = re.compile(
        r"Bus\s+(?P<bus>\d+)\s+Device\s+(?P<dev>\d+):\s+ID\s+05ac:(?P<pid>[0-9a-fA-F]{4})\s*(?P<desc>.*)"
    )

    _MODE_BY_PID = {
        "1227": "dfu",
        "1280": "recovery",
        "1281": "recovery",
        "1282": "recovery",
        "1283": "recovery",
        "12a8": "normal",
        "12ab": "normal",
        "12ac": "normal",
    }

    def tool_status(self) -> RestoreToolStatus:
        return RestoreToolStatus(
            idevicerestore=shutil.which("idevicerestore"),
            ideviceinfo=shutil.which("ideviceinfo"),
            ideviceenterrecovery=shutil.which("ideviceenterrecovery"),
            idevicepair=shutil.which("idevicepair"),
            usbmuxd=shutil.which("usbmuxd"),
            lsusb=shutil.which("lsusb"),
        )

    def linux_readiness_report(self) -> Dict[str, str]:
        """Return installed-tool status for Linux restore support."""
        status = self.tool_status()
        report = {
            "idevicerestore": status.idevicerestore or "missing",
            "ideviceinfo": status.ideviceinfo or "missing",
            "ideviceenterrecovery": status.ideviceenterrecovery or "missing",
            "idevicepair": status.idevicepair or "missing",
            "usbmuxd": status.usbmuxd or "missing",
            "lsusb": status.lsusb or "missing",
        }
        if not status.idevicerestore:
            report["restore_ready"] = "no: install idevicerestore"
        elif not status.lsusb:
            report["restore_ready"] = "partial: install usbutils for recovery/DFU detection"
        else:
            report["restore_ready"] = "yes"
        return report

    def scan_devices(self) -> List[IPhoneDevice]:
        devices = self._scan_lsusb()
        if not devices:
            normal_device = self._scan_ideviceinfo()
            if normal_device:
                devices.append(normal_device)
        return devices

    def build_restore_command(self, device: Optional[IPhoneDevice] = None) -> List[str]:
        status = self.tool_status()
        if not status.idevicerestore:
            raise RuntimeError("idevicerestore is not installed")

        command = [
            status.idevicerestore,
            "--erase",
            "--latest",
            "--no-input",
            "--plain-progress",
        ]
        if device and device.ecid:
            command.extend(["--ecid", device.ecid])
        return command

    def is_restore_mode(self, device: IPhoneDevice) -> bool:
        """Return True when a device is in a mode idevicerestore can erase."""
        return device.mode in {"recovery", "dfu", "apple_usb"}

    def can_prepare_for_restore(self, device: IPhoneDevice) -> bool:
        """Return True when the app can restore now or try to enter recovery first."""
        status = self.tool_status()
        return self.is_restore_mode(device) or (
            device.mode == "normal"
            and bool(status.ideviceenterrecovery)
            and bool(device.serial)
            and not device.serial.startswith("usb_")
        )

    def find_restore_ready_device(self) -> Optional[IPhoneDevice]:
        """Return the first connected iPhone/iPad that is ready for restore."""
        for device in self.scan_devices():
            if self.is_restore_mode(device):
                return device
        return None

    def find_connected_device(self) -> Optional[IPhoneDevice]:
        """Return any connected Apple mobile device detected by the available tools."""
        devices = self.scan_devices()
        return devices[0] if devices else None

    def enter_recovery_mode(
        self,
        device: IPhoneDevice,
        output_callback: Optional[Callable[[str], None]] = None,
    ) -> bool:
        """Ask a normal-mode iPhone to reboot into recovery mode when tooling allows it."""
        status = self.tool_status()
        if not status.ideviceenterrecovery:
            if output_callback:
                output_callback("ideviceenterrecovery is not installed; waiting for manual recovery/DFU mode.")
            return False
        if device.mode != "normal":
            return self.is_restore_mode(device)
        if not device.serial or device.serial.startswith("usb_"):
            if output_callback:
                output_callback("Normal-mode device has no UDID; waiting for manual recovery/DFU mode.")
            return False

        if output_callback:
            output_callback(f"Requesting recovery mode for {device.description}...")
        try:
            result = subprocess.run(
                [status.ideviceenterrecovery, device.serial],
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
            )
        except Exception as exc:
            if output_callback:
                output_callback(f"Could not request recovery mode: {exc}")
            return False

        if result.stdout and output_callback:
            output_callback(result.stdout.strip())
        if result.stderr and output_callback:
            output_callback(result.stderr.strip())
        return result.returncode == 0

    def wait_for_restore_ready_device(
        self,
        timeout_seconds: Optional[float] = None,
        poll_interval: float = 2.0,
        output_callback: Optional[Callable[[str], None]] = None,
    ) -> Optional[IPhoneDevice]:
        """Poll USB until a recovery/DFU Apple device is connected."""
        deadline = None if timeout_seconds is None else time.monotonic() + timeout_seconds
        recovery_requested_for: set[str] = set()
        while True:
            devices = self.scan_devices()
            for device in devices:
                if not self.is_restore_mode(device):
                    continue
                if output_callback:
                    output_callback(
                        f"Detected restore-ready device: {device.description} "
                        f"({device.mode}, {device.serial})"
                    )
                return device

            for device in devices:
                if device.mode != "normal" or device.serial in recovery_requested_for:
                    continue
                recovery_requested_for.add(device.serial)
                self.enter_recovery_mode(device, output_callback)

            if deadline is not None and time.monotonic() >= deadline:
                if output_callback:
                    output_callback("Timed out waiting for an iPhone in recovery or DFU mode.")
                return None

            if output_callback:
                output_callback("Waiting for iPhone in recovery or DFU mode...")
            time.sleep(max(0.5, poll_interval))

    def prepare_device_for_restore(
        self,
        device: IPhoneDevice,
        timeout_seconds: float = 120.0,
        poll_interval: float = 2.0,
        output_callback: Optional[Callable[[str], None]] = None,
    ) -> Optional[IPhoneDevice]:
        """Put a selected device into a restore-ready state when possible."""
        if self.is_restore_mode(device):
            return device

        if device.mode != "normal":
            if output_callback:
                output_callback(f"Device mode {device.mode} is not restore-ready.")
            return None

        requested = self.enter_recovery_mode(device, output_callback)
        if requested and output_callback:
            output_callback("Recovery requested. Waiting for the recovery screen and USB reconnect...")
        elif output_callback:
            output_callback("Use the manual recovery button sequence, then keep the phone connected.")

        return self.wait_for_restore_ready_device(
            timeout_seconds=timeout_seconds,
            poll_interval=poll_interval,
            output_callback=output_callback,
        )

    def auto_restore_when_connected(
        self,
        timeout_seconds: Optional[float] = None,
        poll_interval: float = 2.0,
        output_callback: Optional[Callable[[str], None]] = None,
    ) -> int:
        """Wait for a restore-ready device, then erase and restore latest iOS."""
        device = self.wait_for_restore_ready_device(
            timeout_seconds=timeout_seconds,
            poll_interval=poll_interval,
            output_callback=output_callback,
        )
        if not device:
            return 2

        if output_callback:
            output_callback("Starting full erase and latest signed iOS restore.")
        return self.restore_latest_firmware(device, output_callback)

    def restore_latest_firmware(
        self,
        device: Optional[IPhoneDevice] = None,
        output_callback: Optional[Callable[[str], None]] = None,
    ) -> int:
        command = self.build_restore_command(device)
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
        assert process.stdout is not None
        for line in process.stdout:
            if output_callback:
                output_callback(line.rstrip())
        return process.wait()

    def erase_device(
        self,
        device: IPhoneDevice,
        output_callback: Optional[Callable[[str], None]] = None,
    ) -> int:
        """Erase a selected iPhone through the standard recovery restore flow."""
        restore_device = self.prepare_device_for_restore(device, output_callback=output_callback)
        if not restore_device:
            return 2
        if output_callback:
            output_callback("Starting full erase and latest signed iOS restore.")
        return self.restore_latest_firmware(restore_device, output_callback)

    @staticmethod
    def iphone_13_recovery_steps() -> List[str]:
        return list(IPHONE_13_RECOVERY_STEPS)

    @staticmethod
    def apple_account_recovery_steps() -> List[str]:
        return list(APPLE_ACCOUNT_RECOVERY_STEPS)

    def _scan_lsusb(self) -> List[IPhoneDevice]:
        status = self.tool_status()
        if not status.lsusb:
            return []

        try:
            result = subprocess.run(
                [status.lsusb],
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )
        except Exception:
            return []

        return self.parse_lsusb(result.stdout)

    def parse_lsusb(self, output: str) -> List[IPhoneDevice]:
        devices: List[IPhoneDevice] = []
        for line in output.splitlines():
            match = self._USB_RE.search(line)
            if not match:
                continue
            pid = match.group("pid").lower()
            mode = self._MODE_BY_PID.get(pid, "apple_usb")
            bus = match.group("bus")
            dev = match.group("dev")
            desc = match.group("desc").strip() or "Apple device"
            devices.append(
                IPhoneDevice(
                    serial=f"usb_{bus}_{dev}_{APPLE_VENDOR_ID}_{pid}",
                    mode=mode,
                    product_id=pid,
                    description=desc,
                )
            )
        return devices

    def _scan_ideviceinfo(self) -> Optional[IPhoneDevice]:
        status = self.tool_status()
        if not status.ideviceinfo:
            return None

        try:
            result = subprocess.run(
                [status.ideviceinfo],
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )
        except Exception:
            return None

        if result.returncode != 0 or not result.stdout.strip():
            return None

        info = self._parse_ideviceinfo(result.stdout)
        model = info.get("ProductType") or "iPhone/iPad"
        udid = info.get("UniqueDeviceID") or "apple_normal_mode"
        name = info.get("DeviceName") or model
        marketing_name = IPHONE_13_MODELS.get(model, model)
        return IPhoneDevice(
            serial=udid,
            mode="normal",
            product_id="unknown",
            description=f"{name} ({marketing_name})",
            model_identifier=model,
        )

    @staticmethod
    def _parse_ideviceinfo(output: str) -> Dict[str, str]:
        info: Dict[str, str] = {}
        for line in output.splitlines():
            if ":" not in line:
                continue
            key, value = line.split(":", 1)
            info[key.strip()] = value.strip()
        return info
