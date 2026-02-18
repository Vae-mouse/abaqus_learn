# Abaqus 学习仓库

曹同学的 Abaqus 二次开发学习项目 🤖🏗️

## 环境配置

- **Abaqus 版本**: 2026
- **安装路径**: `D:\Program Files\SIMULIA\EstProducts\2026`
- **Python 环境**: uv + Python 3.10
- **核心库**: abqpy 2025.9

## 快速开始

```bash
# 安装依赖
uv sync

# 运行测试
uv run python test_abaqus_api.py
```

## 文件说明

| 文件 | 说明 |
|------|------|
| `test_abaqus_api.py` | Abaqus API 测试主脚本 |
| `test_abaqus_script.py` | Abaqus Python 脚本（在 Abaqus 环境中运行） |
| `test_model.cae` | 测试生成的 Abaqus 模型文件 |

## 开发说明

- 使用 `abqpy` 提供类型提示和自动补全
- 实际脚本需要在 Abaqus Python 环境中运行
- WSL 通过 PowerShell 调用 Windows Abaqus

---
*由 你蝶派来帮你的人工智障 维护*
