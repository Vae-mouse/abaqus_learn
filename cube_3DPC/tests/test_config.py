# -*- coding: utf-8 -*-
"""
Test suite for cube_3DPC project
Tests configuration validation and data integrity
Python 2.7 compatible for Abaqus 2021
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import CubeCompressionConfig


def test_config_structure():
    """Test that config class has all required attributes"""
    print("\n[Test] Config structure...")
    
    config = CubeCompressionConfig()
    
    # Required attributes that should exist
    required_attrs = [
        'cube_length_x', 'cube_length_y', 'cube_length_z',
        'num_layers', 'layer_thickness',
        'concrete_E', 'concrete_nu',
        'concrete_comp_hardening',
        'cohesive_Enn', 'cohesive_Ess', 'cohesive_Ett',
        'work_dir', 'model_name', 'job_name',
    ]
    
    missing = []
    for attr in required_attrs:
        if not hasattr(config, attr):
            missing.append(attr)
    
    if missing:
        print("  FAIL: Missing attributes: %s" % missing)
        return False
    
    print("  PASS: All required attributes exist")
    return True


def test_config_validation_empty():
    """Test that validate() raises NotImplementedError for empty config"""
    print("\n[Test] Config validation (empty)...")
    
    config = CubeCompressionConfig()
    
    try:
        config.validate()
        print("  FAIL: Should have raised NotImplementedError")
        return False
    except NotImplementedError as e:
        print("  PASS: Correctly raised NotImplementedError")
        print("    Message: %s" % str(e)[:100] + "...")
        return True
    except Exception as e:
        print("  FAIL: Raised wrong exception: %s" % type(e).__name__)
        return False


def test_config_validation_complete():
    """Test that validate() passes when all parameters are set"""
    print("\n[Test] Config validation (complete)...")
    
    config = CubeCompressionConfig()
    
    # Fill in all required parameters
    config.concrete_E = 30000.0
    config.concrete_nu = 0.2
    config.concrete_comp_hardening = [(20.0, 0.0), (30.0, 0.001)]
    config.cohesive_Enn = 10000.0
    config.cohesive_Ess = 10000.0
    config.cohesive_Ett = 10000.0
    config.loading_displacement = -5.0
    
    try:
        config.validate()
        print("  PASS: Validation passed with complete config")
        return True
    except NotImplementedError as e:
        print("  FAIL: Should not raise NotImplementedError: %s" % str(e))
        return False
    except Exception as e:
        print("  FAIL: Unexpected exception: %s" % type(e).__name__)
        return False


def test_geometry_values():
    """Test that geometry values match .inp file"""
    print("\n[Test] Geometry values...")
    
    config = CubeCompressionConfig()
    
    # From .inp file analysis
    expected = {
        'cube_length_x': 360.0,
        'cube_length_y': 90.0,
        'cube_length_z': 60.0,
        'num_layers': 6,
        'layer_thickness': 15.0,
    }
    
    errors = []
    for key, expected_val in expected.items():
        actual_val = getattr(config, key)
        if actual_val != expected_val:
            errors.append("%s: expected %s, got %s" % (key, expected_val, actual_val))
    
    if errors:
        print("  FAIL: Mismatches found:")
        for e in errors:
            print("    - %s" % e)
        return False
    
    print("  PASS: All geometry values correct")
    return True


def test_layer_naming():
    """Test that layer naming convention is correct"""
    print("\n[Test] Layer naming...")
    
    config = CubeCompressionConfig()
    
    # Should have 18 layer names (6 layers x 3 sections each)
    expected_count = 18
    actual_count = len(config.layer_names)
    
    if actual_count != expected_count:
        print("  FAIL: Expected %d layer names, got %d" % (expected_count, actual_count))
        return False
    
    # Check naming pattern
    expected_pattern = [
        'concrete11', 'concrete12', 'concrete13',
        'concrete21', 'concrete22', 'concrete23',
        'concrete31', 'concrete32', 'concrete33',
        'concrete41', 'concrete42', 'concrete43',
        'concrete51', 'concrete52', 'concrete53',
        'concrete61', 'concrete62', 'concrete63',
    ]
    
    if config.layer_names != expected_pattern:
        print("  FAIL: Layer naming pattern mismatch")
        print("    Expected: %s" % expected_pattern)
        print("    Actual: %s" % config.layer_names)
        return False
    
    print("  PASS: Layer naming convention correct")
    return True


def test_material_defaults():
    """Test that material defaults are reasonable"""
    print("\n[Test] Material defaults...")
    
    config = CubeCompressionConfig()
    
    # These should be None to force user to fill in
    should_be_none = [
        'concrete_E', 'concrete_nu',
        'concrete_comp_hardening',
        'cohesive_Enn', 'cohesive_Ess', 'cohesive_Ett',
    ]
    
    errors = []
    for attr in should_be_none:
        val = getattr(config, attr)
        if val is not None:
            errors.append("%s should be None, got %s" % (attr, val))
    
    # These should have reasonable defaults
    if config.steel_E != 210000.0:
        errors.append("steel_E should be 210000.0, got %s" % config.steel_E)
    
    if config.concrete_density != 2.4e-9:
        errors.append("concrete_density should be 2.4e-9, got %s" % config.concrete_density)
    
    if errors:
        print("  FAIL: Default value issues:")
        for e in errors:
            print("    - %s" % e)
        return False
    
    print("  PASS: Material defaults are correct")
    return True


def run_all_tests():
    """Run all tests and report results"""
    print("=" * 70)
    print("Cube 3DPC Test Suite")
    print("=" * 70)
    
    tests = [
        test_config_structure,
        test_config_validation_empty,
        test_config_validation_complete,
        test_geometry_values,
        test_layer_naming,
        test_material_defaults,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append((test.__name__, result))
        except Exception as e:
            print("  ERROR: %s" % str(e))
            results.append((test.__name__, False))
    
    print("\n" + "=" * 70)
    print("Test Results")
    print("=" * 70)
    
    passed = sum(1 for _, r in results if r)
    failed = sum(1 for _, r in results if not r)
    
    for name, result in results:
        status = "PASS" if result else "FAIL"
        print("  [%s] %s" % (status, name))
    
    print("=" * 70)
    print("Total: %d passed, %d failed" % (passed, failed))
    print("=" * 70)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
