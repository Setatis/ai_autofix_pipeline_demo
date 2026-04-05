

"""
计算器应用 - Bug已修复
"""

class Calculator:
    """简单计算器类"""
    
    def add(self, a, b):
        """加法"""
        return a + b
    
    def subtract(self, a, b):
        """减法"""
        return a - b
    
    def multiply(self, a, b):
        """乘法"""
        return a * b
    
    def divide(self, a, b):
        """
        除法 - 已修复除零Bug并添加输入验证
        """
        # 修复: 添加输入验证，确保参数为数字类型
        self.validate_input(a)
        self.validate_input(b)
        
        # 修复: 添加除零检查，防止ZeroDivisionError
        if b == 0:
            raise ValueError("Cannot divide by zero")
        
        return a / b
    
    def power(self, base, exponent):
        """幂运算 - 支持字符串输入"""
        # 转换为数字类型
        try:
            base = float(base)
            exponent = float(exponent)
        except (ValueError, TypeError):
            raise TypeError("Inputs must be numeric")
        return base ** exponent
    
    def average(self, numbers):
        """计算平均值 - 处理空列表"""
        if not numbers:
            return 0
        total = sum(numbers)
        return total / len(numbers)
    
    def validate_input(self, value):
        """输入验证"""
        if value is None:
            raise ValueError("Input cannot be None")
        if not isinstance(value, (int, float)):
            raise ValueError("Input must be a number")
        return True

