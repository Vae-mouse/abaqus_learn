# -*- coding: utf-8 -*-
"""
Geometry module for 3D printed concrete cube compression test
Creates concrete cube and support plates
Python 2.7 compatible for Abaqus 2021
"""

from abaqus import *
from abaqusConstants import *


def create_concrete_cube(model, config):
    """
    Create concrete cube part with layered structure
    
    The original .inp uses NGEN/NFILL to generate nodes.
    Here we create a solid part and partition it into layers.
    
    Args:
        model: Abaqus model object
        config: CubeCompressionConfig object
        
    Returns:
        Part object for concrete cube
    """
    print("Creating concrete cube part...")
    
    # Create sketch for base (X-Z plane)
    sketch = model.ConstrainedSketch(
        name='__cube_base__',
        sheetSize=config.cube_length_x * 1.5
    )
    
    # Draw rectangle (X x Z)
    sketch.rectangle(
        point1=(0.0, 0.0),
        point2=(config.cube_length_x, config.cube_length_z)
    )
    
    # Create 3D part by extrusion in Y direction
    cube = model.Part(
        name='concrete',
        dimensionality=THREE_D,
        type=DEFORMABLE_BODY
    )
    
    cube.BaseSolidExtrude(
        sketch=sketch,
        depth=config.cube_length_y
    )
    
    print("  Base cube created: %.1f x %.1f x %.1f mm" % (
        config.cube_length_x, config.cube_length_y, config.cube_length_z))
    
    # Partition into layers for cohesive insertion
    partition_into_layers(cube, config)
    
    return cube


def partition_into_layers(part, config):
    """
    Partition cube into layers for cohesive element insertion
    
    Creates datum planes at each layer interface and uses them
    to partition the part into separate cells.
    
    Args:
        part: Concrete cube part
        config: Configuration object
    """
    print("Partitioning into %d layers..." % config.num_layers)
    
    # Get the part's datum plane (YZ plane at X=0)
    datum_plane_yz = part.datums[part.features['Solid extrude 1'].id]
    
    # Create datum planes at each layer interface
    for i in range(1, config.num_layers):
        y_offset = i * config.layer_thickness
        
        # Create datum plane parallel to XZ at Y = y_offset
        datum_id = part.DatumPlaneByPrincipalPlane(
            principalPlane=XZPLANE,
            offset=y_offset
        ).id
        
        # Use the datum plane to partition the cell
        datum = part.datums[datum_id]
        
        # Get all cells
        cells = part.cells
        
        # Partition cells using datum plane
        part.PartitionCellByDatumPlane(
            datumPlane=datum,
            cells=cells
        )
        
        print("  Created partition at Y = %.1f mm" % y_offset)
    
    print("  Partitioning complete: %d cells created" % len(part.cells))
    
    # TODO: Cohesive element insertion is not yet implemented
    # The original .inp uses COH3D8 elements between layers
    # This requires:
    # 1. Creating cohesive layers at each interface
    # 2. Meshing with compatible nodes
    # 3. Assigning cohesive sections
    raise NotImplementedError(
        "Cohesive element insertion is not implemented. "
        "The current implementation only partitions the geometry. "
        "To fully replicate the .inp file, cohesive layers need to be "
        "inserted between concrete layers using COH3D8 elements."
    )


def create_support_plate(model, config, name='zhizuo'):
    """
    Create support plate part (for loading and constraints)
    
    The original .inp has 4 plates:
    - zhizuos1: top plate (compression loading)
    - zhizuos2: bottom plate (fixed support)
    - zhizuox1, zhizuox2: side plates (lateral constraint)
    
    Args:
        model: Abaqus model object
        config: Configuration object
        name: Part name
        
    Returns:
        Part object for support plate
    """
    print("Creating support plate part: %s..." % name)
    
    # Plate dimensions (estimated from .inp node coordinates)
    # These should be adjusted based on actual geometry in the paper
    plate_length = config.cube_length_x  # 360 mm
    plate_width = config.cube_length_z   # 60 mm
    plate_thickness = 10.0               # mm (estimated)
    
    # Create sketch
    sketch = model.ConstrainedSketch(
        name='__plate_profile__',
        sheetSize=plate_length * 1.5
    )
    
    sketch.rectangle(
        point1=(0.0, 0.0),
        point2=(plate_length, plate_width)
    )
    
    # Create part
    plate = model.Part(
        name=name,
        dimensionality=THREE_D,
        type=DEFORMABLE_BODY
    )
    
    plate.BaseSolidExtrude(
        sketch=sketch,
        depth=plate_thickness
    )
    
    print("  Plate created: %.1f x %.1f x %.1f mm" % (
        plate_length, plate_width, plate_thickness))
    
    return plate


def create_all_parts(model, config):
    """
    Create all parts for the model
    
    Args:
        model: Abaqus model object
        config: Configuration object
        
    Returns:
        Dictionary of created parts
    """
    print("\n" + "=" * 60)
    print("Creating Geometry Parts")
    print("=" * 60)
    
    parts = {}
    
    # 1. Create concrete cube
    parts['concrete'] = create_concrete_cube(model, config)
    
    # 2. Create support plates
    # In the original .inp, all plates use the same part 'zhizuo'
    # but are instantiated with different positions
    parts['zhizuo'] = create_support_plate(model, config, 'zhizuo')
    
    print("=" * 60)
    print("All parts created successfully!")
    print("=" * 60)
    
    return parts


if __name__ == "__main__":
    # Test geometry creation
    from config import config
    
    model = mdb.Model(name='TestGeometry')
    parts = create_all_parts(model, config)
    
    print("\nTest complete!")
    print("Parts created: %s" % list(parts.keys()))
