# -*- coding: utf-8 -*-
"""
Abaqus Basic Test - Minimal
"""
from abaqus import *
from abaqusConstants import *
from caeModules import *
from driverUtils import executeOnCaeStartup
import os

executeOnCaeStartup()

print("=" * 70)
print("Abaqus Basic Test")
print("=" * 70)

# Work directory
workDir = r"C:\Users\openclaw\AbaqusTest"
if not os.path.exists(workDir):
    os.makedirs(workDir)
os.chdir(workDir)

# 1. Create Model
modelName = 'TestModel'
if modelName in mdb.models.keys():
    del mdb.models[modelName]
model = mdb.Model(name=modelName)
print("1. Created model: %s" % modelName)

# 2. Create Part
sketch = model.ConstrainedSketch(name='__profile__', sheetSize=200.0)
sketch.rectangle(point1=(0.0, 0.0), point2=(10.0, 10.0))
part = model.Part(name='Cube', dimensionality=THREE_D, type=DEFORMABLE_BODY)
part.BaseSolidExtrude(sketch=sketch, depth=10.0)
print("2. Created part: Cube")

# 3. Create Material
material = model.Material(name='Steel')
material.Elastic(table=((210000.0, 0.3), ))
print("3. Created material: Steel")

# 4. Create Section
section = model.HomogeneousSolidSection(name='Section-1', material='Steel')
part.SectionAssignment(region=(part.cells,), sectionName='Section-1')
print("4. Section assigned")

# 5. Create Assembly
assembly = model.rootAssembly
instance = assembly.Instance(name='Cube-1', part=part, dependent=ON)
print("5. Assembly created")

# 6. Save
mdb.saveAs(pathName=os.path.join(workDir, 'BasicTest.cae'))
print("6. Model saved")

print("\n" + "=" * 70)
print("SUCCESS! Abaqus automation is working!")
print("=" * 70)
