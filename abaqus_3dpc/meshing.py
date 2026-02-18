# -*- coding: utf-8 -*-
"""
Mesh generation for 3D printed concrete model.
Creates structured mesh for concrete beam and rebar.
"""

from abaqus import *
from abaqusConstants import *
import mesh
import regionToolset


def mesh_concrete_beam(part, config):
    """
    Generate structured mesh for concrete beam.
    
    Uses C3D8R (8-node brick with reduced integration) elements
    for the concrete beam.
    
    Args:
        part: Concrete beam part object
        config: Config object
        
    Returns:
        bool: True if meshing successful
    """
    print("  Meshing concrete beam...")
    
    # Set element type for concrete (C3D8R)
    elem_type_1 = mesh.ElemType(
        elemCode=C3D8R,
        elemLibrary=STANDARD,
        hourglassControl=DEFAULT,
        distortionControl=DEFAULT
    )
    
    # Alternative: C3D8I (incompatible modes) for better bending behavior
    elem_type_2 = mesh.ElemType(
        elemCode=C3D8I,
        elemLibrary=STANDARD
    )
    
    # Get all cells
    cells = part.cells
    
    # Assign element type to all cells
    region = regionToolset.Region(cells=cells)
    part.setElementType(
        regions=region,
        elemTypes=(elem_type_1,)
    )
    
    # Set mesh controls
    # Use structured mesh for regular geometry
    part.setMeshControls(
        regions=cells,
        elemShape=HEX,
        technique=STRUCTURED
    )
    
    # Seed edges for mesh density control
    # Seed along length (x-direction)
    edges_x = part.edges.findAt(
        coordinates=[(config.beam_length/2, 0, 0)],
        tolerance=config.beam_width
    )
    if edges_x:
        part.seedEdgeBySize(
            edges=edges_x,
            size=config.mesh_size,
            deviationFactor=0.1,
            constraint=FINER
        )
    
    # Seed along width (y-direction)
    edges_y = part.edges.findAt(
        coordinates=[(0, config.beam_width/2, 0)],
        tolerance=config.beam_length
    )
    if edges_y:
        part.seedEdgeBySize(
            edges=edges_y,
            size=config.mesh_size,
            deviationFactor=0.1,
            constraint=FINER
        )
    
    # Seed along height (z-direction) - layer height
    edges_z = part.edges.findAt(
        coordinates=[(0, 0, config.beam_height/2)],
        tolerance=config.beam_length
    )
    if edges_z:
        # Use smaller size in z-direction for better layer resolution
        z_mesh_size = min(config.mesh_size, config.layer_height / 2)
        part.seedEdgeBySize(
            edges=edges_z,
            size=z_mesh_size,
            deviationFactor=0.1,
            constraint=FINER
        )
    
    # Generate mesh
    part.generateMesh()
    
    # Report mesh statistics
    elem_count = len(part.elements)
    node_count = len(part.nodes)
    print("    Concrete mesh: %d elements, %d nodes" % (elem_count, node_count))
    
    return True


def mesh_rebar(part, config):
    """
    Generate mesh for rebar (truss elements).
    
    Uses T3D2 (2-node linear 3D truss) elements.
    
    Args:
        part: Rebar part object
        config: Config object
        
    Returns:
        bool: True if meshing successful
    """
    print("  Meshing rebar...")
    
    # Set element type for rebar (T3D2 - 2-node truss)
    elem_type = mesh.ElemType(
        elemCode=T3D2,
        elemLibrary=STANDARD
    )
    
    # Get all edges (wires)
    edges = part.edges
    
    # Assign element type
    region = regionToolset.Region(edges=edges)
    part.setElementType(
        regions=region,
        elemTypes=(elem_type,)
    )
    
    # Set mesh controls for edges
    part.setMeshControls(
        regions=edges,
        elemShape=LINE,
        technique=STRUCTURED
    )
    
    # Seed edges
    # Use smaller mesh size for rebar to ensure nodes align with concrete
    rebar_mesh_size = config.mesh_size / 2
    
    part.seedPart(
        size=rebar_mesh_size,
        deviationFactor=0.1,
        minSizeFactor=0.1
    )
    
    # Generate mesh
    part.generateMesh()
    
    # Report mesh statistics
    elem_count = len(part.elements)
    node_count = len(part.nodes)
    print("    Rebar mesh: %d elements, %d nodes" % (elem_count, node_count))
    
    return True


