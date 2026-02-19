# 🎓 3DPC项目 - 小白上手指南

## 🎯 前言：写给初学者的你

你好！这个项目看起来代码很多，但别担心。我会用最简单的方式教你上手。

**核心思想**：就像玩乐高积木，我们有很多小零件（模块），按顺序拼起来就是一个完整的模型。

---

## 📚 第一课：项目是什么？

### 简单理解
这是一个**自动生成Abaqus模型的工具**。

你告诉它：
- "我要一个300mm长、100mm宽、50mm高的梁"
- "用C30混凝土"
- "加钢筋"
- "分5层打印"

它自动帮你：
- 画几何图形
- 定义材料
- 放钢筋
- 分网格
- 保存成.cae文件

### 三种使用方式

| 方式 | 难度 | 适合谁 |
|------|------|--------|
| GUI界面 | ⭐ 最简单 | 第一次用，喜欢点点点 |
| CLI命令行 | ⭐⭐ 中等 | 要批量处理，写脚本 |
| Python代码 | ⭐⭐⭐ 高级 | 要深度定制，改功能 |

---

## 🖱️ 第二课：GUI方式（推荐初学者）

### 步骤1：打开界面
```bash
# 在cao设备上执行
python C:\Users\openclaw\abaqus_3dpc\gui.py
```

### 步骤2：填写参数
你会看到几个输入框：

```
梁长度: [300] mm  ← 改成你要的长度
梁宽度: [100] mm  ← 改成你要的宽度
梁高度: [50]  mm  ← 改成你要的高度
层厚度: [10]  mm  ← 每层多厚

钢筋直径: [6]  mm  ← 钢筋多粗
钢筋间距: [50] mm  ← 钢筋多远一根
保护层:   [15] mm  ← 钢筋离表面多远
```

### 步骤3：点击生成
点【Generate Model】按钮，等待完成。

### 步骤4：查看结果
生成的文件在：
```
C:\Users\openclaw\Abaqus3DPC_Complete\
└── 3DPC_Complete.cae  ← 这个文件就是模型
```

用Abaqus CAE打开它，就能看到你的模型了！

---

## ⌨️ 第三课：CLI方式（进阶）

### 最简单的命令
```bash
python cli.py --length 300 --width 100 --height 50
```

### 常用参数解释
```bash
python cli.py \
    --length 400 \           # 梁长400mm
    --width 150 \            # 梁宽150mm
    --height 60 \            # 梁高60mm
    --layer-height 12 \      # 每层12mm
    --rebar-diameter 8 \     # 钢筋直径8mm
    --analysis static        # 静力分析
```

### 所有可用参数
```bash
# 几何参数
--length          # 梁长度 (mm)
--width           # 梁宽度 (mm)
--height          # 梁高度 (mm)
--layer-height    # 层厚度 (mm)

# 钢筋参数
--rebar-diameter  # 钢筋直径 (mm)
--rebar-spacing   # 钢筋间距 (mm)
--rebar-cover     # 保护层厚度 (mm)
--no-rebar        # 不加钢筋

# 材料参数
--concrete-E      # 混凝土弹性模量 (MPa)
--concrete-strength # 混凝土强度 (MPa)
--steel-E         # 钢筋弹性模量 (MPa)

# 分析类型
--analysis static   # 静力分析
--analysis thermal  # 热-力耦合
--analysis damage   # 损伤分析

# 其他选项
--cohesive        # 添加层间接触
--element-birth   # 添加打印模拟
--mesh-size       # 网格大小 (mm)

# 输出选项
--name            # 模型名称
--output-dir      # 输出目录
--create-job      # 自动创建作业
```

---

## 🐍 第四课：Python代码方式（高级）

### 最简单的脚本
```python
# my_first_model.py
from config import Config
from geometry import create_concrete_beam
from materials import create_concrete_material

# 1. 创建配置
config = Config()
config.beam_length = 300.0  # 300mm长
config.beam_height = 50.0   # 50mm高

# 2. 创建模型
from abaqus import *
model = mdb.Model(name='MyFirstModel')

# 3. 创建材料
mat = create_concrete_material(model, config)

# 4. 创建几何
beam = create_concrete_beam(model, config)

# 5. 保存
mdb.saveAs('MyFirstModel.cae')
print("模型创建成功！")
```

### 运行方式
在Abaqus CAE的Python控制台：
```python
execfile(r'C:\Users\openclaw\abaqus_3dpc\my_first_model.py')
```

