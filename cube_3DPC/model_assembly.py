# -*- coding: utf-8 -*-
"""
Assembly module for 3D printed concrete cube compression test
Creates assembly with instances, constraints, and rigid bodies
Python 2.7 compatible for Abaqus 2021
"""

from abaqus import *
from abaqusConstants import *


def create_assembly(model, config):
    """
    Create assembly with all instances
    
    Original .inp has:
    - concrete1: concrete cube
    - zhizuos1, zhizuos2: top and bottom plates
    - zhizuox1, zhizuox2: side plates
    
    Args:
        model: Abaqus model object
        config: Configuration object
        
    Returns:
        Assembly object
    """
    print("Creating assembly...")
    
    assembly = model.rootAssembly
    
    # 1. Concrete cube instance
    concrete_instance = assembly.Instance(
        name='concrete1',
        part=model.parts['concrete'],
        dependent=ON
    )
    print("  Instance created: concrete1")
    
    # 2. Support plate instances
    # Position them at top, bottom, and sides
    
    # Bottom plate (zhizuos2)
    plate_instance_s2 = assembly.Instance(
        name='zhizuos2',
        part=model.parts['zhizuo'],
        dependent=ON
    )
    # Translate to bottom
    assembly.translate(
        instanceList=('zhizuos2',),
        vector=(0.0, -10.0, 0.0)  # Below concrete
    )
    print("  Instance created: zhizuos2 (bottom)")
    
    # Top plate (zhizuos1)
    plate_instance_s1 = assembly.Instance(
        name='zhizuos1',
        part=model.parts['zhizuo'],
        dependent=ON
    )
    # Translate to top
    assembly.translate(
        instanceList=('zhizuos1',),
        vector=(0.0, config.cube_length_y, 0.0)  # Above concrete
    )
    print("  Instance created: zhizuos1 (top)")
    
    # Side plates (zhizuox1, zhizuox2) - for lateral constraint
    # These are optional depending on the test setup
    plate_instance_x1 = assembly.Instance(
        name='zhizuox1',
        part=model.parts['zhizuo'],
        dependent=ON
    )
    print("  Instance created: zhizuox1 (side)")
    
    plate_instance_x2 = assembly.Instance(
        name='zhizuox2',
        part=model.parts['zhizuo'],
        dependent=ON
    )
    print("  Instance created: zhizuox2 (side)")
    
    return assembly


def create_reference_points(model, assembly, config):
    """
    Create reference points for rigid body constraints
    
    Original .inp has 4 reference points:
    - Set-RP1: for zhizuos1
    - Set-RP2: for zhizuos2
    - Set-RP3: for zhizuox1
    - Set-RP4: for zhizuox2
    
    Args:
        model: Abaqus model object
        assembly: Assembly object
        config: Configuration object
        
    Returns:
        Dictionary of reference points
    """
    print("Creating reference points...")
    
    rps = {}
    
    # RP1: Top plate center
    rp1 = assembly.ReferencePoint(point=(
        config.cube_length_x / 2.0,
        config.cube_length_y + 20.0,  # Above top plate
        config.cube_length_z / 2.0
    ))
    rps['RP1'] = rp1
    assembly.Set(name='Set-RP1', referencePoints=(rp1,))
    print("  RP1 created (top plate)")
    
    # RP2: Bottom plate center
    rp2 = assembly.ReferencePoint(point=(
        config.cube_length_x / 2.0,
        -20.0,  # Below bottom plate
        config.cube_length_z / 2.0
    ))
    rps['RP2'] = rp2
    assembly.Set(name='Set-RP2', referencePoints=(rp2,))
    print("  RP2 created (bottom plate)")
    
    # RP3, RP4: Side plates
    rp3 = assembly.ReferencePoint(point=(
        -20.0,
        config.cube_length_y / 2.0,
        config.cube_length_z / 2.0
    ))
    rps['RP3'] = rp3
    assembly.Set(name='Set-RP3', referencePoints=(rp3,))
    print("  RP3 created (side plate 1)")
    
    rp4 = assembly.ReferencePoint(point=(
        config.cube_length_x + 20.0,
        config.cube_length_y / 2.0,
        config.cube_length_z / 2.0
    ))
    rps['RP4'] = rp4
    assembly.Set(name='Set-RP4', referencePoints=(rp4,))
    print("  RP4 created (side plate 2)")
    
    return rps


