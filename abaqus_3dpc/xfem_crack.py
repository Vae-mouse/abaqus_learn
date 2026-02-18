# -*- coding: utf-8 -*-
"""
XFEM (Extended Finite Element Method) for crack propagation in 3D printed concrete.
Simulates discrete crack growth without remeshing.
"""

try:
    from abaqus import *
    from abaqusConstants import *
    ABAQUS_AVAILABLE = True
except ImportError:
    ABAQUS_AVAILABLE = False
    # Mock constants
    SIGNED_DISTANCE = 'SIGNED_DISTANCE'
    UNIFORM = 'UNIFORM'
    PROPAGATION_ALLOWED = 'PROPAGATION_ALLOWED'
    PROPAGATION_DISABLED = 'PROPAGATION_DISABLED'
    ENRICHMENT_DOFS = 'ENRICHMENT_DOFS'


def create_xfem_crack(model, name, crack_domain, initial_crack=None):
    """
    Create XFEM crack definition.
    
    Args:
        model: Abaqus model object
        name: Name of the crack
        crack_domain: Region where crack can propagate (Set or Surface)
        initial_crack: Initial crack surface (optional)
        
    Returns:
        Crack object
    """
    if not ABAQUS_AVAILABLE:
        return None
        
    crack = model.CrackFromDeformation(
        name=name,
        crackDomain=crack_domain,
        crackLocation=initial_crack if initial_crack else crack_domain
    )
    
    return crack


def create_xfem_enrichment(model, name, region, enrichment_type='PROPAGATION'):
    """
    Create XFEM enrichment for crack propagation.
    
    Args:
        model: Abaqus model object
        name: Name of the enrichment
        region: Region to apply enrichment
        enrichment_type: 'PROPAGATION' or 'STATIONARY'
        
    Returns:
        Enrichment object
    """
    if not ABAQUS_AVAILABLE:
        return None
        
    if enrichment_type == 'PROPAGATION':
        enrichment = model.EnrichmentDefinition(
            name=name,
            enrichmentElements=PROPAGATION_ALLOWED,
            enrichmentRegion=region,
            enrichmentDOFs=ENRICHMENT_DOFS
        )
    else:
        enrichment = model.EnrichmentDefinition(
            name=name,
            enrichmentElements=PROPAGATION_DISABLED,
            enrichmentRegion=region,
            enrichmentDOFs=ENRICHMENT_DOFS
        )
    
    return enrichment


def create_fracture_criterion(model, name, criterion_type='MAXPS'):
    """
    Create fracture criterion for XFEM crack propagation.
    
    Args:
        model: Abaqus model object
        name: Name of the fracture criterion
        criterion_type: 'MAXPS' (Max Principal Stress), 'MAXPE' (Max Principal Strain),
                       'QUAD' (Quadratic), 'PUCK' (Puck)
        
    Returns:
        Fracture criterion object
    """
    if not ABAQUS_AVAILABLE:
        return None
        
    if criterion_type == 'MAXPS':
        criterion = model.MaxpsDamageInitiation(name=name)
    elif criterion_type == 'MAXPE':
        criterion = model.MaxpeDamageInitiation(name=name)
    elif criterion_type == 'QUAD':
        criterion = model.QuadeDamageInitiation(name=name)
    elif criterion_type == 'PUCK':
        criterion = model.PuckDamageInitiation(name=name)
    else:
        criterion = model.MaxpsDamageInitiation(name=name)
    
    return criterion


def create_damage_evolution(model, criterion, type='ENERGY', value=100.0):
    """
    Create damage evolution law for fracture.
    
    Args:
        model: Abaqus model object
        criterion: Fracture criterion object
        type: 'ENERGY' (fracture energy) or 'DISPLACEMENT'
        value: Fracture energy (N/m) or displacement (mm)
        
    Returns:
        Damage evolution object
    """
    if not ABAQUS_AVAILABLE:
        return None
        
    if type == 'ENERGY':
        evolution = criterion.DamageEvolution(
            type=ENERGY,
            table=((value, ), ),
            mixedModeBehavior=MODE_INDEPENDENT,
            modeMixRatio=ENERGY
        )
    else:
        evolution = criterion.DamageEvolution(
            type=DISPLACEMENT,
            table=((value, ), ),
            mixedModeBehavior=MODE_INDEPENDENT,
            modeMixRatio=ENERGY
        )
    
    return evolution


