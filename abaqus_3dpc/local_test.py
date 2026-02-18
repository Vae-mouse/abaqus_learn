# -*- coding: utf-8 -*-
"""
Local syntax and import test for 3DPC model.
Validates code without running Abaqus.
"""

import ast
import sys
import os


def check_python_syntax(file_path):
    """Check if Python file has valid syntax."""
    try:
        with open(file_path, 'r') as f:
            source = f.read()
        ast.parse(source)
        return True, None
    except SyntaxError as e:
        return False, str(e)


def test_module_imports():
    """Test that modules can be imported (without Abaqus)."""
    print("Testing module structure...")
    
    # Add project directory to path
    project_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, project_dir)
    
    modules_to_test = [
        'config',
    ]
    
    results = {}
    
    for module_name in modules_to_test:
        try:
            # Only test config module (others require Abaqus)
            if module_name == 'config':
                module = __import__(module_name)
                # Try to instantiate Config
                config_class = getattr(module, 'Config')
                config = config_class()
                config.validate()
                results[module_name] = (True, "OK")
            else:
                results[module_name] = (True, "Skipped (requires Abaqus)")
        except Exception as e:
            results[module_name] = (False, str(e))
    
    return results


def check_all_files():
    """Check all Python files in the project."""
    print("Checking Python file syntax...")
    
    project_dir = os.path.dirname(os.path.abspath(__file__))
    
    files_to_check = [
        'config.py',
        'materials.py',
        'geometry.py',
        'rebar.py',
        'printing.py',
        'testing.py',
        'embedded.py',
        'element_birth.py',
        'meshing.py',
        'cohesive.py',
        'main.py',
        'remote_test.py',
    ]
    
    all_ok = True
    results = {}
    
    for filename in files_to_check:
        file_path = os.path.join(project_dir, filename)
        if os.path.exists(file_path):
            ok, error = check_python_syntax(file_path)
            results[filename] = (ok, error)
            if not ok:
                all_ok = False
        else:
            results[filename] = (False, "File not found")
            all_ok = False
    
    return all_ok, results


def validate_abaqus_api_usage():
    """Validate Abaqus API usage patterns."""
    print("\nValidating Abaqus API patterns...")
    
    issues = []
    
    # Check main.py for required imports
    main_file = os.path.join(os.path.dirname(__file__), 'main.py')
    with open(main_file, 'r') as f:
        content = f.read()
    
    required_imports = [
        'from abaqus import',
        'from abaqusConstants import',
        'from driverUtils import executeOnCaeStartup',
    ]
    
    for imp in required_imports:
        if imp in content:
            print("  ✓ Found: %s" % imp)
        else:
            print("  ✗ Missing: %s" % imp)
            issues.append("Missing import: %s" % imp)
    
    # Check for proper module imports
    module_imports = [
        'from config import',
        'from embedded import',
        'from element_birth import',
        'from meshing import',
    ]
    
    for imp in module_imports:
        if imp in content:
            print("  ✓ Found: %s" % imp)
        else:
            print("  ✗ Missing: %s" % imp)
            issues.append("Missing import: %s" % imp)
    
    return len(issues) == 0, issues


def main():
    """Run all validation tests."""
    print("=" * 70)
    print("3DPC Model Validation Test")
    print("=" * 70)
    
    # Test 1: Syntax check
    print("\n[1/3] Syntax Check")
    all_ok, file_results = check_all_files()
    
    for filename, (ok, error) in file_results.items():
        status = "✓" if ok else "✗"
        print("  %s %s" % (status, filename))
        if error and not ok:
            print("      Error: %s" % error)
    
    # Test 2: Module imports
    print("\n[2/3] Module Import Test")
    import_results = test_module_imports()
    
    for module_name, (ok, msg) in import_results.items():
        status = "✓" if ok else "✗"
        print("  %s %s: %s" % (status, module_name, msg))
    
    # Test 3: API validation
    print("\n[3/3] Abaqus API Validation")
    api_ok, api_issues = validate_abaqus_api_usage()
    
    if api_issues:
        for issue in api_issues:
            print("  ✗ %s" % issue)
    
    # Summary
    print("\n" + "=" * 70)
    if all_ok and api_ok:
        print("✓ All validation tests passed!")
        print("\nThe model is ready for testing on cao device.")
        print("Run: python remote_test.py")
    else:
        print("✗ Some validation tests failed.")
        print("Please fix the issues above before remote testing.")
    print("=" * 70)
    
    return all_ok and api_ok


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
