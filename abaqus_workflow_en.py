# -*- coding: utf-8 -*-
"""
Abaqus Complete Workflow Test Script
Modeling -> Material -> Assembly -> Step -> Load -> Mesh -> Job -> Post-processing
"""
from abaqus import *
from abaqusConstants import *
from caeModules import *
from driverUtils import executeOnCaeStartup
import os

# Execute CAE startup
executeOnCaeStartup()

print("=" * 70)
print("Abaqus Complete Workflow Automation Test")
print("=" * 70)

# Work directory
workDir = r"C:\Users\openclaw\AbaqusTest"
if not os.path.exists(workDir):
    os.makedirs(workDir)
os.chdir(workDir)
print("Work directory: %s" % workDir)

# ============================================================
# 1. Create Model
# ============================================================
print("\n" + "=" * 70)
print("Step 1: Create Model")
print("=" * 70)

modelName = 'TestModel'
if modelName in mdb.models.keys():
    del mdb.models[modelName]

model = mdb.Model(name=modelName)
print("Created model: %s" % modelName)

# ============================================================
# 2. Create Part (Cantilever Beam)
# ============================================================
print("\n" + "=" * 70)
print("Step 2: Create Part - Cantilever Beam")
print("=" * 70)

# Create sketch
sketch = model.ConstrainedSketch(name='__profile__', sheetSize=200.0)
sketch.rectangle(point1=(0.0, 0.0), point2=(100.0, 10.0))

# Create 3D part
part = model.Part(name='Beam', dimensionality=THREE_D, type=DEFORMABLE_BODY)
part.BaseSolidExtrude(sketch=sketch, depth=5.0)

print("Created part: Beam (100x10x5 mm)")
print("Volume: %.2f mm3" % part.getVolume())

# ============================================================
# 3. Create Material
# ============================================================
print("\n" + "=" * 70)
print("Step 3: Create Material")
print("=" * 70)

material = model.Material(name='Steel')
material.Elastic(table=((210000.0, 0.3), ))  # E = 210 GPa, nu = 0.3
material.Density(table=((7.8e-09, ), ))  # rho = 7.8 g/cm3

print("Created material: Steel")
print("  Young's modulus: 210 GPa")
print("  Poisson's ratio: 0.3")
print("  Density: 7.8 g/cm3")

# ============================================================
# 4. Create Section and Assign
# ============================================================
print("\n" + "=" * 70)
print("Step 4: Create Section and Assign")
print("=" * 70)

section = model.HomogeneousSolidSection(name='BeamSection', material='Steel')
region = (part.cells,)
part.SectionAssignment(region=region, sectionName='BeamSection')

print("Created section: BeamSection")
print("Section assignment completed")

# ============================================================
# 5. Create Assembly
# ============================================================
print("\n" + "=" * 70)
print("Step 5: Create Assembly")
print("=" * 70)

assembly = model.rootAssembly
instance = assembly.Instance(name='Beam-1', part=part, dependent=ON)

print("Created assembly instance: Beam-1")

# ============================================================
# 6. Create Analysis Step
# ============================================================
print("\n" + "=" * 70)
print("Step 6: Create Analysis Step")
print("=" * 70)

step = model.StaticStep(name='ApplyLoad', previous='Initial', 
                        description='Apply tip load',
                        timePeriod=1.0, nlgeom=OFF)

print("Created step: ApplyLoad")
print("  Type: Static analysis")
print("  Time period: 1.0")

# ============================================================
# 7. Create Boundary Condition (Fixed End)
# ============================================================
print("\n" + "=" * 70)
print("Step 7: Create Boundary Condition")
print("=" * 70)

# Select fixed end face (x=0)
faces = instance.faces
fixedFace = faces.findAt(((0.0, 5.0, 2.5), ))
region = assembly.Set(name='FixedEnd', faces=(fixedFace,))

