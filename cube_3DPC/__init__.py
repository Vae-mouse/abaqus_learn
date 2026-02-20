# 3D打印混凝土立方体抗压试验 - Python工作流
# 基于Abaqus 2021 + Python 2.7
# 项目目标：复现.inp文件结果，用于学习3DPC模拟

"""
项目结构说明：
cube_3DPC/
├── README.md                 # 项目说明
├── config.py                 # 参数配置（从.inp提取）
├── geometry.py               # 几何建模（立方体+压板）
├── materials.py              # 材料定义（混凝土+钢板）
├── assembly.py               # 装配体
├── interactions.py           # 接触关系
├── steps.py                  # 分析步设置
├── loads.py                  # 载荷和约束
├── job.py                    # 作业提交
├── verification.py           # 结果验证
├── main.py                   # 主程序入口
└── docs/
    ├── inp_analysis.md       # .inp文件分析
    └── paper_notes.md        # 文献笔记

开发日志：
- 2026-02-19: 项目初始化，等待.inp文件和文献
"""

__version__ = "0.1.0"
__author__ = "3DPC Learning Project"
