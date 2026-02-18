# -*- coding: utf-8 -*-
"""
Geometry builder for 3D printed concrete beam.
Creates layered concrete beam with rebar mesh.
"""

from abaqus import *
from abaqusConstants import *


def create_concrete_beam(model, config):
    """
    Create concrete beam part with layer-based geometry.
    
    Args:
        model: Abaqus model object
        config: Config object with geometry parameters
        
    Returns:
        Part object
    """
    # Create sketch for beam cross-section
    sketch = model.ConstrainedSketch(
        name='__beam_profile__',
        sheetSize=config.beam_width * 2
    )
    
    # Draw rectangle (width x height)
    sketch.rectangle(
        point1=(0.0, 0.0),
        point2=(config.beam_width, config.beam_height)
    )
    
    # Create 3D part by extrusion
    part = model.Part(
        name='ConcreteBeam',
        dimensionality=THREE_D,
        type=DEFORMABLE_BODY
    )
    
    part.BaseSolidExtrude(
        sketch=sketch,
        depth=config.beam_length
    )
    
    return part


def partition_into_layers(part, config):
    """
    Partition beam into horizontal layers for printing simulation.
    
    Args:
        part: Concrete beam part
        config: Config object
    """
    layer_count = config.get_layer_count()
    
    # Create datum planes for partitioning
    for i in range(1, layer_count):
        z = i * config.layer_height
        
        # Create datum plane
        datum_plane = part.DatumPlaneByPrincipalPlane(
            principalPlane=XYPLANE,
            offset=z
        )
        
        # Partition cell using datum plane
        cells = part.cells
        part.PartitionCellByDatumPlane(
            datumPlane=part.datums[datum_plane.id],
            cells=cells
        )


def create_assembly(model, part, config):
    """
    Create assembly instance of concrete beam.
    
    Args:
        model: Abaqus model object
        part: Concrete beam part
        config: Config object
        
    Returns:
        Assembly instance
    """
    assembly = model.rootAssembly
    
    instance = assembly.Instance(
        name='Beam-1',
        part=part,
        dependent=ON
    )
    
    return instance
