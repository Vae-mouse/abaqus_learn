# 3D打印混凝土Abaqus模型 (abaqus_3dpc)

参数化的3D打印混凝土（含钢筋网）Abaqus建模工具，支持打印过程模拟和力学测试分析。

## 功能特性

### 核心功能
- **几何建模**: 参数化分层梁结构，自动分层划分
- **钢筋网**: 双层钢筋网建模，支持embedded element约束
- **单元生消**: Model Change实现逐层打印模拟
- **层间接触**: Cohesive接触模拟层间粘结
- **网格划分**: 自动C3D8R混凝土网格和T3D2钢筋网格
- **后处理**: 自动提取应力、应变、位移结果

### 测试验证
- **本地测试**: Python语法和模块验证
- **远程测试**: SSH连接cao设备自动测试
- **最小化测试**: 核心功能快速验证

## 文件结构

```
abaqus_3dpc/
├── config.py          # 参数配置中心
├── materials.py       # 材料定义（混凝土、钢筋）
├── geometry.py        # 几何建模（梁、分层）
├── rebar.py          # 钢筋网生成
├── printing.py       # 打印过程设置
├── testing.py        # 力学测试设置
├── embedded.py       # Embedded element约束
├── element_birth.py  # 单元生消（Model Change）
├── meshing.py        # 网格划分
├── cohesive.py       # 层间Cohesive接触
├── postprocess.py    # 后处理结果提取
├── main.py           # 完整版主程序
├── minimal_test.py   # 最小化测试（推荐首次运行）
├── example.py        # 完整工作流示例
├── local_test.py     # 本地代码验证
├── remote_test.py    # 远程设备测试
├── TODO.md           # 项目进度跟踪
├── requirements.md   # 需求文档
└── architecture.md   # 架构设计
```

## 快速开始

### 1. 最小化测试（推荐）

在Abaqus CAE中运行：

```python
execfile(r'path/to/abaqus_3dpc/minimal_test.py')
```

这将创建一个简化的3DPC模型，验证核心功能：
- 材料创建
- 几何建模
- 分层划分
- 网格生成

### 2. 完整模型

```python
execfile(r'path/to/abaqus_3dpc/main.py')
```

### 3. 完整工作流示例

```python
execfile(r'path/to/abaqus_3dpc/example.py')
```

## 配置参数

在 `config.py` 中修改：

```python
# 几何参数
beam_length = 300.0      # 梁长度 (mm)
beam_width = 100.0       # 梁宽度 (mm)
beam_height = 50.0       # 梁高度 (mm)
layer_height = 10.0      # 打印层厚 (mm)

# 钢筋参数
rebar_diameter = 6.0     # 钢筋直径 (mm)
rebar_spacing = 50.0     # 钢筋间距 (mm)
rebar_cover = 15.0       # 保护层厚度 (mm)

# 材料参数
concrete_E = 30000.0     # 混凝土弹性模量 (MPa)
steel_E = 200000.0       # 钢筋弹性模量 (MPa)
```

## 技术要点

### Embedded Element约束
- 使用Abaqus的EmbeddedElement命令
- 将钢筋(truss单元)嵌入混凝土实体单元
- 自动处理节点约束关系

### Model Change单元生消
- 在Initial step中deactivate所有混凝土单元
- 每层打印创建一个PrintLayer分析步
- 使用Model Change interaction逐层激活单元

### 网格划分
- 混凝土: C3D8R单元（8节点六面体减缩积分）
- 钢筋: T3D2单元（2节点三维桁架）

## 远程测试

在WSL/Linux中运行：

```bash
cd abaqus_3dpc
python3 local_test.py    # 本地验证
python3 remote_test.py   # 远程测试（需SSH配置）
```

## 系统要求

- Abaqus 2021 或更高版本
- Python 2.7（Abaqus内置）
- Windows（cao设备）或WSL

## 开发状态

参见 `TODO.md` 了解当前开发进度。

## 许可证

本项目为学术研究用途开发。
