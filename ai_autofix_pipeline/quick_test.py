"""简单测试检查"""
import sys
sys.path.insert(0, "test_app")
from calculator import Calculator

calc = Calculator()

# 测试 1: 除零
print("=" * 40)
print("测试除零:")
try:
    calc.divide(10, 0)
    print("  [FAIL] 没有抛出异常")
except ValueError as e:
    print(f"  [OK] 抛出 ValueError: {e}")
except ZeroDivisionError as e:
    print(f"  [BUG] 抛出 ZeroDivisionError: {e}")

# 测试 2: 字符串幂运算
print("\n测试字符串幂运算:")
try:
    calc.power("2", 3)
    print("  [FAIL] 没有抛出异常")
except ValueError as e:
    print(f"  [OK] 抛出 ValueError: {e}")
except TypeError as e:
    print(f"  [BUG] 抛出 TypeError: {e}")

# 测试 3: 空列表平均值
print("\n测试空列表平均值:")
try:
    result = calc.average([])
    print(f"  [BUG] 返回了值: {result}")
except ValueError as e:
    print(f"  [OK] 抛出 ValueError: {e}")
except ZeroDivisionError as e:
    print(f"  [BUG] 抛出 ZeroDivisionError: {e}")

# 测试 4: 字符串输入验证
print("\n测试字符串输入验证:")
try:
    calc.validate_input("not a number")
    print("  [FAIL] 没有抛出异常")
except ValueError as e:
    print(f"  [OK] 抛出 ValueError: {e}")

print("\n" + "=" * 40)
print("总结: AI已修复 average 和 validate_input")
print("      divide 和 power 仍需修复")