# Create fixed BC
bc = model.DisplacementBC(name='Fixed', createStepName='Initial', 
                          region=region, u1=0.0, u2=0.0, u3=0.0,
                          ur1=0.0, ur2=0.0, ur3=0.0)

print("Created BC: Fixed (fixed end)")

# ============================================================
# 8. Create Load (Tip Load)
# ============================================================
print("\n" + "=" * 70)
print("Step 8: Create Load")
print("=" * 70)

# Select free end face (x=100)
loadFace = faces.findAt(((100.0, 5.0, 2.5), ))
region = assembly.Set(name='LoadEnd', faces=(loadFace,))

# Create concentrated force (downward -Y direction)
load = model.ConcentratedForce(name='TipLoad', createStepName='ApplyLoad',
                               region=region, cf2=-1000.0)  # 1000 N downward

print("Created load: TipLoad")
print("  Magnitude: 1000 N")
print("  Direction: -Y (downward)")

# ============================================================
# 9. Mesh
# ============================================================
print("\n" + "=" * 70)
print("Step 9: Mesh")
print("=" * 70)

# Set mesh controls
cells = part.cells
pickedRegions = cells.getSequenceFromMask(mask=('[#1 ]', ), )
part.setMeshControls(regions=pickedRegions, elemShape=HEX, technique=STRUCTURED)

# Set element type
elemType = mesh.ElemType(elemCode=C3D8R, elemLibrary=STANDARD)
part.setElementType(regions=(pickedRegions, ), elemTypes=(elemType,))

# Seed
part.seedPart(size=5.0, deviationFactor=0.1, minSizeFactor=0.1)

# Generate mesh
part.generateMesh()

print("Mesh generated")
print("  Element type: C3D8R (8-node hexahedron, reduced integration)")
print("  Seed size: 5.0 mm")

# ============================================================
# 10. Create Job and Submit
# ============================================================
print("\n" + "=" * 70)
print("Step 10: Create Job and Submit")
print("=" * 70)

jobName = 'BeamAnalysis'
if jobName in mdb.jobs.keys():
    del mdb.jobs[jobName]

job = mdb.Job(name=jobName, model=modelName, 
              description='Cantilever beam analysis')

print("Created job: %s" % jobName)

# Save model
mdb.saveAs(pathName=os.path.join(workDir, 'BeamAnalysis.cae'))
print("Model saved")

# Submit job
print("\nSubmitting job...")
job.submit()
job.waitForCompletion()

print("Job completed!")

# ============================================================
# 11. Post-processing
# ============================================================
print("\n" + "=" * 70)
print("Step 11: Post-processing")
print("=" * 70)

# Open result file
odbPath = os.path.join(workDir, '%s.odb' % jobName)
odb = session.openOdb(name=odbPath)

# Display in viewport
session.viewports['Viewport: 1'].setValues(displayedObject=odb)

# Get maximum displacement
lastFrame = odb.steps['ApplyLoad'].frames[-1]
displacement = lastFrame.fieldOutputs['U']
maxDisp = max([value.magnitude for value in displacement.values])

print("Maximum displacement: %.4f mm" % maxDisp)

# Get maximum stress
stress = lastFrame.fieldOutputs['S']
maxStress = max([value.maxPrincipal for value in stress.values])

print("Maximum principal stress: %.2f MPa" % maxStress)

# Save image
session.printToFile(fileName=os.path.join(workDir, 'Deformation'), 
                    format=PNG, canvasObjects=(session.viewports['Viewport: 1'], ))

print("Result image saved")

# Close ODB
odb.close()

# ============================================================
# Complete
# ============================================================
print("\n" + "=" * 70)
print("Abaqus Complete Workflow Test Finished!")
print("=" * 70)
print("Model file: %s" % os.path.join(workDir, 'BeamAnalysis.cae'))
print("Result file: %s" % odbPath)
print("Work directory: %s" % workDir)
print("=" * 70)
