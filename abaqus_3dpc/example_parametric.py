# -*- coding: utf-8 -*-
"""
Example: Parametric study for 3D printed concrete layer thickness.
Demonstrates automated parameter sweep and results collection.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from abaqus import *
    from abaqusConstants import *
    ABAQUS_AVAILABLE = True
except ImportError:
    ABAQUS_AVAILABLE = False
    print("This example must be run within Abaqus CAE.")
    print("For local testing, use test_parametric.py")
    sys.exit(1)

from config import Config
from parametric import (
    DesignVariable, DesignStudy,
    create_layer_thickness_study,
    create_rebar_ratio_study,
    create_span_depth_study
)


def create_simple_beam_model(config):
    """
    Create a simple beam model for parametric study.
    
    Args:
        config: Config object
        
    Returns:
        Model object
    """
    from materials import create_concrete_material, create_steel_material
    from materials import create_concrete_section, create_steel_section
    from geometry import create_layered_beam
    from rebar import create_rebar_layers
    from meshing import mesh_concrete_part, mesh_rebar_part
    from embedded import create_embedded_constraint
    
    # Create model
    model_name = 'ParametricBeam'
    if model_name in mdb.models.keys():
        del mdb.models[model_name]
    model = mdb.Model(name=model_name)
    
    # Create materials
    concrete_mat = create_concrete_material(model, config)
    steel_mat = create_steel_material(model, config)
    
    # Create sections
    concrete_sec = create_concrete_section(model, config)
    steel_sec = create_steel_section(model, config)
    
    # Create geometry
    concrete_part, layers = create_layered_beam(model, config)
    rebar_part, rebar_sets = create_rebar_layers(model, config)
    
    # Create assembly
    assembly = model.rootAssembly
    assembly.DatumCsysByDefault(CARTESIAN)
    
    concrete_inst = assembly.Instance(
        name='Concrete-1', part=concrete_part, dependent=ON)
    rebar_inst = assembly.Instance(
        name='Rebar-1', part=rebar_part, dependent=ON)
    
    # Mesh
    mesh_concrete_part(concrete_part, config)
    mesh_rebar_part(rebar_part, config)
    
    # Create embedded constraint
    create_embedded_constraint(model, assembly, concrete_inst, rebar_inst)
    
    # Create step
    model.StaticStep(
        name='ApplyLoad',
        previous='Initial',
        initialInc=0.1,
        maxInc=1.0,
        nlgeom=ON
    )
    
    # Apply boundary conditions
    # Pin support
    pin_region = assembly.Set(
        name='PinSupport',
        vertices=concrete_inst.vertices.findAt(((0.0, 0.0, 0.0),))
    )
    model.DisplacementBC(
        name='Pin', createStepName='Initial', region=pin_region,
        u1=0.0, u2=0.0, u3=0.0
    )
    
    # Roller support
    roller_region = assembly.Set(
        name='RollerSupport',
        vertices=concrete_inst.vertices.findAt(((config.beam_length, 0.0, 0.0),))
    )
    model.DisplacementBC(
        name='Roller', createStepName='Initial', region=roller_region,
        u1=0.0, u3=0.0
    )
    
    # Apply load
    load_region = assembly.Surface(
        name='LoadSurface',
        side2Faces=concrete_inst.faces.findAt(
            ((config.beam_length/2, config.beam_width/2, config.beam_height),)
        )
    )
    model.Pressure(
        name='Load',
        createStepName='ApplyLoad',
        region=load_region,
        magnitude=1.0  # MPa
    )
    
    return model


def run_layer_thickness_study():
    """
    Run a parametric study on layer thickness.
    """
    print("="*60)
    print("Layer Thickness Parametric Study")
    print("="*60)
    
    # Base configuration
    base_config = Config()
    base_config.beam_length = 300.0
    base_config.beam_width = 100.0
    base_config.beam_height = 50.0
    
    # Create study
    study = create_layer_thickness_study(
        base_config,
        thicknesses=[5.0, 10.0, 15.0, 20.0, 25.0]
    )
    
    print("\nStudy: {}".format(study.name))
    print("Design points: {}".format(len(study.generate_design_points())))
    
    # Generate design points
    design_points = study.generate_design_points()
    
    print("\nDesign Points:")
    for config_dict, point_id in design_points:
        print("  DP{}: layer_height = {} mm".format(
            point_id, config_dict['layer_height']))
    
    # Note: Actual execution would require Abaqus
    print("\nNote: To run this study in Abaqus:")
    print("  from parametric import run_parametric_study")
    print("  results = run_parametric_study(study, create_simple_beam_model)")
    
    return study


def run_rebar_ratio_study():
    """
    Run a parametric study on rebar diameter.
    """
    print("\n" + "="*60)
    print("Rebar Diameter Parametric Study")
    print("="*60)
    
    base_config = Config()
    base_config.beam_length = 300.0
    base_config.beam_width = 100.0
    base_config.beam_height = 50.0
    base_config.layer_height = 10.0
    
    study = create_rebar_ratio_study(
        base_config,
        diameters=[4.0, 6.0, 8.0, 10.0, 12.0]
    )
    
    print("\nStudy: {}".format(study.name))
    print("Design points: {}".format(len(study.generate_design_points())))
    
    design_points = study.generate_design_points()
    
    print("\nDesign Points:")
    for config_dict, point_id in design_points:
        print("  DP{}: rebar_diameter = {} mm".format(
            point_id, config_dict['rebar_diameter']))
    
    return study


def run_span_depth_study():
    """
    Run a parametric study on span-to-depth ratio.
    """
    print("\n" + "="*60)
    print("Span-to-Depth Ratio Parametric Study")
    print("="*60)
    
    base_config = Config()
    base_config.beam_width = 100.0
    base_config.layer_height = 10.0
    
    study = create_span_depth_study(
        base_config,
        spans=[200.0, 250.0, 300.0],
        depths=[30.0, 40.0, 50.0]
    )
    
    print("\nStudy: {}".format(study.name))
    print("Design points: {}".format(len(study.generate_design_points())))
    
    design_points = study.generate_design_points()
    
    print("\nDesign Points:")
    for config_dict, point_id in design_points:
        span = config_dict['beam_length']
        depth = config_dict['beam_height']
        ratio = span / depth
        print("  DP{}: span = {} mm, depth = {} mm, ratio = {:.1f}".format(
            point_id, span, depth, ratio))
    
    return study


def demonstrate_custom_study():
    """
    Demonstrate creating a custom parametric study.
    """
    print("\n" + "="*60)
    print("Custom Multi-Variable Study")
    print("="*60)
    
    base_config = Config()
    
    # Create custom study
    study = DesignStudy('CustomStudy', base_config)
    
    # Add variables
    study.add_variable(DesignVariable(
        name='LayerHeight',
        param_path='layer_height',
        min_val=5.0,
        max_val=20.0,
        num_points=4
    ))
    
    study.add_variable(DesignVariable(
        name='RebarSpacing',
        param_path='rebar_spacing',
        values=[40.0, 50.0, 60.0, 75.0, 100.0]
    ))
    
    print("\nStudy: {}".format(study.name))
    print("Variables: {}".format(len(study.variables)))
    print("Design points: {}".format(len(study.generate_design_points())))
    
    design_points = study.generate_design_points()
    
    print("\nFirst 5 Design Points:")
    for config_dict, point_id in design_points[:5]:
        print("  DP{}: {}".format(point_id, config_dict))
    
    if len(design_points) > 5:
        print("  ... and {} more".format(len(design_points) - 5))
    
    return study


if __name__ == '__main__':
    # Run all example studies
    study1 = run_layer_thickness_study()
    study2 = run_rebar_ratio_study()
    study3 = run_span_depth_study()
    study4 = demonstrate_custom_study()
    
    print("\n" + "="*60)
    print("Parametric Study Examples Complete")
    print("="*60)
    print("\nSummary:")
    print("  - Layer thickness study: {} points".format(
        len(study1.design_points)))
    print("  - Rebar diameter study: {} points".format(
        len(study2.design_points)))
    print("  - Span-to-depth study: {} points".format(
        len(study3.design_points)))
    print("  - Custom multi-variable study: {} points".format(
        len(study4.design_points)))
    print("\nTo execute these studies in Abaqus:")
    print("  1. Open Abaqus CAE")
    print("  2. Run: execfile('example_parametric.py')")
    print("  3. Uncomment the run_parametric_study() calls")