def create_tie_constraints(model, assembly, config):
    """
    Create tie constraints between concrete and plates
    
    Original .inp has 4 tie constraints:
    - Constraints1: concrete bottom to zhizuos2
    - Constraints2: concrete top to zhizuos1
    - Constraintx1, Constraintx2: side constraints
    
    Args:
        model: Abaqus model object
        assembly: Assembly object
        config: Configuration object
    """
    print("Creating tie constraints...")
    
    # Get instances
    concrete_inst = assembly.instances['concrete1']
    plate_s1 = assembly.instances['zhizuos1']
    plate_s2 = assembly.instances['zhizuos2']
    
    # Create surfaces for tie constraints
    # Bottom surface of concrete
    concrete_bottom_faces = concrete_inst.faces.getByBoundingBox(
        yMin=-0.1, yMax=0.1
    )
    assembly.Surface(
        name='SFconcretezb',
        side1Faces=concrete_bottom_faces
    )
    
    # Top surface of concrete
    concrete_top_faces = concrete_inst.faces.getByBoundingBox(
        yMin=config.cube_length_y - 0.1,
        yMax=config.cube_length_y + 0.1
    )
    assembly.Surface(
        name='SFconcretezu',
        side1Faces=concrete_top_faces
    )
    
    # Plate surfaces (simplified - should match actual geometry)
    plate_s1_faces = plate_s1.faces.getByBoundingBox(
        yMin=-0.1, yMax=0.1
    )
    assembly.Surface(
        name='SFzhizuos11',
        side1Faces=plate_s1_faces
    )
    
    plate_s2_faces = plate_s2.faces.getByBoundingBox(
        yMin=config.cube_length_y - 0.1,
        yMax=config.cube_length_y + 0.1
    )
    assembly.Surface(
        name='SFzhizuos22',
        side1Faces=plate_s2_faces
    )
    
    # Create tie constraints
    # Tie 1: Concrete bottom to bottom plate
    # TODO: Verify surface selection matches actual geometry
    if 'SFzhizuos22' not in assembly.surfaces or 'SFconcretezb' not in assembly.surfaces:
        raise NotImplementedError(
            "Tie constraint surfaces not properly defined. "
            "The current implementation uses bounding box selection which may not "
            "match the actual geometry in the .inp file. "
            "Please verify and implement proper surface selection."
        )
    
    model.Tie(
        name='Constraints1',
        master=assembly.surfaces['SFzhizuos22'],
        slave=assembly.surfaces['SFconcretezb'],
        adjust=ON,
        positionToleranceMethod=COMPUTED
    )
    print("  Tie constraint 1 created (bottom)")
    
    # Tie 2: Concrete top to top plate
    model.Tie(
        name='Constraints2',
        master=assembly.surfaces['SFzhizuos11'],
        slave=assembly.surfaces['SFconcretezu'],
        adjust=ON,
        positionToleranceMethod=COMPUTED
    )
    print("  Tie constraint 2 created (top)")


def create_rigid_body_constraints(model, assembly, config):
    """
    Create rigid body constraints for plates
    
    Original .inp uses Rigid Body constraint with:
    - ref node: Set-RP1, elset: zhizuos1.eset-zhizuo
    - etc.
    
    Args:
        model: Abaqus model object
        assembly: Assembly object
        config: Configuration object
    """
    print("Creating rigid body constraints...")
    
    # Get element sets for plates
    # Note: In the original, these are instance-level sets
    
    # Constraint for zhizuos1 (top plate)
    model.RigidBody(
        name='ConstraintRs1',
        refPointRegion=assembly.sets['Set-RP1'],
        bodyRegion=assembly.instances['zhizuos1'].sets.get('eset-zhizuo', None)
    )
    print("  Rigid body constraint 1 created (top plate)")
    
    # Constraint for zhizuos2 (bottom plate)
    model.RigidBody(
        name='ConstraintRs2',
        refPointRegion=assembly.sets['Set-RP2'],
        bodyRegion=assembly.instances['zhizuos2'].sets.get('eset-zhizuo', None)
    )
    print("  Rigid body constraint 2 created (bottom plate)")
    
    # Constraints for side plates
    model.RigidBody(
        name='ConstraintRx1',
        refPointRegion=assembly.sets['Set-RP3'],
        bodyRegion=assembly.instances['zhizuox1'].sets.get('eset-zhizuo', None)
    )
    print("  Rigid body constraint 3 created (side plate 1)")
    
    model.RigidBody(
        name='ConstraintRx2',
        refPointRegion=assembly.sets['Set-RP4'],
        bodyRegion=assembly.instances['zhizuox2'].sets.get('eset-zhizuo', None)
    )
    print("  Rigid body constraint 4 created (side plate 2)")


def create_complete_assembly(model, config):
    """
    Complete assembly creation with all constraints
    
    Args:
        model: Abaqus model object
        config: Configuration object
    """
    print("\n" + "=" * 60)
    print("Creating Assembly and Constraints")
    print("=" * 60)
    
    # 1. Create instances
    assembly = create_assembly(model, config)
    
    # 2. Create reference points
    rps = create_reference_points(model, assembly, config)
    
    # 3. Create tie constraints
    create_tie_constraints(model, assembly, config)
    
    # 4. Create rigid body constraints
    create_rigid_body_constraints(model, assembly, config)
    
    print("=" * 60)
    print("Assembly complete!")
    print("=" * 60)
    
    return assembly


if __name__ == "__main__":
    # Test assembly
    from config import config
    from geometry import create_all_parts
    from materials import create_all_materials
    from mesh import create_all_mesh_and_sections
    
    model = mdb.Model(name='TestAssembly')
    
    parts = create_all_parts(model, config)
    materials = create_all_materials(model, config)
    create_all_mesh_and_sections(model, config)
    assembly = create_complete_assembly(model, config)
    
    print("\nTest complete!")
