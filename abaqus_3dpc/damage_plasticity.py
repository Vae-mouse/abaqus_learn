# -*- coding: utf-8 -*-
"""
Concrete Damaged Plasticity (CDP) model for 3D printed concrete.
Simulates concrete damage and crack propagation.
"""

try:
    from abaqus import *
    from abaqusConstants import *
    ABAQUS_AVAILABLE = True
except ImportError:
    ABAQUS_AVAILABLE = False
    # Mock constants for local testing
    ISOTROPIC = 'ISOTROPIC'
    UNITS_MM = 'UNITS_MM'
    UNITS_M = 'UNITS_M'
    UNITS_PA = 'UNITS_PA'
    UNITS_MPA = 'UNITS_MPA'
    STRAIN = 'STRAIN'
    STRESS = 'STRESS'
    NO_INDEPENDENT = 'NO_INDEPENDENT'
    LINEAR = 'LINEAR'
    CONSTANT = 'CONSTANT'
    MULTIPLY = 'MULTIPLY'
    TABULAR = 'TABULAR'
    POWER_LAW = 'POWER_LAW'
    BM = 'BM'
    FB = 'FB'


def add_cdp_properties(model, config):
    """
    Add Concrete Damaged Plasticity (CDP) properties to concrete material.
    
    Args:
        model: Abaqus model object
        config: Config object with material parameters
        
    Returns:
        Updated material object
    """
    if not ABAQUS_AVAILABLE:
        return None
        
    material = model.materials['Concrete']
    
    # Concrete Damaged Plasticity parameters
    # Format: (dilation_angle, eccentricity, fb0/fc0, K, viscosity)
    # dilation_angle: typically 30-40 degrees for concrete
    # eccentricity: typically 0.1 for concrete
    # fb0/fc0: ratio of biaxial to uniaxial compressive strength, typically 1.16
    # K: shape factor, typically 2/3
    # viscosity: small value for regularization, typically 0.0 or small
    
    material.ConcreteDamagedPlasticity(
        table=((38.0, 0.1, 1.16, 0.6667, 0.0001), )
    )
    
    # Compression hardening
    # Format: (yield_stress, inelastic_strain)
    # Typical C30 concrete stress-strain curve
    comp_stress = config.concrete_comp_strength
    material.ConcreteCompressionHardening(
        table=(
            (0.3 * comp_stress, 0.0),
            (0.5 * comp_stress, 0.0001),
            (0.7 * comp_stress, 0.0002),
            (0.9 * comp_stress, 0.0004),
            (1.0 * comp_stress, 0.0006),
            (0.9 * comp_stress, 0.0010),
            (0.7 * comp_stress, 0.0015),
            (0.5 * comp_stress, 0.0020),
        )
    )
    
    # Compression damage (stiffness degradation)
    # Format: (damage_variable, inelastic_strain)
    material.ConcreteCompressionDamage(
        table=(
            (0.0, 0.0),
            (0.0, 0.0001),
            (0.05, 0.0002),
            (0.1, 0.0004),
            (0.2, 0.0006),
            (0.35, 0.0010),
            (0.5, 0.0015),
            (0.7, 0.0020),
        ),
        type=ISOTROPIC
    )
    
    # Tension stiffening (post-cracking behavior)
    # Format: (yield_stress, displacement) or (yield_stress, fracture_energy)
    # Using fracture energy approach (Gf in N/m)
    # Typical Gf for C30: 50-100 N/m
    ft = 0.1 * comp_stress  # Tensile strength ~10% of compressive
    gf = 70.0  # Fracture energy N/m
    
    material.ConcreteTensionStiffening(
        table=(
            (ft, 0.0),
            (0.8 * ft, 0.0001),
            (0.5 * ft, 0.0003),
            (0.2 * ft, 0.0006),
            (0.05 * ft, 0.0010),
        ),
        type=DISPLACEMENT
    )
    
    # Tension damage
    # Format: (damage_variable, displacement)
    material.ConcreteTensionDamage(
        table=(
            (0.0, 0.0),
            (0.2, 0.0001),
            (0.5, 0.0003),
            (0.8, 0.0006),
            (0.95, 0.0010),
        ),
        type=ISOTROPIC
    )
    
    return material


