# -*- coding: utf-8 -*-
"""
Example script demonstrating complete 3DPC workflow.
This script can be run in Abaqus CAE to create, run, and post-process a 3DPC model.
"""

from abaqus import *
from abaqusConstants import *
from caeModules import *
from driverUtils import executeOnCaeStartup
import os
import sys

# Add project directory to path
project_dir = os.path.dirname(os.path.abspath(__file__))
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

# Import project modules
from config import Config
from materials import (
    create_concrete_material,
    create_steel_material,
    create_concrete_section,
    create_steel_section
)
from geometry import create_concrete_beam, partition_into_layers, create_assembly
from rebar import create_rebar_layers
from embedded import create_embedded_constraint
from element_birth import create_printing_sequence
from meshing import mesh_all_parts
from postprocess import generate_report


def create_model():
    """Create the 3DPC model."""
    print("\n" + "=" * 70)
    print("Step 1: Creating 3DPC Model")
    print("=" * 70)
    
    # Configuration
    config = Config()
    config.validate()
    
    print("\nConfiguration:")
    print("  Beam: %.0f x %.0f x %.0f mm" % (
        config.beam_length, config.beam_width, config.beam_height))
    print("  Layers: %d (%.0f mm each)" % (
        config.get_layer_count(), config.layer_height))
    
    # Work directory
    work_dir = r"C:\Users\openclaw\Abaqus3DPC_Example"
    if not os.path.exists(work_dir):
        os.makedirs(work_dir)
    os.chdir(work_dir)
    
    # Create model
    model_name = '3DPC_Example'
    if model_name in mdb.models.keys():
        del mdb.models[model_name]
    model = mdb.Model(name=model_name)
    
    # Materials
    print("\n[1/6] Creating materials...")
    create_concrete_material(model, config)
    create_steel_material(model, config)
    create_concrete_section(model, config)
    create_steel_section(model, config)
    
    # Geometry
    print("[2/6] Creating geometry...")
    beam_part = create_concrete_beam(model, config)
    partition_into_layers(beam_part, config)
    beam_part.SectionAssignment(
        region=(beam_part.cells,),
        sectionName='ConcreteSection'
    )
    
    # Assembly
    print("[3/6] Creating assembly...")
    assembly = model.rootAssembly
    create_assembly(model, beam_part, config)
    
    # Rebar
    print("[4/6] Creating rebar...")
    rebar_part = create_rebar_layers(model, assembly, config)
    rebar_part.SectionAssignment(
        region=(rebar_part.edges,),
        sectionName='SteelSection'
    )
    
    # Mesh
    print("[5/6] Generating mesh...")
    mesh_stats = mesh_all_parts(model, config)
    
    # Constraints and printing sequence
    print("[6/6] Setting up constraints and printing sequence...")
    create_embedded_constraint(model, assembly, config)
    create_printing_sequence(model, assembly, config)
    
    # Save model
    model_path = os.path.join(work_dir, '3DPC_Example.cae')
    mdb.saveAs(pathName=model_path)
    
    print("\n" + "=" * 70)
    print("Model created successfully!")
    print("  File: %s" % model_path)
    print("  Concrete elements: %d" % mesh_stats['concrete_elements'])
    print("  Rebar elements: %d" % mesh_stats['rebar_elements'])
    print("=" * 70)
    
    return model, work_dir


def create_and_submit_job(model, work_dir):
    """Create and submit analysis job."""
    print("\n" + "=" * 70)
    print("Step 2: Creating and Submitting Job")
    print("=" * 70)
    
    job_name = '3DPC_Example_Job'
    
    # Create job
    job = mdb.Job(
        name=job_name,
        model=model.name,
        description='3D printed concrete example analysis',
        numCpus=4,
        numDomains=4,
        parallelizationMethodExplicit=DOMAIN
    )
    
    # Save model before submitting
    mdb.save()
    
    print("Job created: %s" % job_name)
    print("Submitting job...")
    
    # Submit job
    job.submit()
    job.waitForCompletion()
    
    print("Job completed!")
    print("=" * 70)
    
    return job_name


def post_process_results(work_dir, job_name):
    """Post-process analysis results."""
    print("\n" + "=" * 70)
    print("Step 3: Post-Processing Results")
    print("=" * 70)
    
    odb_path = os.path.join(work_dir, job_name + '.odb')
    
    if not os.path.exists(odb_path):
        print("Warning: ODB file not found: %s" % odb_path)
        return
    
    # Generate report
    report_path = os.path.join(work_dir, 'analysis_report.txt')
    report = generate_report(odb_path, report_path)
    
    print(report)
    print("\nReport saved to: %s" % report_path)
    print("=" * 70)


def main():
    """Main workflow function."""
    executeOnCaeStartup()
    
    print("\n" + "=" * 70)
    print("3D Printed Concrete - Complete Workflow Example")
    print("=" * 70)
    
    # Step 1: Create model
    model, work_dir = create_model()
    
    # Step 2: Create and submit job (optional - can be commented out for testing)
    # job_name = create_and_submit_job(model, work_dir)
    
    # Step 3: Post-process (requires completed job)
    # post_process_results(work_dir, job_name)
    
    print("\n" + "=" * 70)
    print("Workflow completed!")
    print("=" * 70)
    print("\nNext steps:")
    print("  1. Review model in Abaqus CAE")
    print("  2. Create and submit job manually, OR")
    print("  3. Uncomment job submission code in example.py")
    print("=" * 70)


if __name__ == "__main__":
    main()
