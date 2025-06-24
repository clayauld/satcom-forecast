#!/usr/bin/env python3
"""
Test runner for SatCom Forecast integration tests.
Runs all tests in a logical order and provides comprehensive results.
"""

import asyncio
import sys
import os
import importlib.util
import unittest
from pathlib import Path

def run_test_file(test_file):
    """Run a single test file."""
    print(f"\n{'='*70}")
    print(f"Running: {test_file.name}")
    print(f"{'='*70}")
    
    try:
        # Import and run the test module
        spec = importlib.util.spec_from_file_location("test_module", test_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Run the appropriate test function
        test_functions = [
            'test_core_functionality',
            'test_multi_region', 
            'test_weather_detection',
            'test_summary_length',
            'test_reconfiguration_logic',
            'main'  # For integration structure test
        ]
        
        for func_name in test_functions:
            if hasattr(module, func_name):
                func = getattr(module, func_name)
                if asyncio.iscoroutinefunction(func):
                    result = asyncio.run(func())
                else:
                    result = func()
                return result
        
        # If no specific test function found, try running as unittest
        if hasattr(module, 'TestReconfigurationLogic'):
            # Run unittest tests
            loader = unittest.TestLoader()
            suite = loader.loadTestsFromModule(module)
            runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
            result = runner.run(suite)
            return result.wasSuccessful()
        
        print(f"❌ No test function found in {test_file.name}")
        return False
        
    except Exception as e:
        print(f"❌ Error running {test_file.name}: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all test files in logical order."""
    test_dir = Path(__file__).parent
    
    # Define test order (structure and core functionality first, then specific features)
    test_order = [
        "test_integration_structure.py",   # Integration structure validation
        "test_reconfiguration.py",         # Reconfiguration functionality
        "test_core_functionality.py",      # Basic functionality
        "test_multi_region.py",            # Multi-region testing
        "test_weather_detection.py",       # Weather detection
        "test_summary_length.py",          # Summary format validation
    ]
    
    # Get all test files that exist
    available_tests = []
    for test_name in test_order:
        test_file = test_dir / test_name
        if test_file.exists():
            available_tests.append(test_file)
    
    print("🧪 SatCom Forecast Integration Test Suite")
    print(f"Found {len(available_tests)} test files")
    print("=" * 70)
    
    results = {
        'passed': 0,
        'failed': 0,
        'total': len(available_tests)
    }
    
    for test_file in available_tests:
        success = run_test_file(test_file)
        if success:
            results['passed'] += 1
            print(f"✅ {test_file.name} - PASSED")
        else:
            results['failed'] += 1
            print(f"❌ {test_file.name} - FAILED")
    
    # Final summary
    print(f"\n{'='*70}")
    print("📊 Test Suite Results")
    print(f"{'='*70}")
    print(f"✅ Passed: {results['passed']}/{results['total']}")
    print(f"❌ Failed: {results['failed']}/{results['total']}")
    
    if results['failed'] == 0:
        print(f"\n🎉 All tests passed! The integration is working correctly.")
        return True
    else:
        print(f"\n⚠️  {results['failed']} test(s) failed. Please review the output above.")
        return False

if __name__ == "__main__":
    print("🚀 Starting SatCom Forecast Test Suite\n")
    success = main()
    sys.exit(0 if success else 1) 