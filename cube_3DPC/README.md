# 3D打印混凝土立方体抗压试验

## 项目目标
复现参考文献中的立方体抗压试验仿真结果，建立可学习的Python工作流。

## 环境要求
- Abaqus 2021
- Python 2.7（Abaqus内置）
- Windows操作系统

## 使用方法

### 1. 完整运行
```bash
# 在Abaqus CAE中
execfile('main.py')
```

### 2. 分步运行
```python
# 在Abaqus CAE Python控制台
execfile('config.py')      # 加载配置
execfile('geometry.py')    # 创建几何
execfile('materials.py')   # 定义材料
# ... 依此类推
```

## 文件说明

| 文件 | 功能 | 对应.inp关键字 |
|------|------|---------------|
| config.py | 参数配置 | *Parameter |
| geometry.py | 几何建模 | *Node, *Element |
| materials.py | 材料定义 | *Material |
| assembly.py | 装配 | *Instance |
| interactions.py | 接触 | *Contact |
| steps.py | 分析步 | *Step |
| loads.py | 载荷约束 | *Boundary, *Load |
| job.py | 作业提交 | *Job |

## 验证方法
运行verification.py对比.inp和.py的结果差异。

## 参考文献
（等待上传）

## 开发状态
- [ ] 接收.inp文件和文献
- [ ] 解析.inp文件结构
- [ ] 提取关键参数
- [ ] 编写Python工作流
- [ ] 验证结果一致性
- [ ] 编写学习文档
