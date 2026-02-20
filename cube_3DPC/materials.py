# -*- coding: utf-8 -*-
"""
Materials module for 3D printed concrete cube compression test
Defines CDP concrete, cohesive adhesives, and steel materials
Python 2.7 compatible for Abaqus 2021
"""

from abaqus import *
from abaqusConstants import *


def create_concrete_material(model, config):
    """
    Create concrete material with CDP (Concrete Damaged Plasticity) model
    
    CDP is the standard model for concrete in Abaqus, accounting for:
    - Compression hardening and damage
    - Tension stiffening and damage
    - Stiffness degradation
    
    Args:
        model: Abaqus model object
        config: Configuration object with material parameters
        
    Returns:
        Material object
    """
    print("Creating concrete material (CDP)...")
    
    # Create material
    mat = model.Material(name=config.concrete_material_name)
    
    # 1. Density
    # Unit: tonne/mm3 (SI with mm)
    mat.Density(table=((config.concrete_density, ), ))
    print("  Density: %.2e tonne/mm3" % config.concrete_density)
    
    # 2. Elastic properties
    # Linear elastic behavior before damage
    mat.Elastic(table=((config.concrete_E, config.concrete_nu), ))
    print("  Elastic: E=%.1f MPa, nu=%.3f" % (config.concrete_E, config.concrete_nu))
    
    # 3. Concrete Damaged Plasticity
    # Main parameters controlling concrete behavior
    mat.ConcreteDamagedPlasticity(
        table=((
            config.cdp_dilation_angle,      # Dilation angle (degrees)
            config.cdp_eccentricity,        # Flow potential eccentricity
            config.cdp_fb0_fc0,             # fb0/fc0 ratio
            config.cdp_k,                   # K parameter
            config.cdp_viscosity            # Viscosity parameter
        ), )
    )
    print("  CDP parameters set")
    
    # 4. Compression Hardening
    # Stress-strain relationship in compression (before damage)
    # Table: (stress, strain)
    if config.concrete_comp_hardening:
        mat.ConcreteCompressionHardening(
            table=tuple(config.concrete_comp_hardening)
        )
        print("  Compression hardening: %d points" % len(config.concrete_comp_hardening))
    
    # 5. Tension Stiffening (displacement type)
    # Post-cracking behavior in tension
    # Table: (stress, displacement) - displacement controls crack opening
    if config.concrete_tension_stiffening:
        mat.ConcreteTensionStiffening(
            type=DISPLACEMENT,
            table=tuple(config.concrete_tension_stiffening)
        )
        print("  Tension stiffening: %d points" % len(config.concrete_tension_stiffening))
    
    # 6. Compression Damage
    # Stiffness degradation in compression
    # Table: (damage, strain), damage from 0 (no damage) to 1 (full damage)
    if config.concrete_comp_damage:
        mat.ConcreteCompressionDamage(
            table=tuple(config.concrete_comp_damage)
        )
        print("  Compression damage: %d points" % len(config.concrete_comp_damage))
    
    # 7. Tension Damage (displacement type)
    # Stiffness degradation in tension
    # Table: (damage, displacement)
    if config.concrete_tension_damage:
        mat.ConcreteTensionDamage(
            type=DISPLACEMENT,
            table=tuple(config.concrete_tension_damage)
        )
        print("  Tension damage: %d points" % len(config.concrete_tension_damage))
    
    print("  Concrete material created successfully!")
    return mat


