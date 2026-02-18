# -*- coding: utf-8 -*-
"""
Inter-layer cohesive contact for 3D printed concrete.
Models bonding behavior between printed layers.
"""

from abaqus import *
from abaqusConstants import *


def create_layer_cohesive_interaction(model, assembly, config):
    """
    Create cohesive contact between printed layers.
    
    Args:
        model: Abaqus model object
        assembly: Assembly object
        config: Config object with cohesive parameters
        
    Returns:
        Dictionary of created interactions
    """
    results = {}
    
    # Cohesive material properties
    # Typical values for 3D printed concrete interface
    cohesive_E = config.concrete_E * 0.5  # Interface stiffness ~50% of bulk
    cohesive_G = cohesive_E / (2 * (1 + 0.2))  # Shear modulus
    
    # Create cohesive material
    cohesive_mat = model.Material(name='LayerInterface')
    
    # Traction-separation behavior
    # Mode I (tensile) and Mode II/III (shear) properties
    cohesive_mat.TractionSeparation(
        table=((cohesive_E, cohesive_G, cohesive_G), )
    )
    
    # Damage evolution
    # Quadratic damage initiation criterion
    cohesive_mat.QuadsDamageInitiation(
        table=((config.concrete_FT, config.concrete_FT, config.concrete_FT), )
    )
    
    # Linear damage evolution
    cohesive_mat.damageEvolution.DamageEvolution(
        type=ENERGY,
        table=((0.1, 0.1, 0.1), )  # Fracture energy (N/mm)
    )
    
    # Create cohesive section
    cohesive_section = model.CohesiveSection(
        name='CohesiveSection',
        material='LayerInterface',
        response=TRACTION_SEPARATION,
        initialThicknessType=SPECIFY,
        initialThickness=0.1  # Interface thickness (mm)
    )
    
    results['material'] = cohesive_mat
    results['section'] = cohesive_section
    
    return results


def create_layer_contact_pairs(model, assembly, config):
    """
    Create contact pairs between adjacent layers.
    
    Args:
        model: Abaqus model object
        assembly: Assembly object
        config: Config object
        
    Returns:
        List of contact interaction names
    """
    interactions = []
    layer_count = config.get_layer_count()
    
    beam_instance = assembly.instances['Beam-1']
    
    # Create contact interaction for each interface
    for i in range(layer_count - 1):
        # Get bottom face of upper layer
        upper_layer_z = (i + 1) * config.layer_height
        
        # Find faces at this interface
        # Bottom face of layer i+1
        bottom_faces = []
        for face in beam_instance.faces:
            center = face.getCentroid()
            if abs(center[2] - upper_layer_z) < 0.01:
                bottom_faces.append(face)
        
        if bottom_faces:
            # Create surface for bottom faces
            bottom_surface_name = 'Layer%d_Bottom' % (i + 2)
            assembly.Surface(
                name=bottom_surface_name,
                side1Faces=tuple(bottom_faces)
            )
            
            # Create contact interaction
            interaction_name = 'LayerInterface_%d_%d' % (i + 1, i + 2)
            
            # Use surface-to-surface contact with cohesive behavior
            interaction = model.SurfaceToSurfaceContactStd(
                name=interaction_name,
                createStepName='Initial',
                master=assembly.surfaces[bottom_surface_name],
                slave=assembly.surfaces.get('Layer%d_Top' % (i + 1), None),
                sliding=SMALL,
                interactionProperty='CohesiveBehavior'
            )
            
            interactions.append(interaction_name)
    
    return interactions


def create_cohesive_contact_property(model):
    """
    Create contact property with cohesive behavior.
    
    Args:
        model: Abaqus model object
        
    Returns:
        Contact property name
    """
    prop_name = 'CohesiveBehavior'
    
    contact_prop = model.ContactProperty(prop_name)
    
    # Add cohesive behavior
    contact_prop.CohesiveBehavior(
        defaultPenalties=OFF,
        table=((1000.0, 500.0, 500.0), )  # Knn, Kss, Ktt (N/mm3)
    )
    
    # Add damage
    contact_prop.Damage(
        initTable=((5.0, 5.0, 5.0), ),  # Tensile and shear strengths (MPa)
        evolutionType=ENERGY,
        evolutionTable=((0.1, 0.1, 0.1), )  # Fracture energies (N/mm)
    )
    
    return prop_name
