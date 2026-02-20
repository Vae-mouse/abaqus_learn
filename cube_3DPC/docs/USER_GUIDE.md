# 3D打印混凝土立方体抗压试验 - 使用指南

## 快速开始

### 1. 环境要求
- Abaqus 2021
- Python 2.7（Abaqus内置）
- Windows操作系统

### 2. 文件结构
```
cube_3DPC/
├── config.py           # 参数配置
├── geometry.py         # 几何建模
├── materials.py        # 材料定义
├── mesh.py             # 网格划分
├── assembly.py         # 装配约束
├── steps_loads.py      # 分析步和载荷
├── main.py             # 主程序
├── run_abaqus.py       # UV运行脚本
├── cube_compression.inp # 参考INP文件
└── docs/
    └── inp_analysis.md  # INP分析报告
```

### 3. 运行方式

#### 方式1: UV终端运行（推荐）
```bash
# 进入项目目录
cd /path/to/cube_3DPC

# 运行建模脚本（打开CAE GUI）
uv run python run_abaqus.py

# 无GUI模式运行
uv run python run_abaqus.py --no-gui

# 建模并自动提交作业
uv run python run_abaqus.py --submit

# 仅提交已有作业
uv run python run_abaqus.py --job-only
```

#### 方式2: Abaqus CAE中运行
```python
# 在Abaqus CAE的Python控制台
execfile(r'path/to/cube_3DPC/main.py')
```

#### 方式3: 命令行直接运行
```bash
# 打开CAE并运行脚本
abq2021 cae script=main.py

# 无GUI模式
abq2021 cae noGUI=main.py
```

### 4. 学习路径

#### 第1步：理解INP文件
阅读 `docs/inp_analysis.md`，了解：
- 模型结构（6层混凝土）
- 材料模型（CDP+Cohesive）
- 约束关系（Tie+Rigid Body）
- 加载方式（位移控制）

#### 第2步：阅读Python代码
按顺序阅读：
1. `config.py` - 所有参数定义
2. `geometry.py` - 如何创建立方体
3. `materials.py` - CDP和Cohesive材料
4. `mesh.py` - 网格划分
5. `assembly.py` - 装配和约束
6. `steps_loads.py` - 分析步和加载
7. `main.py` - 完整流程

#### 第3步：运行和验证
1. 运行 `main.py` 创建模型
2. 对比生成的.cae文件与.inp文件
3. 检查几何、材料、约束是否一致
4. 提交计算并验证结果

#### 第4步：修改和实验
基于现有代码进行修改：
- 修改 `config.py` 中的参数
- 尝试不同的材料属性
- 改变加载条件
- 添加新的输出变量

### 5. 关键参数说明

#### 几何参数（config.py）
```python
cube_length_x = 360.0    # X方向长度 (mm)
cube_length_y = 90.0     # Y方向高度 (mm，6层，每层15mm)
cube_length_z = 60.0     # Z方向宽度 (mm)
num_layers = 6           # 层数
layer_thickness = 15.0   # 层厚 (mm)
```

#### CDP材料参数
```python
concrete_E = 30000.0     # 弹性模量 (MPa)
concrete_nu = 0.2        # 泊松比
cdp_dilation_angle = 38.0    # 膨胀角 (度)

# 压缩硬化曲线 (应力, 应变)
concrete_comp_hardening = [
    (20.0, 0.0),
    (30.0, 0.001),
    (35.0, 0.002),
]
```

#### Cohesive粘结参数
```python
cohesive_Enn = 10000.0   # 法向刚度 (MPa)
cohesive_GIc = 0.1       # I型断裂能 (mJ/mm2)
cohesive_GIIc = 0.5      # II型断裂能 (mJ/mm2)
```

### 6. 常见问题

#### Q: 运行时报错"ImportError: No module named abaqus"
A: 必须在Abaqus CAE环境中运行，不能用普通Python

#### Q: 中文注释导致编码错误
A: 所有.py文件已使用UTF-8编码，如有问题请删除中文注释

#### Q: 如何修改材料参数？
A: 编辑 `config.py` 中的对应参数，然后重新运行

#### Q: 如何验证结果与.inp一致？
A: 对比节点坐标、单元类型、材料参数、约束关系

### 7. 进阶学习

#### 添加自定义功能
在 `main.py` 的 `create_model()` 函数中添加：
```python
# 自定义载荷
model.ConcentratedForce(
    name='CustomLoad',
    createStepName='Step-1',
    region=...,
    cf2=-1000.0
)
```

#### 参数化研究
修改 `config.py` 并批量运行：
```python
# 在main.py中添加循环
for disp in [1, 2, 3, 4, 5]:
    config.displacement = disp
    model = create_model()
    # 保存不同版本
```

### 8. 参考资源

- Abaqus Documentation: Abaqus Scripting Reference Guide
- Abaqus Example Problems Manual
- 原始论文: （请补充文献信息）

---

**提示**: 本工作流专为学习设计，代码中有详细注释。建议逐行阅读理解，再尝试修改。