def mesh_all_parts(model, config):
    """
    Mesh all parts in the model.
    
    Args:
        model: Abaqus model object
        config: Config object
        
    Returns:
        dict: Dictionary with mesh statistics
    """
    results = {
        'concrete_elements': 0,
        'concrete_nodes': 0,
        'rebar_elements': 0,
        'rebar_nodes': 0
    }
    
    print("\n[Mesh Generation]")
    
    # Mesh concrete beam
    if 'ConcreteBeam' in model.parts.keys():
        concrete_part = model.parts['ConcreteBeam']
        mesh_concrete_beam(concrete_part, config)
        results['concrete_elements'] = len(concrete_part.elements)
        results['concrete_nodes'] = len(concrete_part.nodes)
    
    # Mesh rebar
    if 'RebarMesh' in model.parts.keys():
        rebar_part = model.parts['RebarMesh']
        mesh_rebar(rebar_part, config)
        results['rebar_elements'] = len(rebar_part.elements)
        results['rebar_nodes'] = len(rebar_part.nodes)
    
    # Print summary
    print("\n  Mesh Summary:")
    print("    Concrete: %d elements, %d nodes" % (
        results['concrete_elements'], results['concrete_nodes']))
    print("    Rebar: %d elements, %d nodes" % (
        results['rebar_elements'], results['rebar_nodes']))
    
    return results


def verify_mesh_quality(model, config):
    """
    Verify mesh quality and report potential issues.
    
    Args:
        model: Abaqus model object
        config: Config object
        
    Returns:
        bool: True if mesh quality is acceptable
    """
    print("\n[Mesh Quality Check]")
    
    issues = []
    
    # Check concrete mesh
    if 'ConcreteBeam' in model.parts.keys():
        concrete_part = model.parts['ConcreteBeam']
        
        # Check for unmeshed regions
        unmeshed_cells = [cell for cell in concrete_part.cells 
                         if cell not in [elem.parent for elem in concrete_part.elements]]
        if unmeshed_cells:
            issues.append("  Warning: %d unmeshed cells in concrete" % len(unmeshed_cells))
        
        # Check element count
        elem_count = len(concrete_part.elements)
        if elem_count == 0:
            issues.append("  Error: No elements in concrete mesh")
        else:
            print("  Concrete: %d elements" % elem_count)
    
    # Check rebar mesh
    if 'RebarMesh' in model.parts.keys():
        rebar_part = model.parts['RebarMesh']
        
        elem_count = len(rebar_part.elements)
        if elem_count == 0:
            issues.append("  Error: No elements in rebar mesh")
        else:
            print("  Rebar: %d elements" % elem_count)
    
    # Report issues
    if issues:
        print("\n  Issues found:")
        for issue in issues:
            print(issue)
        return False
    else:
        print("  Mesh quality check passed")
        return True


def create_mesh_for_layer_sets(assembly, config):
    """
    Create element sets from cell sets after meshing.
    This is needed for Model Change to work with elements.
    
    Args:
        assembly: Assembly object
        config: Config object
        
    Returns:
        dict: Dictionary mapping layer index to element set name
    """
    layer_elem_sets = {}
    layer_count = config.get_layer_count()
    
    beam_instance = assembly.instances['Beam-1']
    
    for i in range(layer_count):
        cell_set_name = 'LayerCells_%d' % (i + 1)
        elem_set_name = 'LayerElements_%d' % (i + 1)
        
        if cell_set_name in assembly.sets.keys():
            cell_set = assembly.sets[cell_set_name]
            
            # Get elements corresponding to these cells
            # This requires the mesh to exist
            if beam_instance.elements:
                # Map cells to elements
                cell_to_elems = {}
                for elem in beam_instance.elements:
                    parent_cell = elem.parent
                    if parent_cell not in cell_to_elems:
                        cell_to_elems[parent_cell] = []
                    cell_to_elems[parent_cell].append(elem)
                
                # Collect elements for this layer
                layer_elements = []
                for cell in cell_set.cells:
                    if cell in cell_to_elems:
                        layer_elements.extend(cell_to_elems[cell])
                
                # Create element set
                if layer_elements:
                    assembly.Set(
                        name=elem_set_name,
                        elements=tuple(layer_elements)
                    )
                    layer_elem_sets[i] = elem_set_name
    
    return layer_elem_sets
