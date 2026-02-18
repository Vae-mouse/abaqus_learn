# -*- coding: utf-8 -*-
"""
Abaqus 测试脚本
在 Abaqus Python 环境中运行
"""
from abaqus import *
from abaqusConstants import *
from caeModules import *
import os

print("=" * 50)
print("Abaqus Python 环境测试")
print("=" * 50)

# 测试基本功能
try:
    print("Abaqus 版本信息")
    print("当前工作目录: %s" % os.getcwd())
    
    # 获取模型信息
    model_names = list(mdb.models.keys())
    print("现有模型: %s" % model_names)
    
    # 创建一个新模型
    if 'TestModel' in model_names:
        del mdb.models['TestModel']
    
    model = mdb.Model(name='TestModel')
    print("成功创建模型: TestModel")
    
    # 创建一个简单部件
    sketch = model.ConstrainedSketch(name='__profile__', sheetSize=200.0)
    sketch.rectangle(point1=(0.0, 0.0), point2=(10.0, 10.0))
    part = model.Part(name='Part-1', dimensionality=THREE_D, type=DEFORMABLE_BODY)
    part.BaseSolidExtrude(sketch=sketch, depth=10.0)
    print("成功创建部件: Part-1")
    
    # 创建材料
    material = model.Material(name='Steel')
    material.Elastic(table=((210000.0, 0.3), ))
    material.Density(table=((7.8e-09, ), ))
    print("成功创建材料: Steel")
    
    # 创建截面
    section = model.HomogeneousSolidSection(name='Section-1', material='Steel')
    print("成功创建截面: Section-1")
    
    # 指派截面
    region = (part.cells,)
    part.SectionAssignment(region=region, sectionName='Section-1')
    print("成功指派截面")
    
    # 保存模型
    mdb.saveAs(pathName='test_model.cae')
    print("模型已保存到: test_model.cae")
    
    print("\n" + "=" * 50)
    print("所有测试通过！")
    print("=" * 50)
    
except Exception as e:
    print("错误: %s" % str(e))
    import traceback
    traceback.print_exc()
    raise
