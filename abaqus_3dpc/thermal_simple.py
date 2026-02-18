# -*- coding: utf-8 -*-
"""
Simplified thermal-mechanical coupled analysis for 3D printed concrete.
Compatible with Abaqus 2021 on cao device.
"""

import sys
import os

# Add current directory to path
try:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
except NameError:
    sys.path.insert(0, r'C:\Users\openclaw\abaqus_3dpc')

from abaqus import *
from abaqusConstants import *
from caeModules import *
from driverUtils import executeOnCaeStartup

from config import Config
from materials import create_concrete_material, create_steel_material
from materials import create_concrete_section, create_steel_section
from geometry import create_concrete_beam, partition_into_layers
from rebar import create_rebar_layers
from thermal_coupled import (
    add_thermal_properties, add_steel_thermal_properties,
    create_thermal_step, set_initial_temperature,
    create_convective_film
)

executeOnCaeStartup()

print("=" * 70)
print("3DPC Thermal-Mechanical Coupled Analysis (Simplified)")
print("=" * 70)

# Configuration
config = Config()
config.beam_length = 300.0
config.beam_width = 100.0
config.beam_height = 50.0
config.layer_height = 10.0
config.mesh_size = 10.0
config.layer_wait_time = 60.0  # 60 seconds per layer

print("\nConfiguration:")
print("  Beam: %.0fx%.0fx%.0f mm" % (config.beam_length, config.beam_width, config.beam_height))
print("  Layers: %d (%.0fmm each)" % (config.get_layer_count(), config.layer_height))
print("  Layer time: %.0fs" % config.layer_wait_time)

# Work directory
work_dir = r"C:\Users\openclaw\Abaqus3DPC_Thermal"
if not os.path.exists(work_dir):
    os.makedirs(work_dir)
os.chdir(work_dir)

# Create model
print("\n[1/6] Creating model...")
model_name = '3DPC_Thermal'
if model_name in mdb.models.keys():
    del mdb.models[model_name]
model = mdb.Model(name=model_name)

# Create materials with thermal properties
print("[2/6] Creating materials with thermal properties...")
concrete_mat = create_concrete_material(model, config)
steel_mat = create_steel_material(model, config)
add_thermal_properties(model, config)
add_steel_thermal_properties(model, config)
print("  - C30 concrete with thermal properties")
print("  - Q235 steel with thermal properties")

# Create sections
concrete_sec = create_concrete_section(model, config)
steel_sec = create_steel_section(model, config)

# Create geometry
print("[3/6] Creating layered beam...")
beam_part = create_concrete_beam(model, config)
partition_into_layers(beam_part, config)
beam_part.SectionAssignment(region=(beam_part.cells,), sectionName='ConcreteSection')
print("  - Beam partitioned into %d layers" % config.get_layer_count())

# Create rebar
print("[4/6] Creating rebar...")
assembly = model.rootAssembly
rebar_part = create_rebar_layers(model, assembly, config)
print("  - Rebar created")

# Create thermal-mechanical step
print("[5/6] Creating thermal-mechanical step...")
from thermal_coupled import create_thermal_step
coupled_step = create_thermal_step(
    model, 'ThermalStep', 'Initial',
    time_period=300.0  # 5 minutes total
)
print("  - Coupled temperature-displacement step created")

# Set initial temperature
print("[6/6] Setting initial temperature...")
all_cells = beam_part.cells
region = (all_cells,)
set_initial_temperature(model, region, temp=25.0)
print("  - Initial temperature: 25C")

# Save model
mdb.saveAs(pathName=os.path.join(work_dir, '3DPC_Thermal.cae'))

print("\n" + "=" * 70)
print("Thermal-mechanical model created successfully!")
print("=" * 70)
print("File: %s" % os.path.join(work_dir, '3DPC_Thermal.cae'))
print("\nFeatures:")
print("  - Coupled temperature-displacement analysis")
print("  - Thermal material properties")
print("  - Initial temperature field")
print("  - Ready for thermal boundary conditions")
print("=" * 70)
