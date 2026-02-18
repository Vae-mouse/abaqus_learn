# -*- coding: utf-8 -*-
"""
Example: 3D printed concrete with damage plasticity and crack simulation.
Demonstrates CDP and XFEM for failure analysis.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from abaqus import *
    from abaqusConstants import *
    from caeModules import *
    ABAQUS_AVAILABLE = True
except ImportError:
    ABAQUS_AVAILABLE = False
    print("Warning: Abaqus modules not available. This script must be run within Abaqus CAE.")
    sys.exit(1)

from config import Config
from materials import create_concrete_material, create_steel_material
from materials import create_concrete_section, create_steel_section
from geometry import create_layered_beam
from rebar import create_rebar_layers
from meshing import mesh_concrete_part, mesh_rebar_part
from damage_plasticity import add_cdp_properties, setup_cdp_analysis
from xfem_crack import setup_xfem_analysis


def create_damage_analysis_model():
    """
    Create a 3D printed concrete model with damage plasticity and XFEM.
    """
    # Create model
    model_name = '3DPC_Damage'
    if model_name in mdb.models.keys():
        del mdb.models[model_name]
    model = mdb.Model(name=model_name)
    
    # Configuration
    config = Config()
    config.beam_length = 300.0
    config.beam_width = 100.0
    config.beam_height = 50.0
    config.layer_height = 10.0
    config.concrete_comp_strength = 30.0  # C30 concrete
    config.mesh_size = 5.0
    
    print("Creating 3DPC model with damage plasticity...")
    print("  Beam: {}x{}x{} mm".format(
        config.beam_length, config.beam_width, config.beam_height))
    print("  Concrete: C30 (fck={} MPa)".format(config.concrete_comp_strength))
    
    # Create materials with CDP
    print("\n1. Creating materials with CDP...")
    concrete_mat = create_concrete_material(model, config)
    steel_mat = create_steel_material(model, config)
    
    # Add CDP properties
    add_cdp_properties(model, config)
    print("   - Concrete: CDP with compression/tension damage")
    print("   - Steel: Elastic-plastic")
    
    # Create sections
    concrete_sec = create_concrete_section(model, config)
    steel_sec = create_steel_section(model, config)
    
    # Create geometry
    print("\n2. Creating layered beam...")
    concrete_part, layers = create_layered_beam(model, config)
    print("   - Created {} layers".format(len(layers)))
    
    # Create rebar
    print("\n3. Creating rebar...")
    rebar_part, rebar_sets = create_rebar_layers(model, config)
    
    # Create assembly
    print("\n4. Creating assembly...")
    assembly = model.rootAssembly
    assembly.DatumCsysByDefault(CARTESIAN)
    
    concrete_inst = assembly.Instance(
        name='Concrete-1', part=concrete_part, dependent=ON)
    rebar_inst = assembly.Instance(
        name='Rebar-1', part=rebar_part, dependent=ON)
    
    # Mesh
    print("\n5. Meshing...")
    mesh_concrete_part(concrete_part, config)
    mesh_rebar_part(rebar_part, config)
    
    # Create analysis steps
    print("\n6. Creating analysis steps...")
    
    # Initial step
    model.steps['Initial'].setValues(nlgeom=ON)
    
    # Loading step with displacement control for stable crack propagation
    model.StaticStep(
        name='ApplyLoad',
        previous='Initial',
        initialInc=0.01,
        maxInc=0.1,
        minInc=1e-08,
        maxNumInc=1000,
        nlgeom=ON
    )
    print("   - Static step with displacement control")
    
    # Setup CDP analysis
    print("\n7. Setting up CDP analysis...")
    cdp_results = setup_cdp_analysis(model, assembly, config)
    print("   - CDP properties added")
    print("   - Damage field output configured")
    
    # Setup XFEM for crack propagation
    print("\n8. Setting up XFEM...")
    # Define potential crack regions (bottom tension zone)
    crack_region = assembly.Set(
        name='CrackRegion',
        cells=concrete_inst.cells.findAt(
            ((config.beam_length/2, config.beam_width/2, config.layer_height/2),)
        )
    )
    
    xfem_results = setup_xfem_analysis(
        model, assembly, config,
        crack_regions=[crack_region],
        criterion_type='MAXPS',
        fracture_energy=70.0  # N/m for concrete
    )
    print("   - XFEM enrichment added")
    print("   - Fracture criterion: Max Principal Stress")
    print("   - Fracture energy: 70 N/m")
    
    # Apply boundary conditions
    print("\n9. Applying boundary conditions...")
    
    # Pin support at one end
    pin_region = assembly.Set(
        name='PinSupport',
        vertices=concrete_inst.vertices.findAt(
            ((0.0, 0.0, 0.0),)
        )
    )
    model.DisplacementBC(
        name='Pin',
        createStepName='Initial',
        region=pin_region,
        u1=0.0, u2=0.0, u3=0.0,
        ur1=UNSET, ur2=UNSET, ur3=UNSET
    )
    
    # Roller support at other end
    roller_region = assembly.Set(
        name='RollerSupport',
        vertices=concrete_inst.vertices.findAt(
            ((config.beam_length, 0.0, 0.0),)
        )
    )
    model.DisplacementBC(
        name='Roller',
        createStepName='Initial',
        region=roller_region,
        u1=0.0, u2=UNSET, u3=0.0,
        ur1=UNSET, ur2=UNSET, ur3=UNSET
    )
    
    # Apply displacement at midspan for bending
    load_region = assembly.Set(
        name='LoadPoint',
        vertices=concrete_inst.vertices.findAt(
            ((config.beam_length/2, config.beam_width/2, config.beam_height),)
        )
    )
    model.DisplacementBC(
        name='Load',
        createStepName='ApplyLoad',
        region=load_region,
        u1=UNSET, u2=UNSET, u3=-5.0,  # 5mm downward displacement
        ur1=UNSET, ur2=UNSET, ur3=UNSET
    )
    print("   - Simply supported beam")
    print("   - Displacement control loading")
    
    # Configure output
    print("\n10. Configuring output...")
    model.fieldOutputRequests['F-Output-1'].setValues(
        variables=(
            'S', 'E', 'U', 'PE', 'PEEQ',
            'DAMAGEC', 'DAMAGET', 'SDEG', 'STATUS',
            'PHILSM', 'PSILSM', 'STATUSXFEM'
        ),
        frequency=LAST_INCREMENT
    )
    print("   - Field output: Stress, Strain, Damage, XFEM status")
    
    # Save model
    print("\n11. Saving model...")
    mdb.saveAs(pathName='3DPC_Damage.cae')
    print("   - Saved as: 3DPC_Damage.cae")
    
    print("\n" + "="*60)
    print("Damage analysis model created successfully!")
    print("="*60)
    print("\nModel features:")
    print("  - Concrete Damaged Plasticity (CDP)")
    print("  - XFEM crack propagation")
    print("  - Compression and tension damage")
    print("  - Displacement-controlled loading")
    print("\nTo run the analysis:")
    print("  1. Create and submit job")
    print("  2. Monitor damage evolution (DAMAGEC, DAMAGET)")
    print("  3. Visualize crack propagation (PHILSM, STATUSXFEM)")
    print("  4. Use postprocess.py to extract damage history")
    
    return model


if __name__ == '__main__':
    create_damage_analysis_model()
