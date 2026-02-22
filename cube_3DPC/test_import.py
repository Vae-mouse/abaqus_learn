# -*- coding: utf-8 -*-
"""
Test import of mesh module
"""

print("Testing mesh module import...")

try:
    from mesh import create_all_mesh_and_sections
    print("SUCCESS: create_all_mesh_and_sections imported successfully")
except ImportError as e:
    print("ERROR: %s" % str(e))
    
    # Try to find what's in mesh module
    import mesh
    print("\nAvailable in mesh module:")
    for name in dir(mesh):
        if not name.startswith('_'):
            print("  - %s" % name)
