
# -*- coding: utf-8 -*-
"""
Abaqus 自动化操作脚本
在 Abaqus CAE 中执行
"""
from abaqus import *
from abaqusConstants import *
from caeModules import *
from driverUtils import executeOnCaeStartup
import os

# 执行 CAE 启动时的标准操作
executeOnCaeStartup()

print("=" * 60)
print("Abaqus 自动化操作")
print("=" * 60)

# 获取当前模型
if 'TestModel' in mdb.models.keys():
    model = mdb.models['TestModel']
    print("已加载模型: TestModel")
else:
    print("错误: 未找到 TestModel")
    raise ValueError("Model not found")

# 切换到 Part 模块并显示 Part-1
print("\n切换到 Part 模块...")
session.viewports['Viewport: 1'].setValues(displayedObject=model.parts['Part-1'])

# 设置视图方向
session.viewports['Viewport: 1'].view.setValues(
    session.views['Iso']
)
print("视图已设置为等轴测")

# 切换到 Property 模块显示材料
print("\n切换到 Property 模块...")
session.viewports['Viewport: 1'].setValues(displayedObject=model)

# 打印模型信息摘要
print("\n" + "=" * 60)
print("模型信息摘要")
print("=" * 60)
print(f"部件: {list(model.parts.keys())}")
print(f"材料: {list(model.materials.keys())}")
print(f"截面: {list(model.sections.keys())}")

# 保存模型
mdb.save()
print("\n模型已保存")

print("\n" + "=" * 60)
print("操作完成！请检查 Abaqus CAE 窗口")
print("=" * 60)
