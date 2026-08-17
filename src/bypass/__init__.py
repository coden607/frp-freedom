#!/usr/bin/env python3
"""
Bypass module for FRP Freedom
Contains all FRP bypass methods and management functionality
"""

from .types import BypassMethod, BypassResult

__all__ = [
    'BypassManager',
    'BypassMethod',
    'BypassResult',
    'ADBExploitManager',
    'InterfaceExploitManager',
    'SystemExploitManager',
    'HardwareExploitManager'
]


def __getattr__(name):
    """Load manager classes lazily to keep shared types importable."""
    managers = {
        'BypassManager': ('.bypass_manager', 'BypassManager'),
        'ADBExploitManager': ('.adb_exploits', 'ADBExploitManager'),
        'InterfaceExploitManager': ('.interface_exploits', 'InterfaceExploitManager'),
        'SystemExploitManager': ('.system_exploits', 'SystemExploitManager'),
        'HardwareExploitManager': ('.hardware_exploits', 'HardwareExploitManager'),
    }
    if name not in managers:
        raise AttributeError(name)

    import importlib

    module_name, attribute = managers[name]
    value = getattr(importlib.import_module(module_name, __name__), attribute)
    globals()[name] = value
    return value
