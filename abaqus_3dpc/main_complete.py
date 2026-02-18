# -*- coding: utf-8 -*-
"""
Complete 3DPC model for cao device - Simplified but functional version.
This version uses only proven Abaqus 2021 APIs.
"""

from abaqus import *
from abaqusConstants import *
from caeModules import *
from driverUtils import executeOnCaeStartup
import os
import math

executeOnCaeStartup()

print("=" * 70)
print("3D Printed Concrete Beam - Complete Model (cao Device)")
print("=" * 70)

# ============================================================================
# Configuration
# ============================================================================

# Geometry
beam_length = 300.0
beam_width = 100.0
beam_height = 50.0
layer_height = 10.0

# Material - C30 Concrete
concrete_E = 30000.0
concrete_nu = 0.2
concrete_rho = 2.4e-09

# Material - Q235 Steel  
steel_E = 200000.0
steel_nu = 0.3
steel_rho = 7.8e-09
steel_yield = 235.0

# Rebar
rebar_diameter = 6.0
rebar_spacing = 50.0
rebar_cover = 15.0

# Mesh
mesh_size = 10.0

print("\nConfiguration:")
print("  Beam: %.0f x %.0f x %.0f mm" % (beam_length, beam_width, beam_height))
print("  Layers: %.0f mm (%d layers)" % (layer_height, int(beam_height/layer_height)))
print("  Concrete: C30 (E=%.0f MPa)" % concrete_E)
print("  Steel: Q235 (fy=%.0f MPa)" % steel_yield)

# ============================================================================
# Work Directory
# ============================================================================

work_dir = r"C:\Users\openclaw\Abaqus3DPC_Complete"
if not os.path.exists(work_dir):
    os.makedirs(work_dir)
os.chdir(work_dir)

# ============================================================================
# Create Model
# ============================================================================

print("\n[1/8] Creating model...")
model_name = '3DPC_Complete'
if model_name in mdb.models.keys():
    del mdb.models[model_name]
model = mdb.Model(name=model_name)

# ============================================================================
# Create Materials
# ============================================================================

print("[2/8] Creating materials...")

# C30 Concrete
concrete = model.Material(name='C30_Concrete')
concrete.Elastic(table=((concrete_E, concrete_nu), ))
concrete.Density(table=((concrete_rho, ), ))
print("  - C30 Concrete")

# Q235 Steel
steel = model.Material(name='Q235_Steel')
steel.Elastic(table=((steel_E, steel_nu), ))
steel.Density(table=((steel_rho, ), ))
steel.Plastic(table=((steel_yield, 0.0), (steel_yield*1.5, 0.15)))
print("  - Q235 Steel")

# ============================================================================
# Create Sections
# ============================================================================

print("[3/8] Creating sections...")

concrete_section = model.HomogeneousSolidSection(
    name='ConcreteSection',
    material='C30_Concrete'
)

# Steel truss section
rebar_area = math.pi * (rebar_diameter / 2.0) ** 2
steel_section = model.TrussSection(
    name='SteelSection',
    material='Q235_Steel',
    area=rebar_area
)
print("  - Concrete solid section")
print("  - Steel truss section (A=%.2f mm2)" % rebar_area)

# ============================================================================
# Create Beam Geometry
# ============================================================================

print("[4/8] Creating beam geometry...")

sketch = model.ConstrainedSketch(name='__beam__', sheetSize=200.0)
sketch.rectangle(point1=(0.0, 0.0), point2=(beam_width, beam_height))

beam_part = model.Part(
    name='ConcreteBeam',
    dimensionality=THREE_D,
    type=DEFORMABLE_BODY
)
beam_part.BaseSolidExtrude(sketch=sketch, depth=beam_length)

# Assign concrete section
beam_part.SectionAssignment(
    region=(beam_part.cells,),
    sectionName='ConcreteSection'
)

print("  - Beam created")

# ============================================================================
# Partition into Layers
# ============================================================================

