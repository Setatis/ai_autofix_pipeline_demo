
"""
测试监控模块 - 运行测试并收集结果
"""
import subprocess
from typing import List, Dict, Any
from datetime import datetime


class Monitor:
    """监控测试执行"""
    
    def __init__(self):
        pass
    
    def run_tests(self) -> Dict[str, Any]:
        """
        运行测试套件并收集结果
        
        Returns:
            测试结果字典
        """
        print("\n" + "="*60)
        print("[?] 步骤1: 运行测试监控")
        print("="*60)
        
        try:
            import os
            # 获取脚本所在目录作为工作目录
            cwd = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            
            # 运行pytest
            result = subprocess.run(
                ["python", "-m", "pytest", "test_app/", "-v", "--tb=short"],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                cwd=cwd,
                timeout=60
            )
            
            # 解析测试结果
            test_report = self._parse_test_output(result)
            
            print(f"\n[OK] 测试执行完成")
            print(f"   通过: {test_report['passed']}")
            print(f"   失败: {test_report['failed']}")
            print(f"   错误: {test_report['errors']}")
            
            return test_report
            
        except subprocess.TimeoutExpired:
            print("[ERR] 测试执行超时")
            return {"status": "timeout", "failures": []}
        except Exception as e:
            print(f"[ERR] 测试执行失败: {e}")
            return {"status": "error", "error": str(e)}
    
    def _parse_test_output(self, result: subprocess.CompletedProcess) -> Dict[str, Any]:
        """解析pytest输出"""
        output = result.stdout + "\n" + result.stderr
        
        # 统计通过和失败的测试
        passed = output.count(" PASSED")
        failed = output.count(" FAILED")
        errors = output.count(" ERROR")
        
        # 提取失败信息
        failures = []
        lines = output.split("\n")
        
        for i, line in enumerate(lines):
            # 更精确地匹配 FAILED 行
            # 格式1: test_app/test_calculator.py::TestCalculator::test_name FAILED [ XX%]
            # 格式2: FAILED test_app/test_calculator.py::TestCalculator::test_name
            if "FAILED" in line and "test_" in line:
                # 提取测试名称
                if "::" in line:
                    parts = line.split("::")
                    if len(parts) >= 2:
                        # 提取完整的测试路径: TestCalculator::test_name
                        # 需要从文件路径后开始提取
                        test_path_parts = []
                        for part in parts:
                            part_stripped = part.strip()
                            # 跳过文件路径部分
                            if '/' in part_stripped or '\\' in part_stripped:
                                continue
                            # 收集类名和函数名
                            if part_stripped and not part_stripped.startswith('['):
                                test_path_parts.append(part_stripped.split()[0])  # 去除后缀
                        
                        # 组合成完整测试路径
                        if test_path_parts:
                            full_test_name = '::'.join(test_path_parts)
                            
                            # 查找错误信息
                            error_msg = "Unknown error"
                            for j in range(i+1, min(i+10, len(lines))):
                                line_stripped = lines[j].strip()
                                if not line_stripped or line_stripped.startswith("["):
                                    continue
                                if (line_stripped.startswith("E ") or 
                                    "Error" in line_stripped or 
                                    "Failed" in line_stripped):
                                    error_msg = line_stripped
                                    break
                            
                            failures.append({
                                "test": full_test_name,
                                "error": error_msg,
                                "timestamp": datetime.now().isoformat()
                            })
        
        # 去重（同一个测试可能被多次匹配）
        seen_tests = set()
        unique_failures = []
        for failure in failures:
            if failure["test"] not in seen_tests:
                seen_tests.add(failure["test"])
                unique_failures.append(failure)
        
        return {
            "status": "completed",
            "passed": passed,
            "failed": failed,
            "errors": errors,
            "failures": unique_failures,
            "raw_output": output
        }
    
    def run_tests_silent(self) -> Dict[str, Any]:
        """
        静默运行测试套件（不打印输出）
        
        Returns:
            测试结果字典
        """
        try:
            import os
            # 获取脚本所在目录作为工作目录
            cwd = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            
            result = subprocess.run(
                ["python", "-m", "pytest", "test_app/", "-v", "--tb=short"],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                cwd=cwd,
                timeout=60
            )
            
            test_report = self._parse_test_output(result)
            return test_report
            
        except subprocess.TimeoutExpired:
            return {"status": "timeout", "failures": []}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def detect_failures(self, test_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        检测并返回失败的测试用例
        
        Args:
            test_results: 测试结果
            
        Returns:
            失败列表
        """
        failures = test_results.get("failures", [])
        
        if failures:
            print(f"\n[!] 检测到 {len(failures)} 个测试失败:")
            for i, failure in enumerate(failures, 1):
                print(f"   {i}. {failure['test']}")
                print(f"      错误: {failure['error'][:100]}...")
        else:
            print("\n[OK] 所有测试通过!")
        
        return failures
