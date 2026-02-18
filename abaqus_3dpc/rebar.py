# -*- coding: utf-8 -*-
"""
Rebar mesh creation for 3D printed concrete beam.
Creates top and bottom rebar layers.
"""

from abaqus import *
from abaqusConstants import *
import math


def create_rebar_layers(model, assembly, config):
    """
    Create top and bottom rebar layers in beam.
    
    Args:
        model: Abaqus model object
        assembly: Assembly object
        config: Config object
        
    Returns:
        Part object for rebar
    """
    # Create wire part for rebar
    rebar_part = model.Part(
        name='RebarMesh',
        dimensionality=THREE_D,
        type=DEFORMABLE_BODY
    )
    
    # Calculate rebar positions
    bottom_z = config.rebar_cover + config.rebar_diameter / 2.0
    top_z = config.beam_height - config.rebar_cover - config.rebar_diameter / 2.0
    
    # Create longitudinal rebars (along beam length)
    _create_longitudinal_rebars(
        rebar_part, config, bottom_z, 'Bottom'
    )
    _create_longitudinal_rebars(
        rebar_part, config, top_z, 'Top'
    )
    
    # Create transverse rebars (across beam width)
    _create_transverse_rebars(
        rebar_part, config, bottom_z, 'Bottom'
    )
    _create_transverse_rebars(
        rebar_part, config, top_z, 'Top'
    )
    
    # Create instance in assembly
    rebar_instance = assembly.Instance(
        name='Rebar-1',
        part=rebar_part,
        dependent=ON
    )
    
    return rebar_part


def _create_longitudinal_rebars(part, config, z_pos, layer_name):
    """
    Create longitudinal rebars at specified height.
    
    Args:
        part: Rebar part
        config: Config object
        z_pos: Z position for rebars
        layer_name: 'Top' or 'Bottom'
    """
    # Number of rebars across width
    num_rebars = int((config.beam_width - 2 * config.rebar_cover) 
                     / config.rebar_spacing) + 1
    
    for i in range(num_rebars):
        y_pos = config.rebar_cover + i * config.rebar_spacing
        if y_pos > config.beam_width - config.rebar_cover:
            break
        
        # Create wire for rebar
        sketch = part.ConstrainedSketch(
            name='__rebar_long_%s_%d__' % (layer_name, i),
            sheetSize=config.beam_length
        )
        
        sketch.Line(
            point1=(0.0, y_pos),
            point2=(config.beam_length, y_pos)
        )
        
        # Create wire feature
        part.Wire(sketch=sketch)


def _create_transverse_rebars(part, config, z_pos, layer_name):
    """
    Create transverse rebars at specified height.
    
    Args:
        part: Rebar part
        config: Config object
        z_pos: Z position for rebars
        layer_name: 'Top' or 'Bottom'
    """
    # Number of rebars along length
    num_rebars = int((config.beam_length - 2 * config.rebar_cover) 
                     / config.rebar_spacing) + 1
    
    for i in range(num_rebars):
        x_pos = config.rebar_cover + i * config.rebar_spacing
        if x_pos > config.beam_length - config.rebar_cover:
            break
        
        # Create wire for rebar
        sketch = part.ConstrainedSketch(
            name='__rebar_trans_%s_%d__' % (layer_name, i),
            sheetSize=config.beam_width
        )
        
        sketch.Line(
            point1=(x_pos, config.rebar_cover),
            point2=(x_pos, config.beam_width - config.rebar_cover)
        )
        
        # Create wire feature
        part.Wire(sketch=sketch)
