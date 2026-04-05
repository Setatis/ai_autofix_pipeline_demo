
"""
验证模块 - 验证修复是否成功
"""
import subprocess
from typing import Dict, Any, List
from datetime import datetime


class Verifier:
    """验证修复结果"""
    
    def __init__(self):
        self.verification_results = []
    
    def verify_fix(self, issue: Dict[str, Any], app_dir: str = "test_app") -> Dict[str, Any]:
        """验证修复是否成功"""
        print(f"\n[验证] 步骤6: 验证修复 - {issue['id']}")
        # 兼容 test_name 和 test 字段
        test_name = issue.get('test_name', issue.get('test', 'Unknown'))
        print(f"   测试: {test_name}")
        
        verification = {
            "issue_id": issue["id"],
            "test_name": test_name,
            "timestamp": None,
            "success": False,
            "details": {}
        }
        
        try:
            test_result = self._run_specific_test(test_name, app_dir)
            verification["details"] = test_result
            verification["timestamp"] = test_result.get("timestamp")
            
            if test_result.get("passed", False):
                print(f"   [OK] 验证通过 - 测试 {test_name} 现在通过了!")
                verification["success"] = True
            else:
                print(f"   [ERR] 验证失败 - 测试仍然失败")
                print(f"      错误: {test_result.get('error', 'Unknown')[:100]}")
                verification["success"] = False
            
            self.verification_results.append(verification)
            return verification
            
        except Exception as e:
            print(f"   [ERR] 验证过程出错: {e}")
            import traceback
            traceback.print_exc()
            verification["error"] = str(e)
            return verification
    
    def run_full_test_suite(self, app_dir: str = "test_app") -> Dict[str, Any]:
        """运行完整测试套件"""
        print(f"\n[验证] 运行完整测试套件...")
        
        try:
            import os
            cwd = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            
            result = subprocess.run(
                ["python", "-m", "pytest", f"{app_dir}/", "-v", "--tb=short"],
                capture_output=True,
                text=True,
                cwd=cwd,
                timeout=60
            )
            
            passed = result.stdout.count(" PASSED")
            failed = result.stdout.count(" FAILED")
            
            print(f"   通过: {passed}")
            print(f"   失败: {failed}")
            
            return {
                "passed": passed,
                "failed": failed,
                "raw_output": result.stdout
            }
            
        except Exception as e:
            print(f"   [ERR] 测试执行失败: {e}")
            return {"passed": 0, "failed": 0, "error": str(e)}
    
    def _run_specific_test(self, test_name: str, app_dir: str) -> Dict[str, Any]:
        """运行特定测试"""
        try:
            import os
            # 构建测试 ID
            # test_name 可能是: test_divide_by_zero 或 TestCalculator::test_divide_by_zero
            test_file = f"{app_dir}/test_calculator.py"
            
            # 如果 test_name 已经包含 ::，直接使用；否则添加到 TestCalculator 类下
            if "::" in test_name:
                test_id = f"{test_file}::{test_name}"
            else:
                test_id = f"{test_file}::TestCalculator::{test_name}"
            
            print(f"   运行: pytest {test_id}")
            
            # 获取工作目录
            cwd = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            
            # 运行测试，增加超时时间到 60 秒
            result = subprocess.run(
                ["python", "-m", "pytest", test_id, "-v", "--tb=short"],
                capture_output=True,
                text=True,
                cwd=cwd,
                timeout=60
            )
            
            passed = "PASSED" in result.stdout
            error = result.stderr if not passed else None
            
            if passed:
                print(f"   [OK] 测试通过")
            else:
                print(f"   [ERR] 测试失败: {error[:100] if error else 'Unknown'}")
            
            return {
                "test_name": test_name,
                "passed": passed,
                "error": error[:200] if error else None,
                "timestamp": datetime.now().isoformat()
            }
            
        except subprocess.TimeoutExpired:
            print(f"   [ERR] 测试超时")
            return {
                "test_name": test_name,
                "passed": False,
                "error": "Test execution timeout (60s)",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            print(f"   [ERR] 执行异常: {e}")
            return {
                "test_name": test_name,
                "passed": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
