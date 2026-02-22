# -*- coding: utf-8 -*-
"""
Abaqus full workflow - Python 2.7 compatible
"""
from abaqus import *
from abaqusConstants import *
from caeModules import *
from driverUtils import executeOnCaeStartup
import os

executeOnCaeStartup()

print("=" * 70)
print("Abaqus Full Workflow Test")
print("=" * 70)

# Work directory
workDir = r"C:\Users\openclaw\AbaqusTest"
if not os.path.exists(workDir):
    os.makedirs(workDir)
os.chdir(workDir)
print("Work directory: %s" % workDir)

# Step 1: Create model
print("\n" + "=" * 70)
print("Step 1: Create Model")

modelName = 'BeamModel'
if modelName in mdb.models.keys():
    del mdb.models[modelName]

myModel = mdb.Model(name=modelName)
print("Model created: %s" % modelName)

# Step 2: Create part (cantilever beam)
print("\n" + "=" * 70)
print("Step 2: Create Part")

sketch = myModel.ConstrainedSketch(name='__profile__', sheetSize=50.0)
sketch.rectangle(point1=(0.0, 0.0), point2=(10.0, 5.0))

myPart = myModel.Part(name='Beam', dimensionality=THREE_D, type=DEFORMABLE_BODY)
myPart.BaseSolidExtrude(sketch=sketch, depth=100.0)

print("Part created: Beam (100x10x5 mm)")
print("  Volume: %.2f mm3" % myPart.getVolume())

# Step 3: Create material
print("\n" + "=" * 70)
print("Step 3: Create Material")

steel = myModel.Material(name='Steel')
steel.Elastic(table=((210000.0, 0.3), ))
steel.Density(table=((7.8e-09, ), ))

print("Material created: Steel")
print("  E = 210000 MPa")
print("  nu = 0.3")

# Step 4: Create section
print("\n" + "=" * 70)
print("Step 4: Create Section")

mySection = myModel.HomogeneousSolidSection(name='BeamSection', material='Steel')
region = (myPart.cells,)
myPart.SectionAssignment(region=region, sectionName='BeamSection')

print("Section assigned")

# Step 5: Create assembly
print("\n" + "=" * 70)
print("Step 5: Create Assembly")

myAssembly = myModel.rootAssembly
myInstance = myAssembly.Instance(name='Beam-1', part=myPart, dependent=ON)

print("Assembly created")

# Step 6: Create step
print("\n" + "=" * 70)
print("Step 6: Create Analysis Step")

myModel.StaticStep(name='LoadStep', previous='Initial', 
                   description='Apply load to beam tip', nlgeom=OFF)

print("Step created: LoadStep")

# Step 7: Boundary condition (fixed end)
print("\n" + "=" * 70)
print("Step 7: Boundary Condition")

fixedFace = myInstance.faces.findAt(((5.0, 2.5, 0.0), ))
fixedRegion = myAssembly.Set(name='FixedEnd', faces=(fixedFace,))

myModel.DisplacementBC(name='Fixed', createStepName='Initial',
                       region=fixedRegion, u1=0.0, u2=0.0, u3=0.0)

print("BC created: Fixed at x=0")

# Step 8: Load (pressure at tip)
print("\n" + "=" * 70)
print("Step 8: Apply Load")

loadFace = myInstance.faces.findAt(((5.0, 5.0, 100.0), ))
loadSurface = myAssembly.Surface(name='LoadSurface', side1Faces=(loadFace,))

myModel.Pressure(name='TipLoad', createStepName='LoadStep',
                 region=loadSurface, magnitude=10.0)

print("Load created: 10.0 MPa at tip")

# Step 9: Mesh
print("\n" + "=" * 70)
print("Step 9: Mesh")

myPart.seedPart(size=5.0, deviationFactor=0.1, minSizeFactor=0.1)
myPart.generateMesh()

numElements = len(myPart.elements)
numNodes = len(myPart.nodes)

print("Mesh generated")
print("  Elements: %d" % numElements)
print("  Nodes: %d" % numNodes)

# Step 10: Create and submit job
print("\n" + "=" * 70)
print("Step 10: Create and Submit Job")

jobName = 'BeamJob'
if jobName in mdb.jobs.keys():
    del mdb.jobs[jobName]

myJob = mdb.Job(name=jobName, model=modelName, description='Beam analysis')

print("Job created: %s" % jobName)

# Save model
mdb.saveAs(pathName=os.path.join(workDir, 'BeamAnalysis.cae'))
print("Model saved")

# Submit job
print("Submitting job...")
myJob.submit()
myJob.waitForCompletion()
print("Job completed!")

# Step 11: Post-processing
print("\n" + "=" * 70)
print("Step 11: Post-processing")

odbPath = os.path.join(workDir, jobName + '.odb')
myOdb = session.openOdb(name=odbPath)

session.viewports['Viewport: 1'].setValues(displayedObject=myOdb)

lastStep = myOdb.steps['LoadStep']
lastFrame = lastStep.frames[-1]

# Get displacement
dispField = lastFrame.fieldOutputs['U']
dispValues = [v.magnitude for v in dispField.values]
maxDisp = max(dispValues)

print("Results extracted")
print("  Max displacement: %.4f mm" % maxDisp)

# Get stress
stressField = lastFrame.fieldOutputs['S']
stressValues = [v.mises for v in stressField.values]
maxStress = max(stressValues)

print("  Max Mises stress: %.2f MPa" % maxStress)

# Visualization
session.viewports['Viewport: 1'].odbDisplay.display.setValues(plotState=(DEFORMED,))
session.viewports['Viewport: 1'].odbDisplay.setPrimaryVariable(
    variableLabel='S',
    outputPosition=INTEGRATION_POINT,
    refinement=(COMPONENT, 'Mises')
)

print("  Visualization ready")

myOdb.close()

# Done
print("\n" + "=" * 70)
print("All steps completed!")
print("=" * 70)
print("Model: %s" % os.path.join(workDir, 'BeamAnalysis.cae'))
print("Results: %s" % odbPath)
print("=" * 70)
