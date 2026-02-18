# -*- coding: utf-8 -*-
"""
Minimal 3DPC test - verify core functionality on cao device.
"""

from abaqus import *
from abaqusConstants import *
from caeModules import *
from driverUtils import executeOnCaeStartup
import os

executeOnCaeStartup()

print("=" * 70)
print("3DPC Minimal Test on cao Device")
print("=" * 70)

# Work directory
work_dir = r"C:\Users\openclaw\Abaqus3DPC_Minimal"
if not os.path.exists(work_dir):
    os.makedirs(work_dir)
os.chdir(work_dir)

# Configuration
beam_length = 300.0
beam_width = 100.0
beam_height = 50.0
layer_height = 10.0

print("\nConfiguration:")
print("  Beam: %.0f x %.0f x %.0f mm" % (beam_length, beam_width, beam_height))
print("  Layer height: %.0f mm" % layer_height)

# Create model
print("\n[1/5] Creating model...")
model_name = 'Minimal3DPC'
if model_name in mdb.models.keys():
    del mdb.models[model_name]
model = mdb.Model(name=model_name)

# Create material
print("[2/5] Creating material...")
concrete = model.Material(name='Concrete')
concrete.Elastic(table=((30000.0, 0.2), ))
concrete.Density(table=((2.4e-09, ), ))
print("  - Concrete created")

# Create section
section = model.HomogeneousSolidSection(
    name='ConcreteSection',
    material='Concrete'
)

# Create geometry
print("[3/5] Creating geometry...")
sketch = model.ConstrainedSketch(name='__profile__', sheetSize=200.0)
sketch.rectangle(point1=(0.0, 0.0), point2=(beam_width, beam_height))

beam_part = model.Part(
    name='Beam',
    dimensionality=THREE_D,
    type=DEFORMABLE_BODY
)
beam_part.BaseSolidExtrude(sketch=sketch, depth=beam_length)

# Assign section
beam_part.SectionAssignment(
    region=(beam_part.cells,),
    sectionName='ConcreteSection'
)

print("  - Beam created: %.0f x %.0f x %.0f mm" % (beam_length, beam_width, beam_height))

# Partition into layers
print("[4/5] Partitioning into layers...")
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

# Create assembly
print("[5/5] Creating assembly...")
assembly = model.rootAssembly
beam_instance = assembly.Instance(
    name='Beam-1',
    part=beam_part,
    dependent=ON
)

# Simple mesh
print("\nGenerating mesh...")
beam_part.seedPart(size=10.0, deviationFactor=0.1, minSizeFactor=0.1)
beam_part.generateMesh()
print("  - Mesh generated: %d elements" % len(beam_part.elements))

# Save model
mdb.saveAs(pathName=os.path.join(work_dir, 'Minimal3DPC.cae'))

print("\n" + "=" * 70)
print("Minimal 3DPC test completed successfully!")
print("=" * 70)
print("File: %s" % os.path.join(work_dir, 'Minimal3DPC.cae'))
print("\nCore functionality verified:")
print("  - Material creation")
print("  - Geometry modeling")
print("  - Layer partitioning")
print("  - Mesh generation")
print("  - Model save")
print("=" * 70)
