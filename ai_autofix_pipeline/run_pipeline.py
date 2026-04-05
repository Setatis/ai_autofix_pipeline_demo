"""运行 Pipeline 并保存输出"""
import subprocess
import sys
import os

os.chdir(r"d:\apply4sitp\ai_autofix_pipeline")

result = subprocess.run(
    [sys.executable, "demo_full_pipeline.py"],
    capture_output=True,
    text=True,
    encoding='utf-8',
    errors='replace',
    timeout=600
)

print(result.stdout)
if result.stderr:
    print("STDERR:", result.stderr)

# 保存到文件
with open("pipeline_output.txt", "w", encoding="utf-8") as f:
    f.write("=== STDOUT ===\n")
    f.write(result.stdout)
    f.write("\n=== STDERR ===\n")
    f.write(result.stderr)
    f.write(f"\n\nReturn code: {result.returncode}\n")

print(f"\n输出已保存到 pipeline_output.txt")
