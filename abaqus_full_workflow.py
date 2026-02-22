# -*- coding: utf-8 -*-
"""
Abaqus 完整工作流程测试脚本
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
print("=" * 70)

modelName = 'TestModel'
if modelName in mdb.models.keys():
    del mdb.models[modelName]

model = mdb.Model(name=modelName)
print("✓ 创建模型: %s" % modelName)

# ============================================================
# 2. 创建部件 (悬臂梁)
# ============================================================
print("\n" + "=" * 70)
print("步骤 2: 创建部件 - 悬臂梁")
print("=" * 70)

# 创建草图
sketch = model.ConstrainedSketch(name='__profile__', sheetSize=200.0)
sketch.rectangle(point1=(0.0, 0.0), point2=(100.0, 10.0))

# 创建三维部件
part = model.Part(name='Beam', dimensionality=THREE_D, type=DEFORMABLE_BODY)
part.BaseSolidExtrude(sketch=sketch, depth=5.0)

print("✓ 创建部件: Beam (100x10x5 mm)")
print("  - 体积: %s mm³" % part.getVolume():.2f)

# ============================================================
# 3. 创建材料
# ============================================================
print("\n" + "=" * 70)
print("步骤 3: 创建材料")
print("=" * 70)

material = model.Material(name='Steel')
material.Elastic(table=((210000.0, 0.3), ))  # 弹性模量 210 GPa, 泊松比 0.3
material.Density(table=((7.8e-09, ), ))  # 密度 7.8 g/cm³

print("✓ 创建材料: Steel")
print("  - 弹性模量: 210 GPa")
print("  - 泊松比: 0.3")
print("  - 密度: 7.8 g/cm³")

# ============================================================
# 4. 创建截面并指派
# ============================================================
print("\n" + "=" * 70)
print("步骤 4: 创建截面并指派")
print("=" * 70)

section = model.HomogeneousSolidSection(name='BeamSection', material='Steel')
region = (part.cells,)
part.SectionAssignment(region=region, sectionName='BeamSection')

print("✓ 创建截面: BeamSection")
print("✓ 截面指派完成")

# ============================================================
# 5. 创建装配
# ============================================================
print("\n" + "=" * 70)
print("步骤 5: 创建装配")
print("=" * 70)

assembly = model.rootAssembly
instance = assembly.Instance(name='Beam-1', part=part, dependent=ON)

print("✓ 创建装配实例: Beam-1")

# ============================================================
# 6. 创建分析步
# ============================================================
print("\n" + "=" * 70)
print("步骤 6: 创建分析步")
print("=" * 70)

# 创建静力分析步
step = model.StaticStep(name='ApplyLoad', previous='Initial', 
                        description='Apply tip load',
                        timePeriod=1.0, nlgeom=OFF)

print("✓ 创建分析步: ApplyLoad")
print("  - 类型: 静力分析")
print("  - 时间周期: 1.0")

# ============================================================
# 7. 创建边界条件 (固定端)
# ============================================================
print("\n" + "=" * 70)
print("步骤 7: 创建边界条件")
print("=" * 70)

# 选择固定端面 (x=0)
faces = instance.faces
fixedFace = faces.findAt(((0.0, 5.0, 2.5), ))
region = assembly.Set(name='FixedEnd', faces=(fixedFace,))

# 创建固定边界条件
bc = model.DisplacementBC(name='Fixed', createStepName='Initial', 
                          region=region, u1=0.0, u2=0.0, u3=0.0,
                          ur1=0.0, ur2=0.0, ur3=0.0)

print("✓ 创建边界条件: Fixed (固定端)")

# ============================================================
# 8. 创建载荷 (自由端集中力)
# ============================================================
print("\n" + "=" * 70)
print("步骤 8: 创建载荷")
print("=" * 70)

# 选择自由端面 (x=100)
loadFace = faces.findAt(((100.0, 5.0, 2.5), ))
region = assembly.Set(name='LoadEnd', faces=(loadFace,))

# 创建集中力 (向下 -Y 方向)
load = model.ConcentratedForce(name='TipLoad', createStepName='ApplyLoad',
                               region=region, cf2=-1000.0)  # 1000 N 向下

print("✓ 创建载荷: TipLoad")
print("  - 大小: 1000 N")
print("  - 方向: -Y (向下)")

# ============================================================
# 9. 划分网格
# ============================================================
print("\n" + "=" * 70)
print("步骤 9: 划分网格")
print("=" * 70)

# 设置网格控制
cells = part.cells
region = (cells,)
part.setMeshControls(regions=region, elemShape=HEX, technique=STRUCTURED)

# 设置单元类型
elemType = mesh.ElemType(elemCode=C3D8R, elemLibrary=STANDARD)
part.setElementType(regions=region, elemTypes=(elemType,))

# 设置种子
part.seedPart(size=5.0, deviationFactor=0.1, minSizeFactor=0.1)

# 生成网格
part.generateMesh()

print("✓ 网格划分完成")
print("  - 单元类型: C3D8R (8节点六面体减缩积分)")
print("  - 种子大小: 5.0 mm")

# ============================================================
# 10. 创建作业并提交计算
# ============================================================
print("\n" + "=" * 70)
print("步骤 10: 创建作业并提交计算")
print("=" * 70)

jobName = 'BeamAnalysis'
if jobName in mdb.jobs.keys():
    del mdb.jobs[jobName]

job = mdb.Job(name=jobName, model=modelName, 
              description='Cantilever beam analysis')

print("✓ 创建作业: %s" % jobName)

# 保存模型
mdb.saveAs(pathName=os.path.join(workDir, 'BeamAnalysis.cae'))
print("✓ 模型已保存")

# 提交作业
print("\n提交计算...")
job.submit()
job.waitForCompletion()

print("✓ 计算完成!")

# ============================================================
# 11. 后处理
# ============================================================
print("\n" + "=" * 70)
print("步骤 11: 后处理")
print("=" * 70)

# 打开结果文件
odbPath = os.path.join(workDir, f'{jobName}.odb')
odb = session.openOdb(name=odbPath)

# 创建变形图
session.viewports['Viewport: 1'].setValues(displayedObject=odb)

# 获取最大位移
lastFrame = odb.steps['ApplyLoad'].frames[-1]
displacement = lastFrame.fieldOutputs['U']
maxDisp = max([value.magnitude for value in displacement.values])

print("✓ 最大位移: %s mm" % maxDisp:.4f)

# 获取最大应力
stress = lastFrame.fieldOutputs['S']
maxStress = max([value.maxPrincipal for value in stress.values])

print("✓ 最大主应力: %s MPa" % maxStress:.2f)

# 保存结果
session.printToFile(fileName=os.path.join(workDir, 'Deformation'), 
                    format=PNG, canvasObjects=(session.viewports['Viewport: 1'], ))

print("✓ 结果图像已保存")

# 关闭 ODB
odb.close()

# ============================================================
# 完成
# ============================================================
print("\n" + "=" * 70)
print("Abaqus 完整工作流程测试完成!")
print("=" * 70)
print("模型文件: %s" % os.path.join(workDir, 'BeamAnalysis.cae'))
print("结果文件: %s" % odbPath)
print("工作目录: %s" % workDir)
print("=" * 70)
