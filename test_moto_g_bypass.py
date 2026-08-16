import unittest
from unittest.mock import MagicMock, patch
from src.bypass.auto_bypass_manager_enhanced import AutoBypassManager
from src.core.device_manager import DeviceManager, DeviceInfo
from src.core.config import Config
from src.bypass.bypass_manager import BypassManager

class TestMotoGBypass(unittest.TestCase):
    def setUp(self):
        self.config = Config()
        self.device_manager = DeviceManager()
        self.bypass_manager = BypassManager()
        self.auto_bypass = AutoBypassManager(self.config, self.device_manager, self.bypass_manager)

    def test_moto_g_detection(self):
        """Test Moto G device detection"""
        moto_g_device = DeviceInfo(
            serial="123456789",
            brand="motorola",
            model="Moto G Power",
            manufacturer="motorola",
            chipset="qualcomm",
            connection_type="adb"
        )

        optimal_mode = self.auto_bypass._determine_optimal_mode(moto_g_device)
        self.assertEqual(optimal_mode, 'brom', "Moto G should default to brom mode")

    def test_moto_g_brom_mode(self):
        """Test Moto G brom mode detection"""
        moto_g_device = DeviceInfo(
            serial="123456789",
            brand="motorola",
            model="Moto G Stylus",
            manufacturer="motorola",
            chipset="qualcomm",
            connection_type="brom"
        )

        optimal_mode = self.auto_bypass._determine_optimal_mode(moto_g_device)
        self.assertEqual(optimal_mode, 'brom', "Moto G in brom mode should stay in brom mode")

    def test_moto_g_fastboot_mode(self):
        """Test Moto G fastboot mode detection"""
        moto_g_device = DeviceInfo(
            serial="123456789",
            brand="motorola",
            model="Moto G Play",
            manufacturer="motorola",
            chipset="qualcomm",
            connection_type="fastboot"
        )

        optimal_mode = self.auto_bypass._determine_optimal_mode(moto_g_device)
        self.assertEqual(optimal_mode, 'fastboot', "Moto G in fastboot mode should stay in fastboot mode")

    @patch('src.core.device_manager.DeviceManager.execute_adb_command')
    @patch('src.core.device_manager.DeviceManager.scan_devices')
    def test_moto_g_switch_to_brom(self, mock_scan, mock_adb):
        """Test Moto G switching to brom mode"""
        moto_g_device = DeviceInfo(
            serial="123456789",
            brand="motorola",
            model="Moto G",
            manufacturer="motorola",
            chipset="qualcomm",
            connection_type="adb"
        )

        # Mock scan to return device in brom mode after reboot
        mock_scan.return_value = [
            DeviceInfo(
                serial="123456789",
                brand="motorola",
                model="Moto G",
                manufacturer="motorola",
                chipset="qualcomm",
                connection_type="brom"
            )
        ]

        # Mock ADB command success
        mock_adb.return_value = (True, "")

        switched_device = self.auto_bypass._switch_device_mode(moto_g_device, 'brom')
        self.assertIsNotNone(switched_device, "Should successfully switch to brom mode")
        self.assertEqual(switched_device.connection_type, 'brom', "Device should be in brom mode after switch")

    @patch('src.core.device_manager.DeviceManager.execute_fastboot_command')
    @patch('src.core.device_manager.DeviceManager.scan_devices')
    def test_moto_g_switch_to_brom_from_fastboot(self, mock_scan, mock_fastboot):
        """Test Moto G switching to brom mode from fastboot"""
        moto_g_device = DeviceInfo(
            serial="123456789",
            brand="motorola",
            model="Moto G",
            manufacturer="motorola",
            chipset="qualcomm",
            connection_type="fastboot"
        )

        # Mock scan to return device in brom mode after reboot
        mock_scan.return_value = [
            DeviceInfo(
                serial="123456789",
                brand="motorola",
                model="Moto G",
                manufacturer="motorola",
                chipset="qualcomm",
                connection_type="brom"
            )
        ]

        # Mock fastboot command success
        mock_fastboot.return_value = (True, "")

        switched_device = self.auto_bypass._switch_device_mode(moto_g_device, 'brom')
        self.assertIsNotNone(switched_device, "Should successfully switch to brom mode from fastboot")
        self.assertEqual(switched_device.connection_type, 'brom', "Device should be in brom mode after switch")

if __name__ == '__main__':
    unittest.main()