# -*- coding: utf-8 -*-
"""
Mesh module for 3D printed concrete cube compression test
Python 2.7 compatible for Abaqus 2021
"""

from abaqus import *
from abaqusConstants import *

print("DEBUG: mesh.py loaded successfully")

def mesh_concrete_cube(part, config):
    """Mesh concrete cube with C3D8R elements"""
    print("Meshing concrete cube...")
    
    elem_type = mesh.ElemType(
        elemCode=C3D8R,
        elemLibrary=STANDARD,
        kinematicSplit=AVERAGE_STRAIN,
        hourglassControl=DEFAULT,
        distortionControl=DEFAULT
    )
    
    cells = part.cells
    part.setMeshControls(regions=cells, elemShape=HEX, technique=STRUCTURED)
    part.setElementType(regions=(cells,), elemTypes=(elem_type,))
    
    seed_size = config.layer_thickness / 2.0
    part.seedPart(size=seed_size, deviationFactor=0.1, minSizeFactor=0.1)
    part.generateMesh()
    
    print("  Elements: %d" % len(part.elements))


def mesh_support_plate(part, config):
    """Mesh support plate with C3D8R elements"""
    print("Meshing support plate: %s..." % part.name)
    
    elem_type = mesh.ElemType(elemCode=C3D8R, elemLibrary=STANDARD)
    cells = part.cells
    part.setMeshControls(regions=cells, elemShape=HEX, technique=STRUCTURED)
    part.setElementType(regions=(cells,), elemTypes=(elem_type,))
    
    part.seedPart(size=20.0, deviationFactor=0.1, minSizeFactor=0.1)
    part.generateMesh()
    
    print("  Elements: %d" % len(part.elements))


def create_cohesive_sections(model, config):
    """Create cohesive sections for interlayer bonding"""
    print("Creating cohesive sections...")
    
    sections = {}
    sections['cohesiveXY'] = model.CohesiveSection(
        name='cohesiveXY',
        material='ADHESIVE1',
        response=TRACTION_SEPARATION,
        initialThicknessType=SPECIFY,
        initialThickness=0.01,
        outOfPlaneThickness=None
    )
    
    sections['cohesiveXZ'] = model.CohesiveSection(
        name='cohesiveXZ',
        material='ADHESIVE5',
        response=TRACTION_SEPARATION,
        initialThicknessType=SPECIFY,
        initialThickness=0.01,
        outOfPlaneThickness=None
    )
    
    return sections


def create_solid_sections(model, config):
    """Create solid sections for concrete and steel"""
    print("Creating solid sections...")
    
    sections = {}
    sections['concrete'] = model.HomogeneousSolidSection(
        name='concreteSection',
        material=config.concrete_material_name
    )
    sections['steel'] = model.HomogeneousSolidSection(
        name='steelSection',
        material=config.steel_material_name
    )
    
    return sections


def assign_sections(model, config):
    """Assign sections to parts"""
    print("Assigning sections...")
    
    concrete_part = model.parts['concrete']
    plate_part = model.parts['zhizuo']
    
    concrete_region = (concrete_part.cells,)
    concrete_part.SectionAssignment(
        region=concrete_region,
        sectionName='concreteSection'
    )
    
    plate_region = (plate_part.cells,)
    plate_part.SectionAssignment(
        region=plate_region,
        sectionName='steelSection'
    )


def create_all_mesh_and_sections(model, config):
    """Complete meshing and section assignment"""
    print("DEBUG: create_all_mesh_and_sections called")
    print("\n" + "=" * 60)
    print("Meshing and Section Assignment")
    print("=" * 60)
    
    solid_sections = create_solid_sections(model, config)
    cohesive_sections = create_cohesive_sections(model, config)
    assign_sections(model, config)
    mesh_concrete_cube(model.parts['concrete'], config)
    mesh_support_plate(model.parts['zhizuo'], config)
    
    print("=" * 60)
    print("Meshing complete!")
    print("=" * 60)
