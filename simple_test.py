
# 简单的 Abaqus 环境测试
from abaqus import *
from abaqusConstants import *

print("Abaqus Python 环境正常!")
print(f"模型列表: {list(mdb.models.keys())}")

# 创建简单模型
mdb.Model(name='SimpleTest')
print("成功创建 SimpleTest 模型")
mdb.saveAs('simple_test.cae')
print("保存成功!")
