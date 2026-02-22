import re

# 读取文件
with open('abaqus_full_workflow.py', 'r') as f:
    content = f.read()

# 替换 f-string 为 % 格式化
# 处理 f"...{var}..."
content = re.sub(r'print\(f"([^"]*)\{([^}]+)\}([^"]*)"\)', r'print("\1%s\3" % \2)', content)

# 写入文件
with open('abaqus_full_workflow.py', 'w') as f:
    f.write(content)

print("修复完成！")
