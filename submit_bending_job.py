# -*- coding: utf-8 -*-
"""
Submit bending test job and monitor progress.
"""

from abaqus import *
from abaqusConstants import *
from caeModules import *
from driverUtils import executeOnCaeStartup
import os

executeOnCaeStartup()

print("=" * 70)
print("Submit Bending Test Job")
print("=" * 70)

# Open model
work_dir = r"C:\Users\openclaw\BendingTest"
os.chdir(work_dir)

mdb.openAuxMdb(pathName=os.path.join(work_dir, 'BendingTest.cae'))
mdb.openAuxMdb(pathName=os.path.join(work_dir, 'BendingTest.cae'))

# Get model
model = mdb.models['BendingTest']

# Create and submit job
job_name = 'BendingTest_C30_Q235_Run'
if job_name in mdb.jobs.keys():
    del mdb.jobs[job_name]

job = mdb.Job(
    name=job_name,
    model='BendingTest',
    description='3DPC beam three-point bending test - C30 Q235',
    type=ANALYSIS,
    numCpus=4,
    numDomains=4,
    parallelizationMethodExplicit=DOMAIN
)

print("\nJob created: %s" % job_name)
print("Submitting...")

# Submit job
job.submit()

print("Job submitted successfully!")
print("Monitor with: abq2021 job=%s monitor" % job_name)

# Wait for completion (optional - comment out if not needed)
# print("\nWaiting for completion...")
# job.waitForCompletion()
# print("Job completed!")
