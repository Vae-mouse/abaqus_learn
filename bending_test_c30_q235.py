# -*- coding: utf-8 -*-
"""
Three-point bending test for 3D printed concrete beam.
Simply supported beam with displacement-controlled loading.

Materials:
- Concrete: C30 (fck = 30 MPa, E = 30 GPa)
- Steel: Q235 (fy = 235 MPa, E = 200 GPa)
"""

from abaqus import *
from abaqusConstants import *
from caeModules import *
from driverUtils import executeOnCaeStartup
import os
import math

executeOnCaeStartup()

print("=" * 70)
print("3D Printed Concrete Beam - Three-Point Bending Test")
print("=" * 70)

# ============================================================================
# Configuration
# ============================================================================

# Beam dimensions (mm)
BEAM_LENGTH = 300.0
BEAM_WIDTH = 100.0
BEAM_HEIGHT = 50.0

# Material properties - C30 Concrete
CONCRETE_E = 30000.0      # MPa (30 GPa)
CONCRETE_NU = 0.2         # Poisson's ratio
CONCRETE_FCK = 30.0       # Compressive strength (MPa)
CONCRETE_FT = 2.0         # Tensile strength (MPa)
CONCRETE_RHO = 2.4e-09    # Density (tonne/mm3)

# Material properties - Q235 Steel
STEEL_E = 200000.0        # MPa (200 GPa)
STEEL_NU = 0.3            # Poisson's ratio
STEEL_FY = 235.0          # Yield strength (MPa)
STEEL_RHO = 7.8e-09       # Density (tonne/mm3)

# Rebar configuration
REBAR_DIAMETER = 6.0      # mm
REBAR_SPACING = 50.0      # mm
REBAR_COVER = 15.0        # mm

# Loading configuration
SPAN_LENGTH = 250.0       # Distance between supports (mm)
MAX_DISPLACEMENT = 10.0   # Maximum displacement at mid-span (mm)

# Mesh size
MESH_SIZE = 5.0           # mm

# Work directory
WORK_DIR = r"C:\Users\openclaw\BendingTest"
if not os.path.exists(WORK_DIR):
    os.makedirs(WORK_DIR)
os.chdir(WORK_DIR)

print("\nConfiguration:")
print("  Beam: %.0f x %.0f x %.0f mm" % (BEAM_LENGTH, BEAM_WIDTH, BEAM_HEIGHT))
print("  Span: %.0f mm" % SPAN_LENGTH)
print("  Concrete: C30 (E=%.0f MPa)" % CONCRETE_E)
print("  Steel: Q235 (fy=%.0f MPa)" % STEEL_FY)
print("  Max displacement: %.1f mm" % MAX_DISPLACEMENT)

# ============================================================================
# Create Model
# ============================================================================

print("\n[1/8] Creating model...")
MODEL_NAME = 'BendingTest'
if MODEL_NAME in mdb.models.keys():
    del mdb.models[MODEL_NAME]

model = mdb.Model(name=MODEL_NAME)

# ============================================================================
# Create Materials
# ============================================================================

print("[2/8] Creating materials...")

# C30 Concrete
concrete = model.Material(name='C30_Concrete')
concrete.Elastic(table=((CONCRETE_E, CONCRETE_NU), ))
concrete.Density(table=((CONCRETE_RHO, ), ))

# Concrete Damaged Plasticity (CDP) for bending behavior
concrete.ConcreteDamagedPlasticity(
    table=((30.0, 0.1, 1.16, 0.667, 0.0), )
)
concrete.concreteDamagedPlasticity.ConcreteCompressionHardening(
    table=((CONCRETE_FCK, 0.0), (CONCRETE_FCK * 1.2, 0.002))
)
concrete.concreteDamagedPlasticity.ConcreteTensionStiffening(
    table=((CONCRETE_FT, 0.0), (0.0, 0.001))
)

print("  - C30 Concrete with CDP")

# Q235 Steel
steel = model.Material(name='Q235_Steel')
steel.Elastic(table=((STEEL_E, STEEL_NU), ))
steel.Density(table=((STEEL_RHO, ), ))
steel.Plastic(table=((STEEL_FY, 0.0), (STEEL_FY * 1.5, 0.15)))

print("  - Q235 Steel (bilinear)")

