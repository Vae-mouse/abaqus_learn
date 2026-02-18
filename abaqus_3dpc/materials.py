# -*- coding: utf-8 -*-
"""
Material factory for 3D printed concrete model.
Creates concrete and steel materials with proper properties.
"""

from abaqus import *
from abaqusConstants import *


def create_concrete_material(model, config):
    """
    Create concrete material with elastic properties.
    
    Args:
        model: Abaqus model object
        config: Config object with material parameters
        
    Returns:
        Material object
    """
    material = model.Material(name='Concrete')
    
    # Elastic properties
    material.Elastic(
        table=((config.concrete_E, config.concrete_nu), )
    )
    
    # Density
    material.Density(
        table=((config.concrete_rho, ), )
    )
    
    # Concrete damaged plasticity (simplified)
    # For full implementation, add CDP parameters
    
    return material


def create_steel_material(model, config):
    """
    Create steel rebar material with elastic-plastic properties.
    
    Args:
        model: Abaqus model object
        config: Config object with material parameters
        
    Returns:
        Material object
    """
    material = model.Material(name='Steel')
    
    # Elastic properties
    material.Elastic(
        table=((config.steel_E, config.steel_nu), )
    )
    
    # Density
    material.Density(
        table=((config.steel_rho, ), )
    )
    
    # Plastic properties (bilinear)
    material.Plastic(
        table=((config.steel_yield, 0.0), 
               (config.steel_yield * 1.1, 0.02))
    )
    
    return material


def create_concrete_section(model, config):
    """
    Create homogeneous solid section for concrete.
    
    Args:
        model: Abaqus model object
        config: Config object
        
    Returns:
        Section object
    """
    section = model.HomogeneousSolidSection(
        name='ConcreteSection',
        material='Concrete'
    )
    return section


def create_steel_section(model, config):
    """
    Create truss section for steel rebar.
    
    Args:
        model: Abaqus model object
        config: Config object
        
    Returns:
        Section object
    """
    import math
    area = math.pi * (config.rebar_diameter / 2.0) ** 2
    
    section = model.TrussSection(
        name='SteelSection',
        material='Steel',
        area=area
    )
    return section
