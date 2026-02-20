# -*- coding: utf-8 -*-
"""
Steps and loads module for 3D printed concrete cube compression test
Defines analysis step, boundary conditions, and loading
Python 2.7 compatible for Abaqus 2021
"""

from abaqus import *
from abaqusConstants import *


def create_analysis_step(model, config):
    """
    Create static analysis step with stabilization
    
    Original .inp:
    *Step, name=Step-1, nlgeom=YES, inc=10000
    *Static, stabilize, factor=0.0002, allsdtol=0, continue=NO
    
    Args:
        model: Abaqus model object
        config: Configuration object
        
    Returns:
        Step object
    """
    print("Creating analysis step...")
    
    step = model.StaticStep(
        name=config.step_name,
        previous='Initial',
        description='Cube compression test',
        nlgeom=config.nlgeom,
        maxNumInc=config.max_increments,
        initialInc=0.01,
        minInc=1e-12,
        maxInc=1.0
    )
    
    # Enable stabilization
    if config.stabilize:
        step.setValues(
            stabilize=ON,
            stabilization=((
                config.stabilize_factor,    # factor
                config.allsdtol,            # allsdtol
                0.0,                        # dsol
                0.0,                        # elim
                0.0,                        # eqnb
                0.0,                        # eqls
                0.0,                        # eqs
                0.0,                        # eqsl
                0.0,                        # eqsm
                0.0,                        # eqsr
                0.0,                        # eqss
                0.0,                        # eqst
                0.0,                        # eqsv
                0.0,                        # eqw
                0.0,                        # eqx
                0.0,                        # eqy
                0.0,                        # eqz
            ), )
        )
        print("  Stabilization enabled (factor=%.4f)" % config.stabilize_factor)
    
    print("  Step created: %s" % config.step_name)
    print("  Nonlinear geometry: %s" % config.nlgeom)
    print("  Max increments: %d" % config.max_increments)
    
    return step


def create_amplitude(model, config):
    """
    Create amplitude for loading
    
    Original .inp has:
    *AMPLITUDE,NAME=RA
    (but values are not shown in the snippet)
    
    For compression test, typically use ramp loading.
    
    Args:
        model: Abaqus model object
        config: Configuration object
        
    Returns:
        Amplitude object
    """
    print("Creating amplitude curve...")
    
    # Create smooth step amplitude for gradual loading
    # Time vs amplitude pairs
    amp_data = (
        (0.0, 0.0),
        (0.1, 0.1),
        (0.5, 0.5),
        (1.0, 1.0)
    )
    
    amplitude = model.SmoothStepAmplitude(
        name='RA',
        data=amp_data,
        timeSpan=STEP
    )
    
    print("  Amplitude 'RA' created (smooth step)")
    
    return amplitude


def create_boundary_conditions(model, assembly, config):
    """
    Create boundary conditions
    
    Original .inp has:
    - BC-1, BC-2: (not fully shown)
    - BC-3, BC-4: displacement with amplitude RA
    
    For compression test:
    - Fix bottom plate (RP2)
    - Apply displacement to top plate (RP1)
    
    Args:
        model: Abaqus model object
        assembly: Assembly object
        config: Configuration object
    """
    print("Creating boundary conditions...")
    
    # 1. Fix bottom plate (RP2) - all DOFs
    model.DisplacementBC(
        name='BC-Fixed',
        createStepName='Initial',
        region=assembly.sets['Set-RP2'],
        u1=0.0, u2=0.0, u3=0.0,
        ur1=0.0, ur2=0.0, ur3=0.0
    )
    print("  BC-Fixed: Bottom plate fully constrained")
    
    # 2. Apply displacement to top plate (RP1)
    # Compression: negative Y displacement
    displacement_magnitude = -5.0  # mm (to be adjusted based on test)
    
    model.DisplacementBC(
        name='BC-Load',
        createStepName=config.step_name,
        region=assembly.sets['Set-RP1'],
        u1=0.0,
        u2=displacement_magnitude,  # Vertical compression
        u3=0.0,
        ur1=0.0,
        ur2=UNSET,  # Allow rotation
        ur3=0.0,
        amplitude='RA'
    )
    print("  BC-Load: Top plate displacement = %.2f mm" % displacement_magnitude)
    
    # 3. Constrain side plates (if needed)
    # Prevent lateral movement of side plates
    model.DisplacementBC(
        name='BC-Side1',
        createStepName='Initial',
        region=assembly.sets['Set-RP3'],
        u1=0.0, u2=0.0, u3=0.0
    )
    print("  BC-Side1: Side plate 1 constrained")
    
    model.DisplacementBC(
        name='BC-Side2',
        createStepName='Initial',
        region=assembly.sets['Set-RP4'],
        u1=0.0, u2=0.0, u3=0.0
    )
    print("  BC-Side2: Side plate 2 constrained")


