# -*- coding: utf-8 -*-
"""
Main script for 3D printed concrete beam simulation.
Integrates all modules to create complete model.
"""

from abaqus import *
from abaqusConstants import *
from caeModules import *
from driverUtils import executeOnCaeStartup
import os

# Import project modules
from config import Config
from materials import (
    create_concrete_material,
    create_steel_material,
    create_concrete_section,
    create_steel_section
)
from geometry import (
    create_concrete_beam,
    partition_into_layers,
    create_assembly
)
from rebar import create_rebar_layers
from printing import (
    create_print_steps,
    setup_gravity_load,
    create_layer_sets
)
from testing import (
    setup_bending_test,
    setup_compression_test,
    create_test_step
)
from embedded import (
    create_embedded_constraint,
    verify_embedded_constraint
)
from element_birth import (
    create_printing_sequence,
    verify_model_change_setup
)
from meshing import (
    mesh_all_parts,
    verify_mesh_quality
)
from cohesive import (
    create_layer_cohesive_interaction,
    create_cohesive_contact_property
)


def main():
    """Main function to create 3DPC model."""
    
    # Execute CAE startup
    executeOnCaeStartup()
    
    print("=" * 70)
    print("3D Printed Concrete Beam Simulation")
    print("=" * 70)
    
    # Initialize configuration
    config = Config()
    config.validate()
    
    print("\nConfiguration:")
    print("  Beam size: %.0f x %.0f x %.0f mm" % (
        config.beam_length, config.beam_width, config.beam_height))
    print("  Layer height: %.0f mm (%d layers)" % (
        config.layer_height, config.get_layer_count()))
    print("  Rebar diameter: %.0f mm" % config.rebar_diameter)
    
    # Work directory
    work_dir = r"C:\Users\openclaw\Abaqus3DPC"
    if not os.path.exists(work_dir):
        os.makedirs(work_dir)
    os.chdir(work_dir)
    
    # Create model
    print("\n[1/8] Creating model...")
    model_name = '3DPC_Beam'
    if model_name in mdb.models.keys():
        del mdb.models[model_name]
    model = mdb.Model(name=model_name)
    
    # Create materials
    print("[2/8] Creating materials...")
    concrete_mat = create_concrete_material(model, config)
    steel_mat = create_steel_material(model, config)
    concrete_sec = create_concrete_section(model, config)
    steel_sec = create_steel_section(model, config)
    
    # Create geometry
    print("[3/8] Creating geometry...")
    beam_part = create_concrete_beam(model, config)
    partition_into_layers(beam_part, config)
    
    # Assign concrete section
    beam_part.SectionAssignment(
        region=(beam_part.cells,),
        sectionName='ConcreteSection'
    )
    
    # Create assembly
    print("[4/8] Creating assembly...")
    assembly = model.rootAssembly
    beam_instance = create_assembly(model, beam_part, config)
    
    # Create rebar
    print("[5/8] Creating rebar mesh...")
    rebar_part = create_rebar_layers(model, assembly, config)
    
    # Assign truss section to rebar
    rebar_edges = rebar_part.edges
    rebar_region = regionToolset.Region(edges=rebar_edges)
    rebar_part.SectionAssignment(
        region=rebar_region,
        sectionName='SteelSection'
    )
    
    # Create mesh
    print("[6/8] Generating mesh...")
    mesh_stats = mesh_all_parts(model, config)
    verify_mesh_quality(model, config)
    
    # Create embedded constraint
    print("[7/8] Creating embedded element constraint...")
    embedded_constraint = create_embedded_constraint(model, assembly, config)
    verify_embedded_constraint(model, assembly)
    
    # Create printing sequence with Model Change
    print("[8/9] Creating printing sequence (Model Change)...")
    printing_setup = create_printing_sequence(model, assembly, config)
    verify_model_change_setup(model, assembly, config)
    
    # Create cohesive contact between layers
    print("[9/9] Creating inter-layer cohesive contact...")
    cohesive_prop = create_cohesive_contact_property(model)
    cohesive_setup = create_layer_cohesive_interaction(model, assembly, config)
    
    # Setup gravity load
    gravity = setup_gravity_load(model, config)
    
    # Save model
    print("\nSaving model...")
    mdb.saveAs(pathName=os.path.join(work_dir, '3DPC_Beam.cae'))
    
    print("\n" + "=" * 70)
    print("Model created successfully!")
    print("=" * 70)
    print("File: %s" % os.path.join(work_dir, '3DPC_Beam.cae'))
    print("\nModel Statistics:")
    print("  Concrete elements: %d" % mesh_stats['concrete_elements'])
    print("  Concrete nodes: %d" % mesh_stats['concrete_nodes'])
    print("  Rebar elements: %d" % mesh_stats['rebar_elements'])
    print("  Rebar nodes: %d" % mesh_stats['rebar_nodes'])
    print("  Print layers: %d" % config.get_layer_count())
    print("  Cohesive interfaces: %d" % (config.get_layer_count() - 1))
    print("\nNext steps:")
    print("  1. Create job and submit")
    print("  2. Monitor simulation progress")
    print("  3. Post-process results")
    print("=" * 70)


if __name__ == "__main__":
    main()
