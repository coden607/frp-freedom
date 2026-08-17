#!/usr/bin/env python3
"""
Wait for an iPhone in recovery/DFU mode, then erase and restore latest iOS.

This uses Apple's standard restore flow through libimobiledevice's
idevicerestore. It does not bypass Activation Lock.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.core.iphone_recovery import IPhoneRecoveryManager


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Automatically erase/restore an iPhone when it is plugged in recovery or DFU mode."
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Skip the safety confirmation and start restore as soon as a recovery/DFU iPhone is detected.",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=None,
        help="Seconds to wait for a recovery/DFU iPhone. Default: wait forever.",
    )
    parser.add_argument(
        "--poll",
        type=float,
        default=2.0,
        help="Seconds between USB scans. Default: 2.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Print Linux restore-tool readiness and exit.",
    )
    parser.add_argument(
        "--iphone13-steps",
        action="store_true",
        help="Print iPhone 13 recovery-mode button steps and exit.",
    )
    return parser.parse_args()


def print_status(message: str) -> None:
    print(message, flush=True)


def main() -> int:
    args = parse_args()
    manager = IPhoneRecoveryManager()
    tools = manager.tool_status()

    if args.check:
        for name, value in manager.linux_readiness_report().items():
            print(f"{name}: {value}")
        return 0 if tools.can_restore else 127

    if args.iphone13_steps:
        print("iPhone 13 recovery mode button sequence:")
        for index, step in enumerate(manager.iphone_13_recovery_steps(), 1):
            print(f"{index}. {step}")
        print()
        for step in manager.apple_account_recovery_steps():
            print(f"- {step}")
        return 0

    if not tools.idevicerestore:
        print(
            "idevicerestore is not installed. Install libimobiledevice/idevicerestore first.",
            file=sys.stderr,
        )
        return 127

    print("iPhone auto restore is armed.")
    print("This will erase the iPhone and install the latest signed iOS firmware.")
    print("It will not bypass Activation Lock; setup may require the linked Apple Account.")
    print("Put the iPhone in recovery or DFU mode, then plug it in by USB.")

    if not args.yes:
        answer = input("Type ERASE to arm automatic restore: ").strip()
        if answer != "ERASE":
            print("Cancelled.")
            return 1

    return manager.auto_restore_when_connected(
        timeout_seconds=args.timeout,
        poll_interval=args.poll,
        output_callback=print_status,
    )


if __name__ == "__main__":
    raise SystemExit(main())