def add_layer_dependent_cdp(model, config, layer_strength_factor=None):
    """
    Add CDP properties with layer-dependent strength (for inter-layer weakness).
    
    3D printed concrete may have weaker inter-layer bonds. This function
    creates material variations for different layer orientations.
    
    Args:
        model: Abaqus model object
        config: Config object
        layer_strength_factor: Factor for inter-layer strength reduction (0-1)
        
    Returns:
        Dictionary of created materials
    """
    if not ABAQUS_AVAILABLE:
        return {}
        
    if layer_strength_factor is None:
        layer_strength_factor = 0.8  # 20% reduction for inter-layer
    
    results = {}
    
    # Base concrete material (intra-layer)
    base_mat = add_cdp_properties(model, config)
    results['concrete_base'] = base_mat
    
    # Inter-layer material (weaker)
    inter_mat = model.Material(name='Concrete_InterLayer')
    
    # Copy basic properties
    inter_mat.Elastic(
        table=((config.concrete_E * layer_strength_factor, config.concrete_nu), )
    )
    inter_mat.Density(
        table=((config.concrete_rho, ), )
    )
    
    # Add CDP with reduced strength
    comp_stress = config.concrete_comp_strength * layer_strength_factor
    
    inter_mat.ConcreteDamagedPlasticity(
        table=((38.0, 0.1, 1.16, 0.6667, 0.0001), )
    )
    
    inter_mat.ConcreteCompressionHardening(
        table=(
            (0.3 * comp_stress, 0.0),
            (0.5 * comp_stress, 0.0001),
            (0.7 * comp_stress, 0.0002),
            (0.9 * comp_stress, 0.0004),
            (1.0 * comp_stress, 0.0006),
            (0.9 * comp_stress, 0.0010),
        )
    )
    
    inter_mat.ConcreteCompressionDamage(
        table=(
            (0.0, 0.0),
            (0.1, 0.0002),
            (0.25, 0.0006),
            (0.5, 0.0010),
        ),
        type=ISOTROPIC
    )
    
    ft = 0.1 * comp_stress
    inter_mat.ConcreteTensionStiffening(
        table=(
            (ft, 0.0),
            (0.5 * ft, 0.0003),
            (0.1 * ft, 0.0010),
        ),
        type=DISPLACEMENT
    )
    
    inter_mat.ConcreteTensionDamage(
        table=(
            (0.0, 0.0),
            (0.4, 0.0003),
            (0.9, 0.0010),
        ),
        type=ISOTROPIC
    )
    
    results['concrete_interlayer'] = inter_mat
    
    return results


def create_damage_field_output(model):
    """
    Create field output request for damage analysis.
    
    Args:
        model: Abaqus model object
        
    Returns:
        Field output request object
    """
    if not ABAQUS_AVAILABLE:
        return None
        
    # Update existing field output or create new one
    if 'F-Output-1' in model.fieldOutputRequests.keys():
        model.fieldOutputRequests['F-Output-1'].setValues(
            variables=(
                'S', 'E', 'U', 'PE', 'PEEQ', 'PEEQMAX',
                'DAMAGEC', 'DAMAGET', 'SDEG', 'STATUS'
            )
        )
    else:
        model.FieldOutputRequest(
            name='F-Output-Damage',
            createStepName='ApplyLoad',
            variables=(
                'S', 'E', 'U', 'PE', 'PEEQ', 'PEEQMAX',
                'DAMAGEC', 'DAMAGET', 'SDEG', 'STATUS'
            )
        )
    
    return model.fieldOutputRequests['F-Output-1']


def create_damage_history_output(model, region, step_name='ApplyLoad'):
    """
    Create history output for damage monitoring at specific region.
    
    Args:
        model: Abaqus model object
        region: Region to monitor (Set object)
        step_name: Step name for output
        
    Returns:
        History output request object
    """
    if not ABAQUS_AVAILABLE:
        return None
        
    history = model.HistoryOutputRequest(
        name='H-Output-Damage',
        createStepName=step_name,
        variables=('DAMAGEC', 'DAMAGET', 'SDEG'),
        region=region,
        sectionPoints=DEFAULT,
        rebar=EXCLUDE
    )
    
    return history


def setup_cdp_analysis(model, assembly, config, 
                       include_interlayer_weakness=False):
    """
    Setup complete CDP analysis for 3D printed concrete.
    
    Args:
        model: Abaqus model object
        assembly: Assembly object
        config: Config object
        include_interlayer_weakness: Whether to model inter-layer weakness
        
    Returns:
        Dictionary containing created objects
    """
    if not ABAQUS_AVAILABLE:
        return {}
        
    results = {}
    
    # Add CDP properties
    if include_interlayer_weakness:
        materials = add_layer_dependent_cdp(model, config)
        results['materials'] = materials
    else:
        material = add_cdp_properties(model, config)
        results['material'] = material
    
    # Setup field output for damage
    field_output = create_damage_field_output(model)
    results['field_output'] = field_output
    
    return results