def create_cohesive_section_for_xfem(model, name, material, thickness=None):
    """
    Create cohesive section for XFEM crack behavior.
    
    Args:
        model: Abaqus model object
        name: Name of the section
        material: Material name or object
        thickness: Section thickness (optional)
        
    Returns:
        Cohesive section object
    """
    if not ABAQUS_AVAILABLE:
        return None
        
    if thickness:
        section = model.CohesiveSection(
            name=name,
            material=material,
            response=TRACTION_SEPARATION,
            initialThicknessType=SPECIFY,
            initialThickness=thickness,
            outOfPlaneThickness=thickness
        )
    else:
        section = model.CohesiveSection(
            name=name,
            material=material,
            response=TRACTION_SEPARATION,
            initialThicknessType=GEOMETRY
        )
    
    return section


def setup_xfem_analysis(model, assembly, config, 
                        crack_regions=None,
                        criterion_type='MAXPS',
                        fracture_energy=100.0):
    """
    Setup complete XFEM analysis for crack propagation.
    
    Args:
        model: Abaqus model object
        assembly: Assembly object
        config: Config object
        crack_regions: List of regions where cracks can initiate
        criterion_type: Fracture criterion type
        fracture_energy: Fracture energy in N/m
        
    Returns:
        Dictionary containing created objects
    """
    if not ABAQUS_AVAILABLE:
        return {}
        
    results = {}
    
    # Create fracture criterion
    criterion = create_fracture_criterion(model, 'ConcreteFracture', criterion_type)
    results['criterion'] = criterion
    
    # Create damage evolution
    evolution = create_damage_evolution(model, criterion, 'ENERGY', fracture_energy)
    results['evolution'] = evolution
    
    # Create XFEM enrichments for specified regions
    if crack_regions:
        enrichments = []
        for i, region in enumerate(crack_regions):
            enrichment = create_xfem_enrichment(
                model, 'XFEM_Crack_{}'.format(i+1), region, 'PROPAGATION'
            )
            enrichments.append(enrichment)
        results['enrichments'] = enrichments
    
    # Setup field output for XFEM
    if 'F-Output-1' in model.fieldOutputRequests.keys():
        model.fieldOutputRequests['F-Output-1'].setValues(
            variables=(
                'S', 'E', 'U', 'PHILSM', 'PSILSM', 'STATUSXFEM'
            )
        )
    else:
        model.FieldOutputRequest(
            name='F-Output-XFEM',
            createStepName='ApplyLoad',
            variables=(
                'S', 'E', 'U', 'PHILSM', 'PSILSM', 'STATUSXFEM'
            )
        )
    
    return results


def create_interlayer_crack_region(model, assembly, layer_interfaces):
    """
    Create crack regions at layer interfaces for 3D printed concrete.
    
    3D printed concrete often has weak inter-layer bonds where cracks
    preferentially initiate and propagate.
    
    Args:
        model: Abaqus model object
        assembly: Assembly object
        layer_interfaces: List of interface surfaces or sets
        
    Returns:
        List of crack regions
    """
    if not ABAQUS_AVAILABLE:
        return []
        
    crack_regions = []
    
    for i, interface in enumerate(layer_interfaces):
        # Create a set for this interface
        region_name = 'LayerInterface_{}'.format(i+1)
        
        if isinstance(interface, str):
            # Interface is a set name
            region = assembly.sets[interface]
        else:
            # Interface is a geometric entity
            region = interface
        
        crack_regions.append(region)
    
    return crack_regions
