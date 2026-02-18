# -*- coding: utf-8 -*-
"""
Abaqus Basic Workflow Test
"""
from abaqus import *
from abaqusConstants import *
from caeModules import *
from driverUtils import executeOnCaeStartup
import os

executeOnCaeStartup()

print("=" * 70)
print("Abaqus Basic Workflow Test")
print("=" * 70)

# Work directory
workDir = r"C:\Users\openclaw\AbaqusTest"
if not os.path.exists(workDir):
    os.makedirs(workDir)
os.chdir(workDir)
print("Work directory: %s" % workDir)

# 1. Create Model
print("\nStep 1: Create Model")
modelName = 'TestModel'
if modelName in mdb.models.keys():
    del mdb.models[modelName]
model = mdb.Model(name=modelName)
print("Created model: %s" % modelName)

# 2. Create Part
print("\nStep 2: Create Part")
sketch = model.ConstrainedSketch(name='__profile__', sheetSize=200.0)
sketch.rectangle(point1=(0.0, 0.0), point2=(10.0, 10.0))
part = model.Part(name='Cube', dimensionality=THREE_D, type=DEFORMABLE_BODY)
part.BaseSolidExtrude(sketch=sketch, depth=10.0)
print("Created part: Cube (10x10x10 mm)")

# 3. Create Material
print("\nStep 3: Create Material")
material = model.Material(name='Steel')
material.Elastic(table=((210000.0, 0.3), ))
material.Density(table=((7.8e-09, ), ))
print("Created material: Steel")

# 4. Create Section and Assign
print("\nStep 4: Create Section")
section = model.HomogeneousSolidSection(name='Section-1', material='Steel')
region = (part.cells,)
part.SectionAssignment(region=region, sectionName='Section-1')
print("Section assigned")

# 5. Create Assembly
print("\nStep 5: Create Assembly")
assembly = model.rootAssembly
instance = assembly.Instance(name='Cube-1', part=part, dependent=ON)
print("Created assembly instance")

# 6. Save Model
print("\nStep 6: Save Model")
mdb.saveAs(pathName=os.path.join(workDir, 'BasicTest.cae'))
print("Model saved to: %s" % os.path.join(workDir, 'BasicTest.cae'))

# 7. Create Job and Export
print("\nStep 7: Create Job")
jobName = 'BasicJob'
if jobName in mdb.jobs.keys():
    del mdb.jobs[jobName]
job = mdb.Job(name=jobName, model=modelName)
print("Created job: %s" % jobName)

# 8. Write Input File
print("\nStep 8: Write Input File")
job.writeInputFile()
print("INP file written")

print("\n" + "=" * 70)
print("Basic workflow test completed successfully!")
print("=" * 70)
