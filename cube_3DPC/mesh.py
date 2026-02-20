# -*- coding: utf-8 -*-
"""
Mesh module for 3D printed concrete cube compression test
Creates structured mesh with cohesive elements between layers
Python 2.7 compatible for Abaqus 2021
"""

from abaqus import *
from abaqusConstants import *


def mesh_concrete_cube(part, config):
    """
    Mesh concrete cube with C3D8R elements
    
    Note: The original .inp uses NGEN/NFILL to manually generate nodes.
    Here we use Abaqus seeding and meshing for structured grid.
    
    Args:
        part: Concrete cube part
        config: Configuration object
    """
    print("Meshing concrete cube...")
    
    # Set mesh controls
    # C3D8R: 8-node brick, reduced integration (standard for structural)
    elem_type = mesh.ElemType(
        elemCode=C3D8R,
        elemLibrary=STANDARD,
        kinematicSplit=AVERAGE_STRAIN,
        hourglassControl=DEFAULT,
        distortionControl=DEFAULT
    )
    
    # Apply to all cells
    cells = part.cells
    part.setMeshControls(regions=cells, elemShape=HEX, technique=STRUCTURED)
    part.setElementType(regions=(cells,), elemTypes=(elem_type,))
    
    # Seed edges
    # Use global seed size based on layer thickness
    seed_size = config.layer_thickness / 2.0  # 2 elements per layer
    
    part.seedPart(size=seed_size, deviationFactor=0.1, minSizeFactor=0.1)
    
    # Generate mesh
    part.generateMesh()
    
    # Report
    num_elems = len(part.elements)
    num_nodes = len(part.nodes)
    
    print("  Mesh generated:")
    print("    Elements: %d" % num_elems)
    print("    Nodes: %d" % num_nodes)
    print("    Element type: C3D8R")
    print("    Seed size: %.2f mm" % seed_size)


def mesh_support_plate(part, config):
    """
    Mesh support plate with C3D8R elements
    
    Args:
        part: Support plate part
        config: Configuration object
    """
    print("Meshing support plate: %s..." % part.name)
    
    elem_type = mesh.ElemType(
        elemCode=C3D8R,
        elemLibrary=STANDARD
    )
    
    cells = part.cells
    part.setMeshControls(regions=cells, elemShape=HEX, technique=STRUCTURED)
    part.setElementType(regions=(cells,), elemTypes=(elem_type,))
    
    # Coarser mesh for plates (rigid bodies)
    seed_size = 20.0  # mm
    part.seedPart(size=seed_size, deviationFactor=0.1, minSizeFactor=0.1)
    
    part.generateMesh()
    
    print("  Mesh generated: %d elements" % len(part.elements))


def create_cohesive_sections(model, config):
    """
    Create cohesive sections for interlayer bonding
    
    Note: In Abaqus CAE, cohesive elements are typically inserted
    using the "Insert cohesive elements" feature or by creating
    separate cohesive layers. This function creates the sections
    that will be assigned to cohesive layers.
    
    Args:
        model: Abaqus model object
        config: Configuration object
    """
    print("Creating cohesive sections...")
    
    sections = {}
    
    # Create section for XY cohesive (between layers in Y direction)
    sections['cohesiveXY'] = model.CohesiveSection(
        name='cohesiveXY',
        material='ADHESIVE1',  # Use first adhesive
        response=TRACTION_SEPARATION,
        initialThicknessType=SPECIFY,
        initialThickness=0.01,  # Small initial thickness
        outOfPlaneThickness=None
    )
    print("  Cohesive section XY created (ADHESIVE1)")
    
    # Create section for XZ cohesive
    sections['cohesiveXZ'] = model.CohesiveSection(
        name='cohesiveXZ',
        material='ADHESIVE5',  # Use fifth adhesive
        response=TRACTION_SEPARATION,
        initialThicknessType=SPECIFY,
        initialThickness=0.01,
        outOfPlaneThickness=None
    )
    print("  Cohesive section XZ created (ADHESIVE5)")
    
    return sections


def create_solid_sections(model, config):
    """
    Create solid sections for concrete and steel
    
    Args:
        model: Abaqus model object
        config: Configuration object
        
    Returns:
        Dictionary of sections
    """
    print("Creating solid sections...")
    
    sections = {}
    
    # Concrete section
    sections['concrete'] = model.HomogeneousSolidSection(
        name='concreteSection',
        material=config.concrete_material_name
    )
    print("  Concrete section created")
    
    # Steel section
    sections['steel'] = model.HomogeneousSolidSection(
        name='steelSection',
        material=config.steel_material_name
    )
    print("  Steel section created")
    
    return sections


def assign_sections(model, config):
    """
    Assign sections to parts
    
    Args:
        model: Abaqus model object
        config: Configuration object
    """
    print("Assigning sections...")
    
    # Get parts
    concrete_part = model.parts['concrete']
    plate_part = model.parts['zhizuo']
    
    # Assign concrete section
    concrete_region = (concrete_part.cells,)
    concrete_part.SectionAssignment(
        region=concrete_region,
        sectionName='concreteSection'
    )
    print("  Concrete section assigned")
    
    # Assign steel section to plate
    plate_region = (plate_part.cells,)
    plate_part.SectionAssignment(
        region=plate_region,
        sectionName='steelSection'
    )
    print("  Steel section assigned")


def create_all_mesh_and_sections(model, config):
    """
    Complete meshing and section assignment
    
    Args:
        model: Abaqus model object
        config: Configuration object
    """
    print("\n" + "=" * 60)
    print("Meshing and Section Assignment")
    print("=" * 60)
    
    # 1. Create sections
    solid_sections = create_solid_sections(model, config)
    cohesive_sections = create_cohesive_sections(model, config)
    
    # 2. Assign sections
    assign_sections(model, config)
    
    # 3. Mesh parts
    mesh_concrete_cube(model.parts['concrete'], config)
    mesh_support_plate(model.parts['zhizuo'], config)
    
    print("=" * 60)
    print("Meshing complete!")
    print("=" * 60)


if __name__ == "__main__":
    # Test meshing
    from config import config
    from geometry import create_all_parts
    from materials import create_all_materials
    
    model = mdb.Model(name='TestMesh')
    
    # Create parts
    parts = create_all_parts(model, config)
    
    # Create materials
    materials = create_all_materials(model, config)
    
    # Mesh and assign sections
    create_all_mesh_and_sections(model, config)
    
    print("\nTest complete!")
