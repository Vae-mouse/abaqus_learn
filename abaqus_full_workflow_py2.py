# -*- coding: utf-8 -*-
"""
Abaqus 完整工作流程测试脚本 (Python 2.7兼容版)
包含：建模 -> 材料 -> 装配 -> 分析步 -> 载荷 -> 网格 -> 计算 -> 后处理
"""
from abaqus import *
from abaqusConstants import *
from caeModules import *
from driverUtils import executeOnCaeStartup
import os

# 执行 CAE 启动时的标准操作
executeOnCaeStartup()

print("=" * 70)
print("Abaqus 完整工作流程自动化测试")
print("=" * 70)

# 工作目录
workDir = r"C:\Users\openclaw\AbaqusTest"
if not os.path.exists(workDir):
    os.makedirs(workDir)
os.chdir(workDir)
print("工作目录: %s" % workDir)

# ============================================================
# 1. 创建模型
# ============================================================
print("\n" + "=" * 70)
print("步骤 1: 创建模型")

modelName = 'BeamModel'
if modelName in mdb.models.keys():
    del mdb.models[modelName]
    print("  删除已有模型: %s" % modelName)

myModel = mdb.Model(name=modelName)
print("模型创建成功: %s" % modelName)

# ============================================================
# 2. 创建部件 (悬臂梁)
# ============================================================
print("\n" + "=" * 70)
print("步骤 2: 创建部件")

# 创建草图
sketch = myModel.ConstrainedSketch(name='__profile__', sheetSize=50.0)
sketch.rectangle(point1=(0.0, 0.0), point2=(10.0, 5.0))

# 创建三维部件
myPart = myModel.Part(name='Beam', dimensionality=THREE_D, type=DEFORMABLE_BODY)
myPart.BaseSolidExtrude(sketch=sketch, depth=100.0)

print("部件创建成功: Beam (100x10x5 mm)")
print("  - 体积: %.2f mm3" % myPart.getVolume())

# ============================================================
# 3. 创建材料
# ============================================================
print("\n" + "=" * 70)
print("步骤 3: 创建材料")

# 钢材
steel = myModel.Material(name='Steel')
steel.Elastic(table=((210000.0, 0.3), ))  # E=210GPa, nu=0.3
steel.Density(table=((7.8e-09, ), ))  # rho=7.8e-9 tonne/mm3

print("材料创建成功: Steel")
print("  - 弹性模量: 210000 MPa")
print("  - 泊松比: 0.3")

# ============================================================
# 4. 创建截面并分配
# ============================================================
print("\n" + "=" * 70)
print("步骤 4: 创建截面")

mySection = myModel.HomogeneousSolidSection(
    name='BeamSection',
    material='Steel'
)

# 选择整个部件
region = (myPart.cells,)
myPart.SectionAssignment(region=region, sectionName='BeamSection')

print("截面分配成功")

# ============================================================
# 5. 创建装配体
# ============================================================
print("\n" + "=" * 70)
print("步骤 5: 创建装配体")

myAssembly = myModel.rootAssembly
myInstance = myAssembly.Instance(name='Beam-1', part=myPart, dependent=ON)

print("装配体创建成功")

# ============================================================
# 6. 创建分析步
# ============================================================
print("\n" + "=" * 70)
print("步骤 6: 创建分析步")

myModel.StaticStep(
    name='LoadStep',
    previous='Initial',
    description='Apply load to beam tip',
    nlgeom=OFF
)

print("分析步创建成功: LoadStep")

# ============================================================
# 7. 定义边界条件 (固定端)
# ============================================================
print("\n" + "=" * 70)
print("步骤 7: 定义边界条件")

# 固定端面 (x=0)
fixedFace = myInstance.faces.findAt(((5.0, 2.5, 0.0), ))
fixedRegion = myAssembly.Set(name='FixedEnd', faces=(fixedFace,))

myModel.DisplacementBC(
    name='Fixed',
    createStepName='Initial',
    region=fixedRegion,
    u1=0.0, u2=0.0, u3=0.0
)

print("边界条件定义成功")
print("  - 固定端: x=0 面")

# ============================================================
# 8. 定义载荷 (端部压力)
# ============================================================
print("\n" + "=" * 70)
print("步骤 8: 定义载荷")

# 加载面 (x=100, y=5)
loadFace = myInstance.faces.findAt(((5.0, 5.0, 100.0), ))
loadSurface = myAssembly.Surface(name='LoadSurface', side1Faces=(loadFace,))

myModel.Pressure(
    name='TipLoad',
    createStepName='LoadStep',
    region=loadSurface,
    magnitude=10.0  # 10 MPa
)

print("载荷定义成功")
print("  - 类型: 压力")
print("  - 大小: 10.0 MPa")
print("  - 位置: 自由端上表面")

# ============================================================
# 9. 划分网格
# ============================================================
print("\n" + "=" * 70)
print("步骤 9: 划分网格")

# 设置种子
myPart.seedPart(size=5.0, deviationFactor=0.1, minSizeFactor=0.1)

# 生成网格
myPart.generateMesh()

# 获取网格信息
numElements = len(myPart.elements)
numNodes = len(myPart.nodes)

print("网格划分成功")
print("  - 单元数: %d" % numElements)
print("  - 节点数: %d" % numNodes)
print("  - 单元类型: C3D8R")
print("  - 种子大小: 5.0 mm")

# ============================================================
# 10. 创建并提交作业
# ============================================================
print("\n" + "=" * 70)
print("步骤 10: 创建并提交作业")

jobName = 'BeamJob'
if jobName in mdb.jobs.keys():
    del mdb.jobs[jobName]

myJob = mdb.Job(name=jobName, model=modelName, description='Beam analysis')

print("作业创建成功: %s" % jobName)

# 保存模型
mdb.saveAs(pathName=os.path.join(workDir, 'BeamAnalysis.cae'))
print("模型已保存")

# 提交作业
print("正在提交作业...")
myJob.submit()
myJob.waitForCompletion()
print("作业完成！")

# ============================================================
# 11. 后处理
# ============================================================
print("\n" + "=" * 70)
print("步骤 11: 后处理")

# 打开结果文件
odbPath = os.path.join(workDir, jobName + '.odb')
myOdb = session.openOdb(name=odbPath)

# 显示在视口
session.viewports['Viewport: 1'].setValues(displayedObject=myOdb)

# 获取最后一步
lastStep = myOdb.steps['LoadStep']
lastFrame = lastStep.frames[-1]

# 提取位移
dispField = lastFrame.fieldOutputs['U']
dispValues = [v.magnitude for v in dispField.values]
maxDisp = max(dispValues)

print("结果提取成功")
print("  - 最大位移: %.4f mm" % maxDisp)

# 提取应力
stressField = lastFrame.fieldOutputs['S']
stressValues = [v.mises for v in stressField.values]
maxStress = max(stressValues)

print("  - 最大Mises应力: %.2f MPa" % maxStress)

# 设置可视化
session.viewports['Viewport: 1'].odbDisplay.display.setValues(plotState=(DEFORMED,))
session.viewports['Viewport: 1'].odbDisplay.setPrimaryVariable(
    variableLabel='S',
    outputPosition=INTEGRATION_POINT,
    refinement=(COMPONENT, 'Mises')
)

print("  - 可视化设置完成")

# 关闭ODB
myOdb.close()

# ============================================================
# 完成
# ============================================================
print("\n" + "=" * 70)
print("所有步骤完成！")
print("=" * 70)
print("模型文件: %s" % os.path.join(workDir, 'BeamAnalysis.cae'))
print("结果文件: %s" % odbPath)
print("=" * 70)
