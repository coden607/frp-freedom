#!/usr/bin/env python3
"""
Automatic Bypass Optimizer
Intelligently selects and executes the best bypass methods for detected devices
"""

import logging
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from .intelligent_detector import IntelligentDetector, BypassMode
from .device_manager import DeviceInfo
from .config import Config
from ..bypass.bypass_manager import BypassManager

@dataclass
class BypassResult:
    """Result of a bypass attempt"""
    success: bool
    method: str
    device_serial: str
    execution_time: float
    message: str
    details: Dict = None

class AutoBypassOptimizer:
    """Automatic bypass optimization system"""
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.detector = IntelligentDetector(config)
        self.bypass_manager = BypassManager(config, self.detector.device_manager)
        
        # Method success rates (updated dynamically)
        self.method_performance = {
            'samsung_setup_wizard_2025': 0.95,
            'adb_talkback_chrome': 0.92,
            'accounts_db_modification': 0.90,
            'persist_partition_edit': 0.95,
            'adb_setup_wizard': 0.85,
            'adb_intent_manipulation': 0.88,
            'chrome_intent_exploit': 0.65,
            'emergency_call_exploit': 0.70,
            'framework_patch_android15': 0.78
        }
    
    def run_intelligent_bypass(self) -> Dict[str, List[BypassResult]]:
        """Run intelligent bypass on all detected devices"""
        self.logger.info("Starting intelligent FRP bypass...")
        
        # Step 1: Detect and optimize devices
        devices, device_modes = self.detector.optimize_all_devices()
        
        if not devices:
            self.logger.warning("No devices detected for bypass")
            return {}
        
        self.logger.info(f"Found {len(devices)} devices for bypass")
        
        # Step 2: Execute bypass on each device
        results = {}
        for device in devices:
            self.logger.info(f"Processing device: {device.serial} ({device.manufacturer} {device.model})")
            
            device_results = []
            optimal_mode = device_modes.get(device.serial)
            
            if optimal_mode:
                device_results = self._execute_optimal_bypass(device, optimal_mode)
            else:
                device_results = self._execute_fallback_bypass(device)
            
            results[device.serial] = device_results
            
            # Update method performance based on results
            self._update_method_performance(device_results)
        
        # Step 3: Generate summary
        self._generate_bypass_summary(results)
        
        return results
    
    def _execute_optimal_bypass(self, device: DeviceInfo, mode: BypassMode) -> List[BypassResult]:
        """Execute bypass using optimal methods for the device mode"""
        results = []
        
        self.logger.info(f"Executing {mode.name} bypass on {device.serial}")
        
        # Try methods in order of success rate for this mode
        for method_name in mode.best_methods:
            if method_name in self.method_performance:
                result = self._execute_bypass_method(device, method_name)
                results.append(result)
                
                # If successful, stop trying other methods
                if result.success:
                    self.logger.info(f"Successfully bypassed {device.serial} using {method_name}")
                    break
                
                # Wait between attempts
                time.sleep(2)
        
        return results
    
    def _execute_fallback_bypass(self, device: DeviceInfo) -> List[BypassResult]:
        """Execute fallback bypass methods when optimal mode is not available"""
        results = []
        
        self.logger.info(f"Executing fallback bypass on {device.serial}")
        
        # Sort methods by success rate
        sorted_methods = sorted(self.method_performance.items(), 
                              key=lambda x: x[1], reverse=True)
        
        # Try top 5 methods
        for method_name, success_rate in sorted_methods[:5]:
            result = self._execute_bypass_method(device, method_name)
            results.append(result)
            
            if result.success:
                self.logger.info(f"Successfully bypassed {device.serial} using fallback method {method_name}")
                break
            
            time.sleep(2)
        
        return results
    
    def _execute_bypass_method(self, device: DeviceInfo, method_name: str) -> BypassResult:
        """Execute a specific bypass method on a device"""
        start_time = time.time()
        
        try:
            self.logger.info(f"Executing {method_name} on {device.serial}")
            
            # Execute bypass method
            result = self.bypass_manager.execute_bypass(method_name, device.serial)
            
            execution_time = time.time() - start_time
            
            # Parse result
            success = result.get('result') == 'success'
            message = result.get('message', 'Unknown result')
            details = result.get('details', {})
            
            bypass_result = BypassResult(
                success=success,
                method=method_name,
                device_serial=device.serial,
                execution_time=execution_time,
                message=message,
                details=details
            )
            
            self.logger.info(f"Method {method_name} on {device.serial}: {'SUCCESS' if success else 'FAILED'} ({execution_time:.1f}s)")
            
            return bypass_result
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(f"Exception executing {method_name} on {device.serial}: {e}")
            
            return BypassResult(
                success=False,
                method=method_name,
                device_serial=device.serial,
                execution_time=execution_time,
                message=f"Exception: {str(e)}",
                details={'exception': str(e)}
            )
    
    def _update_method_performance(self, results: List[BypassResult]):
        """Update method performance based on execution results"""
        for result in results:
            if result.method in self.method_performance:
                # Simple moving average update
                current_rate = self.method_performance[result.method]
                if result.success:
                    new_rate = min(0.99, current_rate + 0.01)  # Increase success rate
                else:
                    new_rate = max(0.01, current_rate - 0.005)  # Decrease success rate
                
                self.method_performance[result.method] = new_rate
                self.logger.debug(f"Updated {result.method} success rate: {new_rate:.2%}")
    
    def _generate_bypass_summary(self, results: Dict[str, List[BypassResult]]):
        """Generate and log bypass execution summary"""
        total_devices = len(results)
        successful_devices = sum(1 for device_results in results.values() 
                               if any(r.success for r in device_results))
        
        total_attempts = sum(len(device_results) for device_results in results.values())
        successful_attempts = sum(1 for device_results in results.values() 
                                for r in device_results if r.success)
        
        self.logger.info("=" * 60)
        self.logger.info("FRP BYPASS EXECUTION SUMMARY")
        self.logger.info("=" * 60)
        self.logger.info(f"Total Devices: {total_devices}")
        self.logger.info(f"Successfully Bypassed: {successful_devices} ({successful_devices/total_devices:.1%})")
        self.logger.info(f"Total Attempts: {total_attempts}")
        self.logger.info(f"Successful Attempts: {successful_attempts} ({successful_attempts/total_attempts:.1%})")
        
        for device_serial, device_results in results.items():
            device_success = any(r.success for r in device_results)
            successful_method = next((r.method for r in device_results if r.success), None)
            
            self.logger.info(f"Device {device_serial}: {'SUCCESS' if device_success else 'FAILED'}")
            if device_success:
                self.logger.info(f"  Method: {successful_method}")
            else:
                attempted_methods = [r.method for r in device_results]
                self.logger.info(f"  Attempted: {', '.join(attempted_methods)}")
        
        self.logger.info("=" * 60)
    
    def get_method_recommendations(self, device: DeviceInfo) -> List[str]:
        """Get recommended bypass methods for a specific device"""
        recommendations = []
        
        # Get device characteristics
        manufacturer = device.manufacturer.lower()
        model = device.model.lower()
        connection_type = device.connection_type
        
        # Manufacturer-specific recommendations
        if 'samsung' in manufacturer:
            recommendations.extend([
                'samsung_setup_wizard_2025',
                'accounts_db_modification',
                'persist_partition_edit'
            ])
        elif 'google' in manufacturer or 'pixel' in model:
            recommendations.extend([
                'adb_talkback_chrome',
                'adb_setup_wizard',
                'chrome_intent_exploit'
            ])
        elif 'xiaomi' in manufacturer or 'redmi' in model:
            recommendations.extend([
                'adb_setup_wizard',
                'adb_intent_manipulation',
                'emergency_call_exploit'
            ])
        else:
            # Generic recommendations
            recommendations.extend([
                'adb_setup_wizard',
                'adb_talkback_chrome',
                'accounts_db_modification'
            ])
        
        # Connection type specific filtering
        if connection_type == 'fastboot':
            recommendations = [r for r in recommendations if 'fastboot' in r or 'partition' in r or 'framework' in r]
        elif connection_type == 'adb':
            recommendations = [r for r in recommendations if 'adb' in r or 'chrome' in r or 'setup' in r]
        
        # Sort by performance
        recommendations.sort(key=lambda x: self.method_performance.get(x, 0.5), reverse=True)
        
        return recommendations[:5]  # Return top 5 recommendations
    
    def run_continuous_optimization(self, max_iterations: int = 3, 
                                 wait_time: int = 30) -> Dict[str, List[BypassResult]]:
        """Run continuous optimization with device re-detection"""
        all_results = {}
        
        for iteration in range(max_iterations):
            self.logger.info(f"Starting optimization iteration {iteration + 1}/{max_iterations}")
            
            # Run bypass on current devices
            iteration_results = self.run_intelligent_bypass()
            
            # Merge results
            for device_serial, device_results in iteration_results.items():
                if device_serial not in all_results:
                    all_results[device_serial] = []
                all_results[device_serial].extend(device_results)
            
            # Check if all devices are successfully bypassed
            all_successful = all(
                any(r.success for r in device_results) 
                for device_results in all_results.values()
            )
            
            if all_successful:
                self.logger.info("All devices successfully bypassed!")
                break
            
            # Wait before next iteration
            if iteration < max_iterations - 1:
                self.logger.info(f"Waiting {wait_time} seconds before next iteration...")
                time.sleep(wait_time)
        
        return all_results
