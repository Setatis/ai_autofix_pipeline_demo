"""运行测试检查Bug"""
import subprocess
import sys

result = subprocess.run(
    [sys.executable, "-m", "pytest", "test_calculator.py", "-v"],
    capture_output=True,
    text=True,
    encoding='utf-8',
    errors='replace',
    cwd="test_app"
)

print("=" * 60)
print("测试输出:")
print("=" * 60)
print(result.stdout)
if result.stderr:
    print("错误:")
    print(result.stderr)
print("=" * 60)
print(f"返回码: {result.returncode}")
