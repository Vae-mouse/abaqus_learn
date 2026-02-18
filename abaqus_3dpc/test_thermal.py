# -*- coding: utf-8 -*-
"""
Local validation test for thermal-mechanical coupled module.
Tests Python syntax and imports without Abaqus environment.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    
    try:
        from config import Config
        print("  ✓ config.py")
    except Exception as e:
        print("  ✗ config.py: {}".format(e))
        return False
    
    try:
        from thermal_coupled import (
            add_thermal_properties,
            add_steel_thermal_properties,
            create_thermal_step,
            create_heat_flux_load,
            create_convective_film,
            create_radiation,
            set_initial_temperature,
            create_print_temperature_field,
            setup_thermal_analysis,
            create_layer_activation_with_temperature,
            ABAQUS_AVAILABLE
        )
        print("  ✓ thermal_coupled.py (Abaqus available: {})".format(ABAQUS_AVAILABLE))
    except Exception as e:
        print("  ✗ thermal_coupled.py: {}".format(e))
        return False
    
    # Don't test example_thermal here as it requires Abaqus
    print("  ⊘ example_thermal.py (requires Abaqus environment)")
    
    return True


def test_config():
    """Test Config class."""
    print("\nTesting Config...")
    
    try:
        from config import Config
        config = Config()
        
        # Test basic attributes
        assert config.beam_length == 300.0
        assert config.beam_width == 100.0
        assert config.get_layer_count() == 5
        assert config.validate() == True
        
        print("  ✓ Config validation passed")
        return True
    except Exception as e:
        print("  ✗ Config test failed: {}".format(e))
        return False


def test_thermal_functions():
    """Test thermal function signatures."""
    print("\nTesting thermal function signatures...")
    
    try:
        import inspect
        from thermal_coupled import (
            add_thermal_properties,
            create_thermal_step,
            set_initial_temperature,
            ABAQUS_AVAILABLE
        )
        
        # Check function signatures
        sig1 = inspect.signature(add_thermal_properties)
        assert 'model' in sig1.parameters
        assert 'config' in sig1.parameters
        print("  ✓ add_thermal_properties signature")
        
        sig2 = inspect.signature(create_thermal_step)
        assert 'model' in sig2.parameters
        assert 'step_name' in sig2.parameters
        print("  ✓ create_thermal_step signature")
        
        sig3 = inspect.signature(set_initial_temperature)
        assert 'model' in sig3.parameters
        assert 'region' in sig3.parameters
        assert 'temp' in sig3.parameters
        print("  ✓ set_initial_temperature signature")
        
        print("  ✓ Abaqus available: {}".format(ABAQUS_AVAILABLE))
        
        return True
    except Exception as e:
        print("  ✗ Thermal function test failed: {}".format(e))
        return False


def test_example_thermal():
    """Test example_thermal module structure (skips Abaqus-dependent code)."""
    print("\nTesting example_thermal module...")
    
    # Skip this test as example_thermal requires Abaqus
    print("  ⊘ Skipped (requires Abaqus environment)")
    print("  ⊘ Run example_thermal.py within Abaqus CAE")
    return True


def main():
    """Run all tests."""
    print("="*60)
    print("Thermal-Mechanical Coupled Module - Local Validation")
    print("="*60)
    
    results = []
    
    results.append(("Imports", test_imports()))
    results.append(("Config", test_config()))
    results.append(("Thermal Functions", test_thermal_functions()))
    results.append(("Example Thermal", test_example_thermal()))
    
    print("\n" + "="*60)
    print("Test Results")
    print("="*60)
    
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print("  {}: {}".format(name, status))
    
    all_passed = all(r[1] for r in results)
    
    print("\n" + "="*60)
    if all_passed:
        print("All tests PASSED ✓")
        print("Module is ready for Abaqus testing")
    else:
        print("Some tests FAILED ✗")
        print("Please fix errors before Abaqus testing")
    print("="*60)
    
    return 0 if all_passed else 1


if __name__ == '__main__':
    sys.exit(main())
