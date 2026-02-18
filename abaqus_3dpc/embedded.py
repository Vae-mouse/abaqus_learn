# -*- coding: utf-8 -*-
"""
Embedded element constraints for rebar-concrete interaction.
Links rebar mesh to concrete host elements.
"""

from abaqus import *
from abaqusConstants import *


def create_embedded_constraint(model, assembly, config):
    """
    Create embedded element constraint between rebar and concrete.
    
    This function establishes the embedded element relationship where
    rebar nodes are constrained to the concrete host elements.
    
    Args:
        model: Abaqus model object
        assembly: Assembly object
        config: Config object
        
    Returns:
        EmbeddedConstraint object
    """
    # Get instances
    concrete_instance = assembly.instances['Beam-1']
    rebar_instance = assembly.instances['Rebar-1']
    
    # Define host region (concrete beam)
    # Use all cells of the concrete beam
    host_region = concrete_instance.cells
    
    # Define embedded region (rebar)
    # Use all edges (wires) of the rebar part
    embedded_region = rebar_instance.edges
    
    # Create embedded element constraint
    # This constrains rebar nodes to concrete elements
    embedded_constraint = model.EmbeddedElement(
        name='RebarEmbedded',
        hostRegion=host_region,
        embeddedRegion=embedded_region,
        weightFactorTolerance=1e-06,
        absoluteTolerance=0.0,
        fractionalTolerance=0.5
    )
    
    return embedded_constraint


def create_embedded_constraint_by_set(model, assembly, config):
    """
    Create embedded element constraint using sets.
    
    Alternative implementation using pre-defined sets for more control.
    
    Args:
        model: Abaqus model object
        assembly: Assembly object
        config: Config object
        
    Returns:
        EmbeddedConstraint object
    """
    # Get instances
    concrete_instance = assembly.instances['Beam-1']
    rebar_instance = assembly.instances['Rebar-1']
    
    # Create set for concrete host region (all cells)
    host_cells = concrete_instance.cells
    host_set = assembly.Set(
        name='ConcreteHostRegion',
        cells=host_cells,
        instance=concrete_instance
    )
    
    # Create set for rebar embedded region (all edges)
    rebar_edges = rebar_instance.edges
    rebar_set = assembly.Set(
        name='RebarEmbeddedRegion',
        edges=rebar_edges,
        instance=rebar_instance
    )
    
    # Create embedded element constraint
    embedded_constraint = model.EmbeddedElement(
        name='RebarEmbedded',
        hostRegion=host_set,
        embeddedRegion=rebar_set,
        weightFactorTolerance=1e-06,
        absoluteTolerance=0.0,
        fractionalTolerance=0.5
    )
    
    return embedded_constraint


def verify_embedded_constraint(model, assembly):
    """
    Verify embedded element constraint is properly defined.
    
    Args:
        model: Abaqus model object
        assembly: Assembly object
        
    Returns:
        bool: True if constraint is valid
    """
    try:
        # Check if constraint exists
        if 'RebarEmbedded' not in model.constraints.keys():
            print("Warning: Embedded constraint 'RebarEmbedded' not found")
            return False
        
        constraint = model.constraints['RebarEmbedded']
        
        # Verify host region exists
        if constraint.hostRegion is None:
            print("Warning: Host region is None")
            return False
        
        # Verify embedded region exists
        if constraint.embeddedRegion is None:
            print("Warning: Embedded region is None")
            return False
        
        print("Embedded element constraint verified successfully")
        return True
        
    except Exception as e:
        print("Error verifying embedded constraint: %s" % str(e))
        return False


def assign_truss_section_to_rebar(model, rebar_part, config):
    """
    Assign truss section to rebar part.
    
    Args:
        model: Abaqus model object
        rebar_part: Rebar part object
        config: Config object
        
    Returns:
        SectionAssignment object
    """
    # Get all edges (wires) in rebar part
    edges = rebar_part.edges
    
    # Create region from all edges
    region = regionToolset.Region(edges=edges)
    
    # Assign truss section
    section_assignment = rebar_part.SectionAssignment(
        region=region,
        sectionName='SteelSection'
    )
    
    # Set element type to truss (T3D2)
    elem_type = mesh.ElemType(
        elemCode=T3D2,
        elemLibrary=STANDARD
    )
    
    # Get all edges for mesh assignment
    all_edges = rebar_part.edges
    edge_region = regionToolset.Region(edges=all_edges)
    
    # Assign element type
    rebar_part.setElementType(
        regions=edge_region,
        elemTypes=(elem_type,)
    )
    
    return section_assignment