# ============================================================================
# Create Sections
# ============================================================================

print("[3/8] Creating sections...")

# Concrete section
concrete_section = model.HomogeneousSolidSection(
    name='ConcreteSection',
    material='C30_Concrete'
)

# Steel section (truss)
rebar_area = math.pi * (REBAR_DIAMETER / 2.0) ** 2
steel_section = model.TrussSection(
    name='SteelSection',
    material='Q235_Steel',
    area=rebar_area
)

print("  - Concrete solid section")
print("  - Steel truss section (d=%.1f mm, A=%.2f mm2)" % (REBAR_DIAMETER, rebar_area))

# ============================================================================
# Create Beam Geometry
# ============================================================================

print("[4/8] Creating beam geometry...")

# Create sketch
sketch = model.ConstrainedSketch(name='__beam__', sheetSize=BEAM_WIDTH * 2)
sketch.rectangle(point1=(0.0, 0.0), point2=(BEAM_WIDTH, BEAM_HEIGHT))

# Create part
beam_part = model.Part(
    name='Beam',
    dimensionality=THREE_D,
    type=DEFORMABLE_BODY
)
beam_part.BaseSolidExtrude(sketch=sketch, depth=BEAM_LENGTH)

# Assign concrete section
beam_part.SectionAssignment(
    region=(beam_part.cells,),
    sectionName='ConcreteSection'
)

print("  - Beam created: %.0f x %.0f x %.0f mm" % (BEAM_LENGTH, BEAM_WIDTH, BEAM_HEIGHT))

# ============================================================================
# Create Rebar (Simplified - as truss elements)
# ============================================================================

print("[5/8] Creating rebar...")

rebar_part = model.Part(name='Rebar', dimensionality=THREE_D, type=DEFORMABLE_BODY)

# Create rebar (as wire features, not sketch)
# Bottom rebar layer
bottom_z = REBAR_COVER + REBAR_DIAMETER / 2.0
num_long_bars = int((BEAM_WIDTH - 2 * REBAR_COVER) / REBAR_SPACING) + 1

for i in range(num_long_bars):
    y_pos = REBAR_COVER + i * REBAR_SPACING
    if y_pos > BEAM_WIDTH - REBAR_COVER:
        break
    
    # Create wire along beam length using datum points
    p1 = (0.0, y_pos, bottom_z)
    p2 = (BEAM_LENGTH, y_pos, bottom_z)
    
    # Create datum points
    dp1 = rebar_part.DatumPointByCoordinate(coords=p1)
    dp2 = rebar_part.DatumPointByCoordinate(coords=p2)
    
    # Create wire between points
    rebar_part.WirePolyLine(points=((rebar_part.datums[dp1.id], 
                                     rebar_part.datums[dp2.id]), ), 
                           mergeType=IMPRINT, meshable=ON)

print("  - %d longitudinal bars at bottom" % num_long_bars)

# ============================================================================
# Create Assembly
# ============================================================================

print("[6/8] Creating assembly...")

assembly = model.rootAssembly
beam_instance = assembly.Instance(name='Beam-1', part=beam_part, dependent=ON)
rebar_instance = assembly.Instance(name='Rebar-1', part=rebar_part, dependent=ON)

# ============================================================================
# Create Sets for BCs and Loading
# ============================================================================

print("[7/8] Creating sets for boundary conditions...")

# Support locations
support_offset = (BEAM_LENGTH - SPAN_LENGTH) / 2.0

# Left support (pin)
left_support_face = beam_instance.faces.findAt(((BEAM_WIDTH/2.0, BEAM_HEIGHT/2.0, support_offset), ))
assembly.Set(name='LeftSupport', faces=(left_support_face,))

# Right support (roller)
right_support_face = beam_instance.faces.findAt(((BEAM_WIDTH/2.0, BEAM_HEIGHT/2.0, support_offset + SPAN_LENGTH), ))
assembly.Set(name='RightSupport', faces=(right_support_face,))

# Loading point (mid-span)
load_face = beam_instance.faces.findAt(((BEAM_WIDTH/2.0, BEAM_HEIGHT, BEAM_LENGTH/2.0), ))
assembly.Set(name='LoadPoint', faces=(load_face,))

# Entire beam for output
assembly.Set(name='BeamAll', cells=beam_instance.cells)

