# -*- coding: utf-8 -*-
"""
Local validation test for damage and crack simulation modules.
Tests Python syntax and imports without Abaqus environment.
"""

import sys
import os

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
        from damage_plasticity import (
            add_cdp_properties,
            add_layer_dependent_cdp,
            create_damage_field_output,
            create_damage_history_output,
            setup_cdp_analysis,
            ABAQUS_AVAILABLE
        )
        print("  ✓ damage_plasticity.py (Abaqus available: {})".format(ABAQUS_AVAILABLE))
    except Exception as e:
        print("  ✗ damage_plasticity.py: {}".format(e))
        return False
    
    try:
        from xfem_crack import (
            create_xfem_crack,
            create_xfem_enrichment,
            create_fracture_criterion,
            create_damage_evolution,
            setup_xfem_analysis,
            create_interlayer_crack_region,
            ABAQUS_AVAILABLE
        )
        print("  ✓ xfem_crack.py (Abaqus available: {})".format(ABAQUS_AVAILABLE))
    except Exception as e:
        print("  ✗ xfem_crack.py: {}".format(e))
        return False
    
    print("  ⊘ example_damage.py (requires Abaqus environment)")
    
    return True


def test_cdp_functions():
    """Test CDP function signatures."""
    print("\nTesting CDP function signatures...")
    
    try:
        import inspect
        from damage_plasticity import (
            add_cdp_properties,
            add_layer_dependent_cdp,
            setup_cdp_analysis
        )
        
        sig1 = inspect.signature(add_cdp_properties)
        assert 'model' in sig1.parameters
        assert 'config' in sig1.parameters
        print("  ✓ add_cdp_properties signature")
        
        sig2 = inspect.signature(add_layer_dependent_cdp)
        assert 'model' in sig2.parameters
        assert 'layer_strength_factor' in sig2.parameters
        print("  ✓ add_layer_dependent_cdp signature")
        
        sig3 = inspect.signature(setup_cdp_analysis)
        assert 'model' in sig3.parameters
        assert 'assembly' in sig3.parameters
        assert 'include_interlayer_weakness' in sig3.parameters
        print("  ✓ setup_cdp_analysis signature")
        
        return True
    except Exception as e:
        print("  ✗ CDP function test failed: {}".format(e))
        return False


def test_xfem_functions():
    """Test XFEM function signatures."""
    print("\nTesting XFEM function signatures...")
    
    try:
        import inspect
        from xfem_crack import (
            create_fracture_criterion,
            create_damage_evolution,
            setup_xfem_analysis
        )
        
        sig1 = inspect.signature(create_fracture_criterion)
        assert 'model' in sig1.parameters
        assert 'criterion_type' in sig1.parameters
        print("  ✓ create_fracture_criterion signature")
        
        sig2 = inspect.signature(create_damage_evolution)
        assert 'model' in sig2.parameters
        assert 'value' in sig2.parameters
        print("  ✓ create_damage_evolution signature")
        
        sig3 = inspect.signature(setup_xfem_analysis)
        assert 'model' in sig3.parameters
        assert 'crack_regions' in sig3.parameters
        assert 'fracture_energy' in sig3.parameters
        print("  ✓ setup_xfem_analysis signature")
        
        return True
    except Exception as e:
        print("  ✗ XFEM function test failed: {}".format(e))
        return False


def test_config():
    """Test Config with CDP parameters."""
    print("\nTesting Config for CDP analysis...")
    
    try:
        from config import Config
        config = Config()
        
        # Test basic attributes
        assert config.concrete_comp_strength > 0
        assert config.concrete_E > 0
        
        # Calculate derived CDP parameters
        ft = 0.1 * config.concrete_comp_strength  # Tensile strength
        gf = 70.0  # Fracture energy
        
        print("  ✓ Concrete compressive strength: {} MPa".format(config.concrete_comp_strength))
        print("  ✓ Estimated tensile strength: {} MPa".format(ft))
        print("  ✓ Fracture energy: {} N/m".format(gf))
        
        return True
    except Exception as e:
        print("  ✗ Config test failed: {}".format(e))
        return False


def main():
    """Run all tests."""
    print("="*60)
    print("Damage & Crack Simulation Modules - Local Validation")
    print("="*60)
    
    results = []
    
    results.append(("Imports", test_imports()))
    results.append(("CDP Functions", test_cdp_functions()))
    results.append(("XFEM Functions", test_xfem_functions()))
    results.append(("Config", test_config()))
    
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
        print("Modules are ready for Abaqus testing")
    else:
        print("Some tests FAILED ✗")
        print("Please fix errors before Abaqus testing")
    print("="*60)
    
    return 0 if all_passed else 1


if __name__ == '__main__':
    sys.exit(main())
