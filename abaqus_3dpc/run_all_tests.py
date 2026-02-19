#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive test suite for 3DPC project.
Runs all tests and generates a unified test report.
"""

import sys
import os
import time
import json
from datetime import datetime

# Test results storage
results = {
    "timestamp": datetime.now().isoformat(),
    "tests": [],
    "summary": {
        "total": 0,
        "passed": 0,
        "failed": 0,
        "skipped": 0
    }
}


def log_test(name, status, message="", duration=0):
    """Log a test result."""
    results["tests"].append({
        "name": name,
        "status": status,
        "message": message,
        "duration": duration
    })
    results["summary"]["total"] += 1
    if status == "PASS":
        results["summary"]["passed"] += 1
    elif status == "FAIL":
        results["summary"]["failed"] += 1
    else:
        results["summary"]["skipped"] += 1


def run_test(name, test_func):
    """Run a single test."""
    print("  Testing: {}...".format(name), end=" ")
    start = time.time()
    try:
        test_func()
        duration = time.time() - start
        log_test(name, "PASS", "", duration)
        print("✓ ({:.2f}s)".format(duration))
        return True
    except Exception as e:
        duration = time.time() - start
        log_test(name, "FAIL", str(e), duration)
        print("✗ ({:.2f}s)".format(duration))
        print("    Error: {}".format(e))
        return False


def test_config_module():
    """Test config module."""
    from config import Config
    config = Config()
    assert config.beam_length == 300.0
    assert config.get_layer_count() == 5
    assert config.validate() == True


def test_parametric_module():
    """Test parametric module."""
    from parametric import DesignVariable, DesignStudy
    from config import Config
    
    var = DesignVariable("Test", "beam_height", min_val=30, max_val=50, num_points=3)
    assert len(var.get_values()) == 3
    
    study = DesignStudy("TestStudy", Config())
    study.add_variable(var)
    points = study.generate_design_points()
    assert len(points) == 3


def test_optimization_module():
    """Test optimization module."""
    from optimization import OptimizationProblem, ObjectiveFunction
    
    problem = OptimizationProblem("Test")
    problem.add_variable("height", 30, 100, 50)
    assert len(problem.variables) == 1
    
    obj = ObjectiveFunction("Volume", "MINIMIZE")
    problem.add_objective(obj)
    assert len(problem.objectives) == 1


def test_damage_module():
    """Test damage module."""
    from damage_plasticity import add_cdp_properties, ABAQUS_AVAILABLE
    # Just test import and basic structure
    assert callable(add_cdp_properties) or not ABAQUS_AVAILABLE


def test_xfem_module():
    """Test XFEM module."""
    from xfem_crack import create_fracture_criterion, ABAQUS_AVAILABLE
    assert callable(create_fracture_criterion) or not ABAQUS_AVAILABLE


def test_thermal_module():
    """Test thermal module."""
    from thermal_coupled import add_thermal_properties, ABAQUS_AVAILABLE
    assert callable(add_thermal_properties) or not ABAQUS_AVAILABLE


def test_cli_module():
    """Test CLI module."""
    from cli import create_parser, validate_args
    
    parser = create_parser()
    args = parser.parse_args(["--length", "300"])
    assert args.length == 300.0
    
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
    
    errors = validate_args(MockArgs())
    assert len(errors) == 0


def test_gui_module():
    """Test GUI module."""
    from gui import TKINTER_AVAILABLE, ABAQUS_AVAILABLE
    # Just verify imports work
    assert TKINTER_AVAILABLE is not None
    assert ABAQUS_AVAILABLE is not None


def test_file_structure():
    """Test that all expected files exist."""
    expected_files = [
        "config.py", "materials.py", "geometry.py", "rebar.py",
        "embedded.py", "element_birth.py", "meshing.py", "cohesive.py",
        "postprocess.py", "thermal_coupled.py", "damage_plasticity.py",
        "xfem_crack.py", "parametric.py", "optimization.py",
        "gui.py", "cli.py", "main_complete.py", "minimal_test.py",
        "example.py", "example_thermal.py", "example_damage.py",
        "example_parametric.py", "README.md", "TODO.md"
    ]
    
    project_dir = os.path.dirname(os.path.abspath(__file__))
    for filename in expected_files:
        filepath = os.path.join(project_dir, filename)
        assert os.path.exists(filepath), "Missing file: {}".format(filename)


def test_documentation():
    """Test that documentation files are valid."""
    project_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Check README exists and has content
    readme_path = os.path.join(project_dir, "README.md")
    with open(readme_path, 'r') as f:
        content = f.read()
        assert len(content) > 100
        assert "3D" in content or "3DPC" in content
    
    # Check TODO exists
    todo_path = os.path.join(project_dir, "TODO.md")
    assert os.path.exists(todo_path)


def run_all_tests():
    """Run all tests."""
    print("=" * 70)
    print(" 3DPC Comprehensive Test Suite")
    print(" Started: {}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    print("=" * 70)
    print()
    
    # Core module tests
    print("Core Module Tests:")
    print("-" * 70)
    run_test("Config Module", test_config_module)
    print()
    
    # Enhanced module tests
    print("Enhanced Module Tests:")
    print("-" * 70)
    run_test("Parametric Module", test_parametric_module)
    run_test("Optimization Module", test_optimization_module)
    run_test("Damage Module", test_damage_module)
    run_test("XFEM Module", test_xfem_module)
    run_test("Thermal Module", test_thermal_module)
    print()
    
    # Interface tests
    print("Interface Tests:")
    print("-" * 70)
    run_test("CLI Module", test_cli_module)
    run_test("GUI Module", test_gui_module)
    print()
    
    # Project structure tests
    print("Project Structure Tests:")
    print("-" * 70)
    run_test("File Structure", test_file_structure)
    run_test("Documentation", test_documentation)
    print()
    
    # Print summary
    print("=" * 70)
    print(" Test Summary")
    print("=" * 70)
    print("  Total:   {}".format(results["summary"]["total"]))
    print("  Passed:  {}".format(results["summary"]["passed"]))
    print("  Failed:  {}".format(results["summary"]["failed"]))
    print("  Skipped: {}".format(results["summary"]["skipped"]))
    print()
    
    if results["summary"]["failed"] == 0:
        print("  ✓ All tests PASSED!")
    else:
        print("  ✗ Some tests FAILED")
    print("=" * 70)


def save_report():
    """Save test report to file."""
    report_path = "test_report.json"
    with open(report_path, 'w') as f:
        json.dump(results, f, indent=2)
    print("\nTest report saved to: {}".format(report_path))


def generate_text_report():
    """Generate human-readable text report."""
    lines = []
    lines.append("=" * 70)
    lines.append(" 3DPC Test Report")
    lines.append(" Generated: {}".format(results["timestamp"]))
    lines.append("=" * 70)
    lines.append("")
    
    lines.append("Summary:")
    lines.append("  Total Tests:   {}".format(results["summary"]["total"]))
    lines.append("  Passed:        {}".format(results["summary"]["passed"]))
    lines.append("  Failed:        {}".format(results["summary"]["failed"]))
    lines.append("  Success Rate:  {:.1f}%".format(
        100 * results["summary"]["passed"] / results["summary"]["total"]
        if results["summary"]["total"] > 0 else 0
    ))
    lines.append("")
    
    lines.append("Detailed Results:")
    lines.append("-" * 70)
    for test in results["tests"]:
        status_symbol = "✓" if test["status"] == "PASS" else "✗" if test["status"] == "FAIL" else "⊘"
        lines.append("  {} {:30s} ({:.2f}s)".format(
            status_symbol, test["name"], test["duration"]
        ))
        if test["message"]:
            lines.append("      {}".format(test["message"]))
    lines.append("")
    lines.append("=" * 70)
    
    return "\n".join(lines)


def main():
    """Main entry point."""
    project_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, project_dir)
    
    try:
        run_all_tests()
        save_report()
        
        # Also save text report
        text_report = generate_text_report()
        with open("test_report.txt", 'w') as f:
            f.write(text_report)
        print("Text report saved to: test_report.txt")
        
        # Return exit code
        return 0 if results["summary"]["failed"] == 0 else 1
        
    except Exception as e:
        print("\nFatal error running tests: {}".format(e))
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