def create_field_output(model, config):
    """
    Create field output requests
    
    Original .inp requests:
    - Node Output: U, RF
    - Element Output: S, E, SDEG, STATUS
    - Contact Output: CSTRESS, CSTATUS
    
    Args:
        model: Abaqus model object
        config: Configuration object
    """
    print("Creating field output requests...")
    
    step = model.steps[config.step_name]
    
    # Node output
    model.FieldOutputRequest(
        name='F-Output-1',
        createStepName=config.step_name,
        variables=('U', 'RF', 'CF'),
        frequency=1
    )
    print("  Node output: U, RF, CF")
    
    # Element output
    model.FieldOutputRequest(
        name='F-Output-2',
        createStepName=config.step_name,
        variables=('S', 'E', 'SDEG', 'STATUS'),
        frequency=1
    )
    print("  Element output: S, E, SDEG, STATUS")
    
    # Contact output
    model.FieldOutputRequest(
        name='F-Output-3',
        createStepName=config.step_name,
        variables=('CSTRESS', 'CSTATUS'),
        frequency=1
    )
    print("  Contact output: CSTRESS, CSTATUS")


def create_history_output(model, config):
    """
    Create history output requests
    
    Original .inp:
    *Output, history, variable=PRESELECT
    
    Args:
        model: Abaqus model object
        config: Configuration object
    """
    print("Creating history output requests...")
    
    # Use preselected variables
    model.HistoryOutputRequest(
        name='H-Output-1',
        createStepName=config.step_name,
        variables=PRESELECT,
        frequency=1
    )
    print("  History output: PRESELECT")


def create_restart_output(model, config):
    """
    Create restart output
    
    Original .inp:
    *Restart, write, frequency=0
    
    Args:
        model: Abaqus model object
        config: Configuration object
    """
    print("Creating restart output...")
    
    if config.restart_write:
        model.Restart(
            name='Restart-1',
            createStepName=config.step_name,
            frequency=config.restart_frequency,
            numberIntervals=0,
            timeMarks=OFF
        )
        print("  Restart output: frequency=%d" % config.restart_frequency)


def create_all_steps_and_loads(model, assembly, config):
    """
    Complete step and load definition
    
    Args:
        model: Abaqus model object
        assembly: Assembly object
        config: Configuration object
    """
    print("\n" + "=" * 60)
    print("Creating Steps, Loads, and Output")
    print("=" * 60)
    
    # 1. Create amplitude
    amplitude = create_amplitude(model, config)
    
    # 2. Create analysis step
    step = create_analysis_step(model, config)
    
    # 3. Create boundary conditions
    create_boundary_conditions(model, assembly, config)
    
    # 4. Create output requests
    create_field_output(model, config)
    create_history_output(model, config)
    create_restart_output(model, config)
    
    print("=" * 60)
    print("Steps and loads complete!")
    print("=" * 60)


if __name__ == "__main__":
    # Test steps and loads
    from config import config
    from geometry import create_all_parts
    from materials import create_all_materials
    from mesh import create_all_mesh_and_sections
    from assembly import create_complete_assembly
    
    model = mdb.Model(name='TestSteps')
    
    parts = create_all_parts(model, config)
    materials = create_all_materials(model, config)
    create_all_mesh_and_sections(model, config)
    assembly = create_complete_assembly(model, config)
    create_all_steps_and_loads(model, assembly, config)
    
    print("\nTest complete!")
