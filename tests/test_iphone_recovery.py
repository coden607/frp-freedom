from src.core.iphone_recovery import IPhoneDevice, IPhoneRecoveryManager


def test_parse_ideviceinfo_identifies_iphone_13_family(monkeypatch):
    manager = IPhoneRecoveryManager()

    monkeypatch.setattr(manager, "tool_status", lambda: type("Tools", (), {"ideviceinfo": "/usr/bin/ideviceinfo"})())
    monkeypatch.setattr(
        "src.core.iphone_recovery.subprocess.run",
        lambda *args, **kwargs: type(
            "Result",
            (),
            {
                "returncode": 0,
                "stdout": (
                    "ProductType: iPhone14,5\n"
                    "UniqueDeviceID: test-udid\n"
                    "DeviceName: Owner iPhone\n"
                ),
            },
        )(),
    )

    device = manager._scan_ideviceinfo()

    assert device is not None
    assert device.serial == "test-udid"
    assert device.mode == "normal"
    assert device.model_identifier == "iPhone14,5"
    assert device.marketing_name == "iPhone 13"
    assert device.is_iphone_13_family


def test_linux_readiness_report_marks_restore_ready_when_tools_exist(monkeypatch):
    manager = IPhoneRecoveryManager()
    monkeypatch.setattr(
        manager,
        "tool_status",
        lambda: type(
            "Tools",
            (),
            {
                "idevicerestore": "/usr/bin/idevicerestore",
                "ideviceinfo": "/usr/bin/ideviceinfo",
                "ideviceenterrecovery": "/usr/bin/ideviceenterrecovery",
                "idevicepair": "/usr/bin/idevicepair",
                "usbmuxd": "/usr/sbin/usbmuxd",
                "lsusb": "/usr/bin/lsusb",
            },
        )(),
    )

    report = manager.linux_readiness_report()

    assert report["restore_ready"] == "yes"
    assert report["idevicerestore"] == "/usr/bin/idevicerestore"


def test_prepare_device_for_restore_requests_recovery_for_normal_device(monkeypatch):
    manager = IPhoneRecoveryManager()
    normal = IPhoneDevice(
        serial="test-udid",
        mode="normal",
        product_id="unknown",
        description="Owner iPhone (iPhone 13)",
        model_identifier="iPhone14,5",
    )
    recovery = IPhoneDevice(
        serial="usb_001_002_05ac_1281",
        mode="recovery",
        product_id="1281",
        description="Apple Mobile Device (Recovery Mode)",
    )
    calls = []

    monkeypatch.setattr(manager, "enter_recovery_mode", lambda device, output_callback=None: calls.append(device) or True)
    monkeypatch.setattr(
        manager,
        "wait_for_restore_ready_device",
        lambda timeout_seconds, poll_interval, output_callback=None: recovery,
    )

    prepared = manager.prepare_device_for_restore(normal)

    assert prepared is recovery
    assert calls == [normal]


def test_erase_device_restores_after_prepare(monkeypatch):
    manager = IPhoneRecoveryManager()
    selected = IPhoneDevice(
        serial="usb_001_002_05ac_1281",
        mode="recovery",
        product_id="1281",
        description="Apple Mobile Device (Recovery Mode)",
    )
    restored = []

    monkeypatch.setattr(manager, "prepare_device_for_restore", lambda device, output_callback=None: selected)
    monkeypatch.setattr(
        manager,
        "restore_latest_firmware",
        lambda device, output_callback=None: restored.append(device) or 0,
    )

    assert manager.erase_device(selected) == 0
    assert restored == [selected]

