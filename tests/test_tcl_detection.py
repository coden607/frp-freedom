from src.ai.ai_engine import AIEngine
from src.bypass.bypass_manager import BypassManager
from src.core.config import Config
from src.core.device_manager import DeviceInfo


def tcl_mtp_device(manufacturer="TCL"):
    return DeviceInfo(
        serial="usb_001_002_1bbb_0001",
        model="TCL USB Device",
        manufacturer=manufacturer,
        brand=manufacturer,
        connection_type="mtp",
    )


def test_ai_recommends_manual_tcl_recovery_for_mtp():
    profile = AIEngine(Config()).analyze_device(tcl_mtp_device())

    assert profile.recommended_methods == ["tcl_manual_recovery_reset"]


def test_tcl_mtp_has_one_selectable_recovery_method():
    methods = BypassManager(Config()).get_recommended_methods(tcl_mtp_device())

    assert [method.name for method in methods] == ["tcl_manual_recovery_reset"]
