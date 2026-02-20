# -*- coding: utf-8 -*-
"""
Main entry point for 3D printed concrete cube compression test
Complete workflow from geometry to job submission
Python 2.7 compatible for Abaqus 2021

Usage:
    In Abaqus CAE: execfile('main.py')
    Or in terminal: abaqus cae script=main.py
"""

from abaqus import *
from abaqusConstants import *
from caeModules import *
from driverUtils import executeOnCaeStartup
import os

# Execute standard CAE startup
executeOnCaeStartup()

# Import project modules
from config import config
from geometry import create_all_parts
from materials import create_all_materials
from mesh import create_all_mesh_and_sections
from assembly import create_complete_assembly
from steps_loads import create_all_steps_and_loads


def create_model():
    """
    Create complete 3DPC cube compression model
    
    This function orchestrates the entire model creation process:
    1. Create parts (concrete cube, support plates)
    2. Define materials (CDP concrete, cohesive, steel)
    3. Mesh parts and assign sections
    4. Create assembly with constraints
    5. Define steps, loads, and output
    
    Returns:
        model: The complete Abaqus model
    """
    print("\n" + "=" * 70)
    print("3D Printed Concrete Cube Compression Test")
    print("=" * 70)
    print("Model: %s" % config.model_name)
    print("Unit System: %s" % config.unit_system)
    print("=" * 70)
    
    # Create new model
    if config.model_name in mdb.models.keys():
        del mdb.models[config.model_name]
        print("\nDeleted existing model: %s" % config.model_name)
    
    model = mdb.Model(name=config.model_name)
    print("\nCreated new model: %s" % config.model_name)
    
    # Step 1: Create geometry
    print("\n" + "-" * 70)
    print("STEP 1: Geometry Creation")
    print("-" * 70)
    parts = create_all_parts(model, config)
    
    # Step 2: Define materials
    print("\n" + "-" * 70)
    print("STEP 2: Material Definition")
    print("-" * 70)
    materials = create_all_materials(model, config)
    
    # Step 3: Mesh and sections
    print("\n" + "-" * 70)
    print("STEP 3: Meshing and Section Assignment")
    print("-" * 70)
    create_all_mesh_and_sections(model, config)
    
    # Step 4: Assembly
    print("\n" + "-" * 70)
    print("STEP 4: Assembly and Constraints")
    print("-" * 70)
    assembly = create_complete_assembly(model, config)
    
    # Step 5: Steps and loads
    print("\n" + "-" * 70)
    print("STEP 5: Analysis Steps and Loading")
    print("-" * 70)
    create_all_steps_and_loads(model, assembly, config)
    
    print("\n" + "=" * 70)
    print("Model creation complete!")
    print("=" * 70)
    
    return model


def save_model(model):
    """
    Save model to work directory
    
    Args:
        model: Abaqus model object
    """
    # Create work directory if not exists
    if not os.path.exists(config.work_dir):
        os.makedirs(config.work_dir)
    
    # Change to work directory
    os.chdir(config.work_dir)
    
    # Save model
    model_path = os.path.join(config.work_dir, config.model_name + '.cae')
    mdb.saveAs(pathName=model_path)
    
    print("\nModel saved to: %s" % model_path)


def create_and_submit_job(model):
    """
    Create and submit analysis job
    
    Args:
        model: Abaqus model object
    """
    print("\n" + "=" * 70)
    print("Creating Analysis Job")
    print("=" * 70)
    
    # Delete existing job if present
    if config.job_name in mdb.jobs.keys():
        del mdb.jobs[config.job_name]
    
    # Create job
    job = mdb.Job(
        name=config.job_name,
        model=config.model_name,
        description='3DPC cube compression test',
        type=ANALYSIS,
        numCpus=1,
        numDomains=1
    )
    
    print("Job created: %s" % config.job_name)
    
    # Write input file (for verification)
    inp_path = os.path.join(config.work_dir, config.job_name + '.inp')
    job.writeInput(consistencyChecking=OFF)
    print("Input file written: %s" % inp_path)
    
    # Uncomment to submit job immediately
    # print("\nSubmitting job...")
    # job.submit()
    # job.waitForCompletion()
    # print("Job completed!")
    
    print("\nTo submit job manually:")
    print("  1. In Abaqus CAE: Job -> Submit")
    print("  2. Or in terminal: abaqus job=%s" % config.job_name)


def main():
    """
    Main execution function
    """
    # Create model
    model = create_model()
    
    # Save model
    save_model(model)
    
    # Create job (optional: also submit)
    create_and_submit_job(model)
    
    print("\n" + "=" * 70)
    print("Workflow Complete!")
    print("=" * 70)
    print("\nNext steps:")
    print("  1. Verify model in Abaqus CAE")
    print("  2. Check mesh quality")
    print("  3. Submit analysis job")
    print("  4. Compare results with reference")
    print("=" * 70)


# Execute main if run directly
if __name__ == "__main__":
    main()