---

## 🔧 第五课：调试技巧

### 技巧1：从简单开始
```bash
# 先跑最简单的，确认环境正常
python minimal_test.py

# 如果成功，会看到：
# ✅ Model created successfully!
```

### 技巧2：看错误信息
```
错误：AttributeError: 'Part' object has no attribute 'ConstrainedSketch'
意思：Part对象没有ConstrainedSketch方法
解决：检查Abaqus版本，或用其他方法
```

### 技巧3：加打印语句
```python
# 在代码中加print，看执行到哪一步
print("步骤1：创建配置")
config = Config()

print("步骤2：创建模型")
model = mdb.Model(name='Test')

print("步骤3：创建几何")
beam = create_concrete_beam(model, config)

print("完成！")
```

### 技巧4：分段测试
```python
# 先测试配置
from config import Config
c = Config()
print(c.beam_length)  # 应该输出300.0

# 再测试几何
from geometry import create_concrete_beam
beam = create_concrete_beam(model, c)
print("几何创建成功")

# 一步步来，不要一次性跑完
```

---

## 📝 第六课：常见问题FAQ

### Q1: 报错"No module named abaqus"
**原因**：你用普通Python运行，而不是Abaqus的Python
**解决**：
```bash
# 错误
python main_complete.py

# 正确
abq2021 cae noGUI=main_complete.py
```

### Q2: 模型生成后怎么打开？
**方法**：
1. 打开Abaqus CAE
2. File → Open
3. 选择生成的.cae文件

### Q3: 怎么改材料强度？
**方法**：编辑`config.py`
```python
# C30混凝土
self.concrete_E = 30000.0  # 30GPa

# 改成C40
self.concrete_E = 40000.0  # 40GPa
```

### Q4: 怎么加自己的载荷？
**方法**：在main_complete.py后面加：
```python
# 创建集中力
model.ConcentratedForce(
    name='MyLoad',
    createStepName='StaticStep',
    region=某个面,
    cf2=-1000.0  # 向下1000N
)
```

### Q5: 怎么知道有哪些函数可用？
**方法**：看每个模块的`__doc__`字符串
```python
import geometry
help(geometry.create_concrete_beam)
# 会显示函数的说明
```

---

## 🎓 第七课：学习路径建议

### 第1天：熟悉环境
- [ ] 运行minimal_test.py，确认能生成模型
- [ ] 用GUI界面生成一个模型
- [ ] 在Abaqus CAE中打开查看

### 第2天：理解参数
- [ ] 修改config.py中的尺寸
- [ ] 重新生成，观察变化
- [ ] 理解每个参数的含义

### 第3天：尝试CLI
- [ ] 用命令行生成模型
- [ ] 尝试不同的参数组合
- [ ] 写一个批处理脚本

### 第4天：阅读代码
- [ ] 看geometry.py，理解怎么建梁
- [ ] 看materials.py，理解材料定义
- [ ] 看rebar.py，理解钢筋怎么放

### 第5天：尝试修改
- [ ] 改一个参数，看效果
- [ ] 添加一个简单的载荷
- [ ] 保存并运行

### 第6-7天：进阶功能
- [ ] 尝试热-力耦合分析
- [ ] 尝试参数化扫描
- [ ] 写自己的分析脚本

---

## 📞 第八课：获取帮助

### 1. 看文档
- `README.md` - 项目说明
- `QUICKSTART.md` - 快速开始
- `TODO.md` - 开发日志

### 2. 看代码注释
每个函数都有docstring，说明：
- 这个函数是干嘛的
- 需要什么参数
- 返回什么结果

### 3. 运行测试
```bash
python local_test.py  # 本地测试
python test_thermal.py  # 热耦合测试
```

### 4. 问问题
记住这几个关键信息：
- 你在用什么方式？（GUI/CLI/代码）
- 报错信息是什么？
- 你想做什么？

---

## 🎉 总结

**你已经学会了：**
1. ✅ 项目是什么
2. ✅ 三种使用方式
3. ✅ 基本操作流程
4. ✅ 调试技巧
5. ✅ 常见问题解决

**下一步：**
- 动手实践！从GUI开始
- 遇到问题不要怕，看错误信息
- 多试几次就熟练了

**加油！你可以的！** 💪

---

*有问题随时问，我会继续帮你！* 🤖
