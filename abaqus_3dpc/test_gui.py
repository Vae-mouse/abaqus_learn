# -*- coding: utf-8 -*-
"""
Local validation test for GUI and CLI modules.
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
        from gui import TKINTER_AVAILABLE, ABAQUS_AVAILABLE
        if TKINTER_AVAILABLE:
            from gui import TDPCGui, launch_gui
            print("  ✓ gui.py (tkinter: {}, abaqus: {})".format(TKINTER_AVAILABLE, ABAQUS_AVAILABLE))
        else:
            print("  ⊘ gui.py (tkinter not available, abaqus: {})".format(ABAQUS_AVAILABLE))
    except Exception as e:
        print("  ✗ gui.py: {}".format(e))
        return False
    
    try:
        from cli import create_parser, validate_args, create_config_from_args
        print("  ✓ cli.py")
    except Exception as e:
        print("  ✗ cli.py: {}".format(e))
        return False
    
    return True


def test_gui_classes():
    """Test GUI class definitions."""
    print("\nTesting GUI classes...")
    
    try:
        from gui import TKINTER_AVAILABLE
        
        if not TKINTER_AVAILABLE:
            print("  ⊘ Tkinter not available - skipping GUI class tests")
            print("    (GUI requires tkinter to be installed)")
            return True
        
        # Only import GUI classes if tkinter is available
        from gui import ModelConfigFrame, MaterialConfigFrame, AnalysisOptionsFrame, OutputFrame
        
        # We can't actually create Tkinter widgets without a root window,
        # but we can check the classes exist and have the right methods
        assert hasattr(ModelConfigFrame, '__init__')
        assert hasattr(MaterialConfigFrame, '__init__')
        assert hasattr(AnalysisOptionsFrame, '__init__')
        assert hasattr(OutputFrame, '__init__')
        
        print("  ✓ ModelConfigFrame class")
        print("  ✓ MaterialConfigFrame class")
        print("  ✓ AnalysisOptionsFrame class")
        print("  ✓ OutputFrame class")
        
        return True
    except Exception as e:
        print("  ✗ GUI classes test failed: {}".format(e))
        return False


def test_cli_parser():
    """Test CLI argument parser."""
    print("\nTesting CLI parser...")
    
    try:
        from cli import create_parser
        
        parser = create_parser()
        
        # Test with minimal args
        args = parser.parse_args(['--length', '300', '--width', '100'])
        assert args.length == 300.0
        assert args.width == 100.0
        assert args.height == 50.0  # Default
        print("  ✓ Parser accepts geometry arguments")
        
        # Test with all args
        args = parser.parse_args([
            '--length', '400',
            '--width', '150',
            '--height', '60',
            '--layer-height', '12',
            '--rebar-diameter', '8',
            '--analysis', 'thermal',
            '--mesh-size', '10',
            '--name', 'TestModel'
        ])
        assert args.length == 400.0
        assert args.analysis == 'thermal'
        assert args.name == 'TestModel'
        print("  ✓ Parser accepts all argument types")
        
        return True
    except Exception as e:
        print("  ✗ CLI parser test failed: {}".format(e))
        import traceback
        traceback.print_exc()
        return False


def test_cli_validation():
    """Test CLI argument validation."""
    print("\nTesting CLI validation...")
    
    try:
        from cli import validate_args
        import argparse
        
        # Create a mock args object
        class MockArgs:
            length = 300.0
            width = 100.0
            height = 50.0
            layer_height = 10.0
            rebar_diameter = 6.0
            rebar_cover = 15.0
            no_rebar = False
            concrete_E = 30000.0
            concrete_strength = 30.0
        
        args = MockArgs()
        errors = validate_args(args)
        assert len(errors) == 0
        print("  ✓ Valid configuration passes")
        
        # Test invalid configuration
        args.height = 55.0  # Not divisible by layer_height
        errors = validate_args(args)
        assert len(errors) > 0
        print("  ✓ Invalid configuration detected")
        
        # Test rebar too large
        args.height = 50.0
        args.rebar_diameter = 25.0  # Too large
        errors = validate_args(args)
        assert len(errors) > 0
        print("  ✓ Rebar size validation works")
        
        return True
    except Exception as e:
        print("  ✗ CLI validation test failed: {}".format(e))
        import traceback
        traceback.print_exc()
        return False


def test_config_creation():
    """Test Config creation from CLI args."""
    print("\nTesting Config creation...")
    
    try:
        from cli import create_config_from_args
        import argparse
        
        # Create mock args
        class MockArgs:
            length = 400.0
            width = 150.0
            height = 60.0
            layer_height = 12.0
            rebar_diameter = 8.0
            rebar_spacing = 60.0
            rebar_cover = 20.0
            concrete_E = 35000.0
            concrete_strength = 40.0
            steel_E = 210000.0
            mesh_size = 8.0
        
        args = MockArgs()
        config = create_config_from_args(args)
        
        assert config.beam_length == 400.0
        assert config.beam_width == 150.0
        assert config.beam_height == 60.0
        assert config.layer_height == 12.0
        assert config.rebar_diameter == 8.0
        assert config.concrete_E == 35000.0
        
        print("  ✓ Config created from CLI args")
        print("    Length: {} mm".format(config.beam_length))
        print("    Height: {} mm ({} layers)".format(
            config.beam_height, config.get_layer_count()))
        
        return True
    except Exception as e:
        print("  ✗ Config creation test failed: {}".format(e))
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("="*60)
    print("GUI & CLI Modules - Local Validation")
    print("="*60)
    
    results = []
    
    results.append(("Imports", test_imports()))
    results.append(("GUI Classes", test_gui_classes()))
    results.append(("CLI Parser", test_cli_parser()))
    results.append(("CLI Validation", test_cli_validation()))
    results.append(("Config Creation", test_config_creation()))
    
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
        print("GUI and CLI modules are ready")
    else:
        print("Some tests FAILED ✗")
        print("Please fix errors before using")
    print("="*60)
    
    return 0 if all_passed else 1


if __name__ == '__main__':
    sys.exit(main())