print("  - Left support at z=%.1f mm" % support_offset)
print("  - Right support at z=%.1f mm" % (support_offset + SPAN_LENGTH))
print("  - Load at mid-span z=%.1f mm" % (BEAM_LENGTH/2.0))

# ============================================================================
# Create Analysis Steps
# ============================================================================

print("[8/8] Creating analysis steps...")

# Initial step
initial_step = model.steps['Initial']

# Gravity step
gravity_step = model.StaticStep(
    name='Gravity',
    previous='Initial',
    description='Apply self-weight',
    timePeriod=1.0,
    nlgeom=OFF
)

# Bending step (displacement controlled)
bending_step = model.StaticStep(
    name='Bending',
    previous='Gravity',
    description='Three-point bending with displacement control',
    timePeriod=1.0,
    nlgeom=ON,  # Large deformation
    maxNumInc=1000,
    initialInc=0.01,
    minInc=1e-08,
    maxInc=0.1
)

print("  - Gravity step")
print("  - Bending step (displacement control)")

# ============================================================================
# Boundary Conditions
# ============================================================================

print("\nSetting up boundary conditions...")

# Left support (pin - fixed in X, Y, Z)
model.DisplacementBC(
    name='LeftSupport_BC',
    createStepName='Initial',
    region=assembly.sets['LeftSupport'],
    u1=0.0, u2=0.0, u3=0.0,
    ur1=UNSET, ur2=UNSET, ur3=UNSET
)

# Right support (roller - fixed in Y, Z, free in X)
model.DisplacementBC(
    name='RightSupport_BC',
    createStepName='Initial',
    region=assembly.sets['RightSupport'],
    u1=UNSET, u2=0.0, u3=0.0,
    ur1=UNSET, ur2=UNSET, ur3=UNSET
)

# Displacement-controlled loading
model.DisplacementBC(
    name='Load_BC',
    createStepName='Bending',
    region=assembly.sets['LoadPoint'],
    u1=UNSET, u2=-MAX_DISPLACEMENT, u3=UNSET,
    ur1=UNSET, ur2=UNSET, ur3=UNSET,
    amplitude=UNSET
)

print("  - Left support: pinned")
print("  - Right support: roller")
print("  - Load: displacement control (%.1f mm downward)" % MAX_DISPLACEMENT)

# ============================================================================
# Gravity Load
# ============================================================================

model.Gravity(
    name='GravityLoad',
    createStepName='Gravity',
    comp3=-9800.0  # mm/s^2
)

print("  - Self-weight applied")

# ============================================================================
# Mesh
# ============================================================================

print("\nMeshing...")

# Mesh beam
beam_part.seedPart(size=MESH_SIZE, deviationFactor=0.1, minSizeFactor=0.1)
beam_part.generateMesh()

# Mesh rebar
rebar_part.seedPart(size=MESH_SIZE, deviationFactor=0.1, minSizeFactor=0.1)
rebar_part.generateMesh()

print("  - Mesh size: %.1f mm" % MESH_SIZE)
print("  - Beam elements: %d" % len(beam_part.elements))
print("  - Rebar elements: %d" % len(rebar_part.elements))

# ============================================================================
# Create Job
# ============================================================================

print("\nCreating job...")

job_name = 'BendingTest_C30_Q235'
if job_name in mdb.jobs.keys():
    del mdb.jobs[job_name]

job = mdb.Job(
    name=job_name,
    model=MODEL_NAME,
    description='3DPC beam three-point bending test',
    type=ANALYSIS
)

# Save model
mdb.saveAs(pathName=os.path.join(WORK_DIR, 'BendingTest.cae'))

print("  - Job: %s" % job_name)
print("  - Model saved: %s" % os.path.join(WORK_DIR, 'BendingTest.cae'))

# ============================================================================
# Summary
# ============================================================================

print("\n" + "=" * 70)
print("Model created successfully!")
print("=" * 70)
print("\nTo run the analysis:")
print("  1. Submit job: abq2021 job=%s" % job_name)
print("  2. Monitor progress")
print("  3. Post-process results")
print("\nExpected outputs:")
print("  - Load-displacement curve")
print("  - Stress distribution")
print("  - Crack pattern (if CDP activated)")
print("=" * 70)