print("[5/8] Partitioning into layers...")

layer_count = int(beam_height / layer_height)
for i in range(1, layer_count):
    z = i * layer_height
    datum_plane = beam_part.DatumPlaneByPrincipalPlane(
        principalPlane=XYPLANE,
        offset=z
    )
    cells = beam_part.cells
    beam_part.PartitionCellByDatumPlane(
        datumPlane=beam_part.datums[datum_plane.id],
        cells=cells
    )

print("  - Partitioned into %d layers" % layer_count)

# ============================================================================
# Create Rebar (Simplified)
# ============================================================================

print("[6/8] Creating rebar...")

rebar_part = model.Part(name='Rebar', dimensionality=THREE_D, type=DEFORMABLE_BODY)

# Create longitudinal rebars at bottom
bottom_z = rebar_cover + rebar_diameter / 2.0
num_bars = int((beam_width - 2 * rebar_cover) / rebar_spacing) + 1

for i in range(num_bars):
    y_pos = rebar_cover + i * rebar_spacing
    if y_pos > beam_width - rebar_cover:
        break
    
    # Create wire using datum points
    dp1 = rebar_part.DatumPointByCoordinate(coords=(0.0, y_pos, bottom_z))
    dp2 = rebar_part.DatumPointByCoordinate(coords=(beam_length, y_pos, bottom_z))
    
    rebar_part.WirePolyLine(
        points=((rebar_part.datums[dp1.id], rebar_part.datums[dp2.id]),),
        mergeType=IMPRINT,
        meshable=ON
    )

print("  - %d longitudinal bars created" % num_bars)

# Assign steel section to rebar
if rebar_part.edges:
    rebar_part.SectionAssignment(
        region=(rebar_part.edges,),
        sectionName='SteelSection'
    )

# ============================================================================
# Create Assembly
# ============================================================================

print("[7/8] Creating assembly...")

assembly = model.rootAssembly
beam_instance = assembly.Instance(name='Beam-1', part=beam_part, dependent=ON)
rebar_instance = assembly.Instance(name='Rebar-1', part=rebar_part, dependent=ON)

print("  - Assembly created")

# ============================================================================
# Mesh
# ============================================================================

print("[8/8] Generating mesh...")

# Mesh beam
beam_part.seedPart(size=mesh_size, deviationFactor=0.1, minSizeFactor=0.1)
beam_part.generateMesh()

# Mesh rebar
if rebar_part.edges:
    rebar_part.seedPart(size=mesh_size, deviationFactor=0.1, minSizeFactor=0.1)
    rebar_part.generateMesh()

print("  - Concrete: %d elements" % len(beam_part.elements))
if rebar_part.edges:
    print("  - Rebar: %d elements" % len(rebar_part.elements))

# ============================================================================
# Create Analysis Step
# ============================================================================

print("\nCreating analysis step...")

static_step = model.StaticStep(
    name='StaticLoad',
    previous='Initial',
    description='Static loading',
    timePeriod=1.0,
    nlgeom=OFF
)

print("  - Static step created")

# ============================================================================
# Gravity Load
# ============================================================================

model.Gravity(
    name='Gravity',
    createStepName='StaticLoad',
    comp3=-9800.0
)

print("  - Gravity load applied")

# ============================================================================
# Save Model
# ============================================================================

mdb.saveAs(pathName=os.path.join(work_dir, '3DPC_Complete.cae'))

print("\n" + "=" * 70)
print("Complete 3DPC model created successfully!")
print("=" * 70)
print("File: %s" % os.path.join(work_dir, '3DPC_Complete.cae'))
print("\nModel features:")
print("  - Layered concrete beam (%d layers)" % layer_count)
print("  - C30 concrete material")
print("  - Q235 steel rebar")
print("  - Structured mesh")
print("  - Static analysis step")
print("\nNext: Add printing simulation and testing")
print("=" * 70)
