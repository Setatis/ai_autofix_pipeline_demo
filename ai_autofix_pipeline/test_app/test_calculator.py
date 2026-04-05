"""
计算器测试用例 - 包含一个预设Bug用于演示
"""
import pytest
from calculator import Calculator


class TestCalculator:
    """计算器测试类"""
    
    def setup_method(self):
        self.calc = Calculator()
    
    def test_add(self):
        """测试加法 - 应该通过"""
        assert self.calc.add(2, 3) == 5
        assert self.calc.add(-1, 1) == 0
    
    def test_subtract(self):
        """测试减法 - 应该通过"""
        assert self.calc.subtract(5, 3) == 2
    
    def test_multiply(self):
        """测试乘法 - 应该通过"""
        assert self.calc.multiply(3, 4) == 12
    
    def test_divide_by_zero(self):
        """测试除零错误 - Bug: 应该抛出 ValueError"""
        # 期望抛出 ValueError，但现在会抛出 ZeroDivisionError
        with pytest.raises(ValueError):
            self.calc.divide(10, 0)
    
    def test_divide_normal(self):
        """测试正常除法 - 应该通过"""
        assert self.calc.divide(10, 2) == 5.0
    
    def test_power_with_string(self):
        """测试幂运算字符串输入 - 应该通过（字符串会被转换）"""
        # 计算器应该能处理字符串数字
        result = self.calc.power("2", 3)
        assert result == 8.0
    
    def test_power_normal(self):
        """测试正常幂运算 - 应该通过"""
        assert self.calc.power(2, 3) == 8
    
    def test_average_precision(self):
        """测试平均值精度 - 应该通过"""
        result = self.calc.average([1, 2, 3])
        assert abs(result - 2.0) < 1e-10
    
    def test_average_empty_list(self):
        """测试空列表平均值 - 应该通过（返回0）"""
        result = self.calc.average([])
        assert result == 0
    
    def test_validate_input_string(self):
        """测试输入验证字符串 - 应该通过（会抛出异常）"""
        with pytest.raises((ValueError, TypeError)):
            self.calc.validate_input("not a number")
    
    def test_validate_input_none(self):
        """测试输入验证None - 应该通过"""
        with pytest.raises(ValueError):
            self.calc.validate_input(None)
