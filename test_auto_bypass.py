#!/usr/bin/env python3
"""
Test script for FRP Freedom Auto Bypass functionality
"""

import logging
import sys
import os
from pathlib import Path

# Add the src directory to the Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.core.device_manager import DeviceManager
from src.core.config import Config
from src.bypass.auto_bypass_manager import AutoBypassManager
from src.bypass.bypass_manager import BypassManager

def progress_callback(message: str, percentage: int):
    """Progress callback for auto bypass"""
    print(f"[{percentage}%] {message}")

def main():
    """Main test function"""
    try:
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        logger = logging.getLogger(__name__)

        logger.info("Starting FRP Freedom Auto Bypass Test")

        # Load configuration
        config = Config()
        config.set('auto_bypass.enabled', True)
        config.set('app.debug_mode', True)

        # Initialize components
        device_manager = DeviceManager(config)
        bypass_manager = BypassManager(config, device_manager)

        # Create auto bypass manager
        auto_bypass = AutoBypassManager(config, device_manager, bypass_manager)

        # Start auto bypass
        logger.info("Starting auto bypass process...")
        result = auto_bypass.start_auto_bypass(progress_callback)

        # Display results
        logger.info("\n=== Auto Bypass Results ===")
        logger.info(f"Overall Result: {result['result']}")
        logger.info(f"Message: {result['message']}")
        logger.info(f"Details: {result['details']}")

        if result['result'] == 'SUCCESS':
            logger.info("FRP bypass completed successfully!")
        else:
            logger.error("FRP bypass failed. Check device connection and try again.")

    except Exception as e:
        logging.error(f"Test failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()