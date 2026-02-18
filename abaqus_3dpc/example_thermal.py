# -*- coding: utf-8 -*-
"""
Thermal-mechanical coupled analysis example for 3D printed concrete.
Demonstrates heat transfer simulation during printing process.
"""

import sys
import os

# Add current directory to path for imports
try:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
except NameError:
    # __file__ not defined in Abaqus noGUI mode
    sys.path.insert(0, r'C:\Users\openclaw\abaqus_3dpc')

try:
    from abaqus import *
    from abaqusConstants import *
    from caeModules import *
    ABAQUS_AVAILABLE = True
except ImportError:
    ABAQUS_AVAILABLE = False
    print("Warning: Abaqus modules not available. This script must be run within Abaqus CAE.")
    print("For local testing, use test_thermal.py")
    sys.exit(1)

from config import Config
from materials import create_concrete_material, create_steel_material
from materials import create_concrete_section, create_steel_section
from geometry import create_concrete_beam, partition_into_layers, create_assembly
from rebar import create_rebar_layers
from meshing import mesh_concrete_part, mesh_rebar_part
from thermal_coupled import (
    add_thermal_properties, add_steel_thermal_properties,
    create_thermal_step, set_initial_temperature,
    create_convective_film, create_radiation
)


def create_thermal_3dpc_model():
    """
    Create a 3D printed concrete model with thermal-mechanical coupling.
    """
    # Create model
    model_name = '3DPC_Thermal'
    if model_name in mdb.models.keys():
        del mdb.models[model_name]
    model = mdb.Model(name=model_name)
    
    # Configuration
    config = Config()
    config.beam_length = 300.0
    config.beam_width = 100.0
    config.beam_height = 50.0
    config.layer_height = 10.0
    config.mesh_size = 10.0  # Coarser mesh for thermal analysis
    
    print("Creating thermal-mechanical coupled 3DPC model...")
    print("  Beam: {}x{}x{} mm".format(
        config.beam_length, config.beam_width, config.beam_height))
    print("  Layers: {} ({}mm each)".format(
        config.get_layer_count(), config.layer_height))
    
    # Create materials with thermal properties
    print("\n1. Creating materials with thermal properties...")
    concrete_mat = create_concrete_material(model, config)
    steel_mat = create_steel_material(model, config)
    
    # Add thermal properties
    add_thermal_properties(model, config)
    add_steel_thermal_properties(model, config)
    print("   - Concrete: thermal conductivity, specific heat, expansion")
    print("   - Steel: thermal conductivity, specific heat, expansion")
    
    # Create sections
    concrete_sec = create_concrete_section(model, config)
    steel_sec = create_steel_section(model, config)
    
    # Create layered concrete beam
    print("\n2. Creating layered beam geometry...")
    concrete_part, layers = create_layered_beam(model, config)
    print("   - Created {} layers".format(len(layers)))
    
    # Create rebar
    print("\n3. Creating rebar layers...")
    rebar_part, rebar_sets = create_rebar_layers(model, config)
    print("   - Created rebar with {} sets".format(len(rebar_sets)))
    
    # Create assembly
    print("\n4. Creating assembly...")
    assembly = model.rootAssembly
    assembly.DatumCsysByDefault(CARTESIAN)
    
    # Instance concrete
    concrete_inst = assembly.Instance(
        name='Concrete-1',
        part=concrete_part,
        dependent=ON
    )
    
    # Instance rebar
    rebar_inst = assembly.Instance(
        name='Rebar-1',
        part=rebar_part,
        dependent=ON
    )
    
    # Mesh parts
    print("\n5. Meshing parts...")
    mesh_concrete_part(concrete_part, config)
    mesh_rebar_part(rebar_part, config)
    print("   - Concrete meshed with C3D8RT elements")
    print("   - Rebar meshed with T3D2T elements")
    
    # Create coupled thermal-mechanical steps
    print("\n6. Creating thermal-mechanical analysis steps...")
    
    # Replace default step with coupled step
    model.steps['Initial'].setValues(
        nlgeom=ON
    )
    
    # Create printing steps
    num_layers = config.get_layer_count()
    for i in range(num_layers):
        step_name = 'PrintLayer-{}'.format(i+1)
        prev_step = 'Initial' if i == 0 else 'PrintLayer-{}'.format(i)
        
        step = create_thermal_step(
            model, step_name, prev_step,
            time_period=config.layer_wait_time
        )
        print("   - Created step: {} ({}s)".format(step_name, config.layer_wait_time))
    
    # Set initial temperature
    print("\n7. Setting initial temperature field...")
    all_regions = assembly.instances['Concrete-1'].sets['All']
    set_initial_temperature(model, all_regions, temp=25.0)
    print("   - Initial temperature: 25C")
    
    # Create convection on external surfaces
    print("\n8. Creating thermal boundary conditions...")
    # Get external surfaces (simplified - all surfaces)
    ext_surfaces = assembly.instances['Concrete-1'].surfaces['External']
    
    for i in range(num_layers):
        step_name = 'PrintLayer-{}'.format(i+1)
        
        # Convective cooling
        create_convective_film(
            model, step_name, ext_surfaces,
            film_coef=10.0,  # W/m^2/K - natural convection
            sink_temp=25.0   # Ambient temperature
        )
        
        # Radiation
        create_radiation(
            model, step_name, ext_surfaces,
            emissivity=0.9,
            ambient_temp=25.0
        )
    
    print("   - Convective film: h=10 W/m^2/K")
    print("   - Surface radiation: emissivity=0.9")
    
    # Create field output for thermal results
    print("\n9. Setting up field output...")
    model.fieldOutputRequests['F-Output-1'].setValues(
        variables=('S', 'E', 'U', 'NT', 'HFL', 'RFL', 'TEMP'),
        frequency=LAST_INCREMENT
    )
    print("   - Output: Stress, Strain, Displacement, Nodal Temp, Heat Flux")
    
    # Create history output for temperature monitoring
    print("\n10. Creating history output...")
    # Monitor center point temperature
    center_point = assembly.Set(
        name='MonitorPoint',
        vertices=assembly.instances['Concrete-1'].vertices.findAt(
            ((config.beam_length/2, config.beam_width/2, config.beam_height/2),)
        )
    )
    
    model.HistoryOutputRequest(
        name='H-Output-Temp',
        createStepName='PrintLayer-1',
        variables=('NT', ),
        region=center_point,
        frequency=EVERY_TIME_INCREMENT
    )
    print("   - Monitoring center point temperature")
    
    # Save model
    print("\n11. Saving model...")
    mdb.saveAs(pathName='3DPC_Thermal.cae')
    print("   - Saved as: 3DPC_Thermal.cae")
    
    print("\n" + "="*60)
    print("Thermal-mechanical coupled model created successfully!")
    print("="*60)
    print("\nModel features:")
    print("  - Coupled temperature-displacement analysis")
    print("  - {} printing steps with thermal effects".format(num_layers))
    print("  - Convective cooling and radiation")
    print("  - Temperature-dependent material properties")
    print("  - Thermal stress calculation")
    print("\nTo run the analysis:")
    print("  1. Create and submit job")
    print("  2. Monitor temperature and stress evolution")
    print("  3. Use postprocess.py to extract thermal results")
    
    return model


if __name__ == '__main__':
    create_thermal_3dpc_model()
