# -*- coding: utf-8 -*-
"""
Mechanical testing module for 3D printed concrete beam.
Setup bending and compression tests.
"""

from abaqus import *
from abaqusConstants import *


def setup_bending_test(model, assembly, config):
    """
    Setup three-point bending test.
    
    Args:
        model: Abaqus model object
        assembly: Assembly object
        config: Config object
        
    Returns:
        Dictionary of test components
    """
    results = {}
    
    # Get beam instance
    beam_instance = assembly.instances['Beam-1']
    
    # Create reference points for supports and load
    # Left support
    rp_left = assembly.ReferencePoint(point=(0.0, config.beam_width/2.0, 0.0))
    # Right support
    rp_right = assembly.ReferencePoint(
        point=(config.beam_length, config.beam_width/2.0, 0.0)
    )
    # Load point (center)
    rp_load = assembly.ReferencePoint(
        point=(config.beam_length/2.0, config.beam_width/2.0, config.beam_height)
    )
    
    results['supports'] = [rp_left, rp_right]
    results['load_point'] = rp_load
    
    # Create coupling constraints
    # (Simplified - in full implementation, create proper couplings)
    
    return results


def setup_compression_test(model, assembly, config):
    """
    Setup compression test.
    
    Args:
        model: Abaqus model object
        assembly: Assembly object
        config: Config object
        
    Returns:
        Dictionary of test components
    """
    results = {}
    
    # Get beam instance
    beam_instance = assembly.instances['Beam-1']
    
    # Create reference points for platens
    rp_bottom = assembly.ReferencePoint(
        point=(config.beam_length/2.0, config.beam_width/2.0, 0.0)
    )
    rp_top = assembly.ReferencePoint(
        point=(config.beam_length/2.0, config.beam_width/2.0, config.beam_height)
    )
    
    results['bottom_platen'] = rp_bottom
    results['top_platen'] = rp_top
    
    return results


def create_test_step(model, test_type, config):
    """
    Create analysis step for testing.
    
    Args:
        model: Abaqus model object
        test_type: 'bending' or 'compression'
        config: Config object
        
    Returns:
        Step object
    """
    step_name = '%sTest' % test_type.capitalize()
    
    step = model.StaticStep(
        name=step_name,
        previous='PrintLayer%d' % config.get_layer_count(),
        description='%s test' % test_type,
        timePeriod=1.0,
        nlgeom=ON,  # Enable for large deformation
        maxNumInc=1000,
        initialInc=0.01,
        minInc=1e-08,
        maxInc=0.1
    )
    
    return step
