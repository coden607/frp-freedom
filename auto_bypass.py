#!/usr/bin/env python3
"""
Auto FRP Bypass Tool
Intelligent device detection and automatic FRP bypass execution
"""

import sys
import logging
import time
from pathlib import Path

# Add the src directory to the Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.core.auto_bypass_optimizer import AutoBypassOptimizer
from src.core.config import Config
from src.core.logger import setup_logging

def main():
    """Main auto bypass execution"""
    try:
        # Setup logging
        setup_logging()
        logger = logging.getLogger(__name__)
        
        logger.info("Starting Auto FRP Bypass Tool")
        logger.info("This tool will automatically detect devices and execute optimal bypass methods")
        
        # Load configuration
        config = Config()
        
        # Initialize auto bypass optimizer
        optimizer = AutoBypassOptimizer(config)
        
        # Run intelligent bypass
        logger.info("Starting intelligent device detection and bypass...")
        results = optimizer.run_intelligent_bypass()
        
        if not results:
            logger.warning("No devices were detected for bypass")
            logger.info("Please ensure devices are connected and try again")
            return
        
        # Check results
        total_devices = len(results)
        successful_devices = sum(1 for device_results in results.values() 
                                 if any(r.success for r in device_results))
        
        if successful_devices == total_devices:
            logger.info(f"🎉 SUCCESS: All {total_devices} devices bypassed successfully!")
        elif successful_devices > 0:
            logger.info(f"⚠️ PARTIAL SUCCESS: {successful_devices}/{total_devices} devices bypassed")
        else:
            logger.info(f"❌ FAILED: No devices were successfully bypassed")
        
        # Offer continuous optimization
        if successful_devices < total_devices:
            logger.info("Running continuous optimization...")
            continuous_results = optimizer.run_continuous_optimization(max_iterations=2)
            
            # Re-check results
            final_successful = sum(1 for device_results in continuous_results.values() 
                                  if any(r.success for r in device_results))
            
            if final_successful == total_devices:
                logger.info(f"🎉 SUCCESS AFTER OPTIMIZATION: All {total_devices} devices bypassed!")
        
        logger.info("Auto FRP Bypass Tool execution completed")
        
    except KeyboardInterrupt:
        logger.info("Auto bypass interrupted by user")
    except Exception as e:
        logger.error(f"Auto bypass failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
