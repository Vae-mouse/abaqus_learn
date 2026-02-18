# -*- coding: utf-8 -*-
"""
Printing process simulation module.
Creates analysis steps for layer-by-layer printing.
"""

from abaqus import *
from abaqusConstants import *


def create_print_steps(model, config):
    """
    Create analysis steps for printing simulation.
    
    Args:
        model: Abaqus model object
        config: Config object
        
    Returns:
        List of step names
    """
    step_names = []
    layer_count = config.get_layer_count()
    
    # Initial step (gravity/self-weight)
    initial_step = model.steps['Initial']
    
    # Create step for each layer
    for i in range(layer_count):
        step_name = 'PrintLayer%d' % (i + 1)
        
        # Static step for layer activation
        step = model.StaticStep(
            name=step_name,
            previous='Initial' if i == 0 else step_names[-1],
            description='Print layer %d' % (i + 1),
            timePeriod=1.0,
            nlgeom=OFF,
            maxNumInc=100,
            initialInc=0.1,
            minInc=1e-05,
            maxInc=1.0
        )
        
        step_names.append(step_name)
    
    return step_names


def setup_gravity_load(model, config):
    """
    Setup gravity load for self-weight.
    
    Args:
        model: Abaqus model object
        config: Config object
    """
    # Get beam instance
    assembly = model.rootAssembly
    
    # Create gravity load in initial step
    gravity = model.Gravity(
        name='Gravity',
        createStepName='Initial',
        comp3=-9800.0  # mm/s^2
    )
    
    return gravity


def create_layer_sets(assembly, config):
    """
    Create sets for each printed layer.
    
    Args:
        assembly: Assembly object
        config: Config object
        
    Returns:
        Dictionary of layer sets
    """
    layer_sets = {}
    layer_count = config.get_layer_count()
    
    beam_instance = assembly.instances['Beam-1']
    
    for i in range(layer_count):
        z_min = i * config.layer_height
        z_max = (i + 1) * config.layer_height
        
        # Find cells in this layer
        cells = beam_instance.cells
        layer_cells = []
        
        for cell in cells:
            # Get cell centroid
            center = cell.getCentroid()
            if z_min <= center[2] < z_max:
                layer_cells.append(cell)
        
        # Create set for layer
        if layer_cells:
            set_name = 'Layer%d' % (i + 1)
            layer_set = assembly.Set(
                name=set_name,
                cells=tuple(layer_cells)
            )
            layer_sets[set_name] = layer_set
    
    return layer_sets