def create_cohesive_material(model, config, name, is_xz=False):
    """
    Create cohesive material for interlayer bonding
    
    Cohesive elements model the interface between concrete layers,
    accounting for delamination and interlayer failure.
    
    Args:
        model: Abaqus model object
        config: Configuration object
        name: Material name (e.g., 'ADHESIVE1')
        is_xz: Whether this is XZ direction (different stack direction)
        
    Returns:
        Material object
    """
    print("Creating cohesive material: %s..." % name)
    
    mat = model.Material(name=name)
    
    # 1. Density
    mat.Density(table=((config.cohesive_density, ), ))
    
    # 2. Elastic behavior (traction-separation)
    # Three stiffness values: normal (nn), shear1 (ss), shear2 (tt)
    mat.Elastic(
        type=TRACTION,
        table=((
            config.cohesive_Enn,    # Normal stiffness
            config.cohesive_Ess,    # Shear stiffness 1
            config.cohesive_Ett     # Shear stiffness 2
        ), )
    )
    print("  Elastic: Enn=%.1f, Ess=%.1f, Ett=%.1f MPa" % (
        config.cohesive_Enn, config.cohesive_Ess, config.cohesive_Ett))
    
    # 3. Damage Initiation
    # QUADS criterion: quadratic stress criterion
    # Damage starts when: (tn/tn_max)^2 + (ts1/ts1_max)^2 + (ts2/ts2_max)^2 = 1
    mat.DamageInitiation(
        criterion=QUADS,
        table=((
            10.0,   # Normal strength (tn_max) - to be updated from paper
            20.0,   # Shear strength 1 (ts1_max)
            20.0    # Shear strength 2 (ts2_max)
        ), )
    )
    print("  Damage initiation: QUADS")
    
    # 4. Damage Evolution
    # Energy-based evolution with power law mixed mode behavior
    # Power law: (GI/GIc)^power + (GII/GIIc)^power + (GIII/GIIIc)^power = 1
    mat.DamageEvolution(
        type=ENERGY,
        mixedModeBehavior=POWER_LAW,
        power=config.cohesive_power_law,
        table=((
            config.cohesive_GIc,    # Mode I fracture energy
            config.cohesive_GIIc,   # Mode II fracture energy
            config.cohesive_GIIIc   # Mode III fracture energy
        ), )
    )
    print("  Damage evolution: ENERGY, POWER LAW (power=%.1f)" % config.cohesive_power_law)
    print("  Fracture energies: GIc=%.3f, GIIc=%.3f, GIIIc=%.3f mJ/mm2" % (
        config.cohesive_GIc, config.cohesive_GIIc, config.cohesive_GIIIc))
    
    print("  Cohesive material %s created successfully!" % name)
    return mat


def create_steel_material(model, config):
    """
    Create steel material for support plates
    
    Simple elastic material for the rigid plates
    
    Args:
        model: Abaqus model object
        config: Configuration object
        
    Returns:
        Material object
    """
    print("Creating steel material...")
    
    mat = model.Material(name=config.steel_material_name)
    
    # Density
    mat.Density(table=((config.steel_density, ), ))
    
    # Elastic properties
    mat.Elastic(table=((config.steel_E, config.steel_nu), ))
    
    print("  Steel: E=%.1f MPa, nu=%.3f, rho=%.2e" % (
        config.steel_E, config.steel_nu, config.steel_density))
    print("  Steel material created successfully!")
    
    return mat


def create_all_materials(model, config):
    """
    Create all materials for the model
    
    Args:
        model: Abaqus model object
        config: Configuration object
        
    Returns:
        Dictionary of created materials
    """
    print("\n" + "=" * 60)
    print("Creating Materials")
    print("=" * 60)
    
    materials = {}
    
    # 1. Concrete (CDP)
    materials['concrete'] = create_concrete_material(model, config)
    
    # 2. Cohesive adhesives (5 types)
    for i, name in enumerate(config.adhesive_names):
        # ADHESIVE5 is XZ direction
        is_xz = (name == 'ADHESIVE5')
        materials[name] = create_cohesive_material(model, config, name, is_xz)
    
    # 3. Steel (for plates)
    materials['steel'] = create_steel_material(model, config)
    
    print("=" * 60)
    print("All materials created successfully!")
    print("Total: %d materials" % len(materials))
    print("=" * 60)
    
    return materials


if __name__ == "__main__":
    # Test material creation
    from config import config
    
    model = mdb.Model(name='TestMaterials')
    materials = create_all_materials(model, config)
    
    print("\nTest complete!")
    print("Materials created: %s" % list(materials.keys()))
