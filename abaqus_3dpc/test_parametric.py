# -*- coding: utf-8 -*-
"""
Local validation test for parametric and optimization modules.
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
        from parametric import (
            DesignVariable,
            DesignStudy,
            create_layer_thickness_study,
            create_rebar_ratio_study,
            create_span_depth_study,
            ABAQUS_AVAILABLE
        )
        print("  ✓ parametric.py (Abaqus available: {})".format(ABAQUS_AVAILABLE))
    except Exception as e:
        print("  ✗ parametric.py: {}".format(e))
        return False
    
    try:
        from optimization import (
            ObjectiveFunction,
            Constraint,
            OptimizationProblem,
            GridSearchOptimizer,
            SensitivityAnalyzer,
            ABAQUS_AVAILABLE
        )
        print("  ✓ optimization.py (Abaqus available: {})".format(ABAQUS_AVAILABLE))
    except Exception as e:
        print("  ✗ optimization.py: {}".format(e))
        return False
    
    print("  ⊘ example_parametric.py (requires Abaqus environment)")
    
    return True


def test_design_variable():
    """Test DesignVariable class."""
    print("\nTesting DesignVariable...")
    
    try:
        from parametric import DesignVariable
        
        # Test with min/max
        var1 = DesignVariable(
            name='TestVar1',
            param_path='beam_height',
            min_val=30.0,
            max_val=70.0,
            num_points=5
        )
        values1 = var1.get_values()
        assert len(values1) == 5
        assert values1[0] == 30.0
        assert values1[-1] == 70.0
        print("  ✓ DesignVariable with min/max")
        
        # Test with explicit values
        var2 = DesignVariable(
            name='TestVar2',
            param_path='layer_height',
            values=[5.0, 10.0, 15.0, 20.0]
        )
        values2 = var2.get_values()
        assert len(values2) == 4
        assert values2[0] == 5.0
        print("  ✓ DesignVariable with explicit values")
        
        return True
    except Exception as e:
        print("  ✗ DesignVariable test failed: {}".format(e))
        return False


def test_design_study():
    """Test DesignStudy class."""
    print("\nTesting DesignStudy...")
    
    try:
        from parametric import DesignStudy, DesignVariable
        from config import Config
        
        config = Config()
        study = DesignStudy('TestStudy', config)
        
        # Add variables
        study.add_variable(DesignVariable(
            name='Height',
            param_path='beam_height',
            min_val=30.0,
            max_val=50.0,
            num_points=3
        ))
        
        study.add_variable(DesignVariable(
            name='Width',
            param_path='beam_width',
            values=[80.0, 100.0, 120.0]
        ))
        
        # Generate design points
        points = study.generate_design_points()
        assert len(points) == 9  # 3 x 3
        print("  ✓ DesignStudy generated {} points".format(len(points)))
        
        # Test config creation
        config_dict, point_id = points[0]
        new_config = study.create_config_for_point(config_dict)
        assert new_config.beam_height in [30.0, 40.0, 50.0]
        assert new_config.beam_width in [80.0, 100.0, 120.0]
        print("  ✓ Config creation for design point")
        
        return True
    except Exception as e:
        print("  ✗ DesignStudy test failed: {}".format(e))
        return False


def test_predefined_studies():
    """Test predefined study creation functions."""
    print("\nTesting predefined studies...")
    
    try:
        from parametric import (
            create_layer_thickness_study,
            create_rebar_ratio_study,
            create_span_depth_study
        )
        from config import Config
        
        config = Config()
        
        # Layer thickness study
        study1 = create_layer_thickness_study(config)
        points1 = study1.generate_design_points()
        assert len(points1) == 4  # Default thicknesses [5, 10, 15, 20]
        print("  ✓ Layer thickness study: {} points".format(len(points1)))
        
        # Rebar ratio study
        study2 = create_rebar_ratio_study(config)
        points2 = study2.generate_design_points()
        assert len(points2) == 4  # Default diameters [4, 6, 8, 10]
        print("  ✓ Rebar ratio study: {} points".format(len(points2)))
        
        # Span-depth study with custom parameters
        study3 = create_span_depth_study(
            config,
            spans=[200.0, 250.0, 300.0],
            depths=[30.0, 40.0, 50.0]
        )
        points3 = study3.generate_design_points()
        assert len(points3) == 9  # 3 spans x 3 depths
        print("  ✓ Span-depth study: {} points".format(len(points3)))
        
        return True
    except Exception as e:
        print("  ✗ Predefined studies test failed: {}".format(e))
        import traceback
        traceback.print_exc()
        return False


def test_optimization_problem():
    """Test OptimizationProblem class."""
    print("\nTesting OptimizationProblem...")
    
    try:
        from optimization import OptimizationProblem, ObjectiveFunction, Constraint
        
        problem = OptimizationProblem('TestProblem')
        
        # Add variables
        problem.add_variable('beam_height', 30.0, 100.0, 50.0)
        problem.add_variable('beam_width', 50.0, 150.0, 100.0)
        
        assert len(problem.variables) == 2
        print("  ✓ Added {} design variables".format(len(problem.variables)))
        
        # Add objective
        obj = ObjectiveFunction('Volume', 'MINIMIZE', None, 1.0)
        problem.add_objective(obj)
        
        assert len(problem.objectives) == 1
        print("  ✓ Added objective function")
        
        # Add constraint
        con = Constraint('MaxStress', 'LESS_THAN', 30.0, None)
        problem.add_constraint(con)
        
        assert len(problem.constraints) == 1
        print("  ✓ Added constraint")
        
        # Test current values
        values = problem.get_current_values()
        assert 'beam_height' in values
        assert 'beam_width' in values
        print("  ✓ Current values retrieval")
        
        return True
    except Exception as e:
        print("  ✗ Optimization problem test failed: {}".format(e))
        return False


def test_sensitivity_analyzer():
    """Test SensitivityAnalyzer class."""
    print("\nTesting SensitivityAnalyzer...")
    
    try:
        from optimization import SensitivityAnalyzer
        from config import Config
        
        config = Config()
        analyzer = SensitivityAnalyzer(config)
        
        # Analyze beam_height parameter
        results = analyzer.analyze_parameter(
            'BeamHeight',
            'beam_height',
            variations=[0.8, 0.9, 1.0, 1.1, 1.2]
        )
        
        assert results['parameter'] == 'BeamHeight'
        assert results['base_value'] == config.beam_height
        assert len(results['variations']) == 5
        print("  ✓ Sensitivity analysis for beam_height")
        print("    Base value: {} mm".format(results['base_value']))
        print("    Variations: {}".format([v['value'] for v in results['variations']]))
        
        return True
    except Exception as e:
        print("  ✗ Sensitivity analyzer test failed: {}".format(e))
        return False


def main():
    """Run all tests."""
    print("="*60)
    print("Parametric & Optimization Modules - Local Validation")
    print("="*60)
    
    results = []
    
    results.append(("Imports", test_imports()))
    results.append(("DesignVariable", test_design_variable()))
    results.append(("DesignStudy", test_design_study()))
    results.append(("Predefined Studies", test_predefined_studies()))
    results.append(("OptimizationProblem", test_optimization_problem()))
    results.append(("SensitivityAnalyzer", test_sensitivity_analyzer()))
    
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
