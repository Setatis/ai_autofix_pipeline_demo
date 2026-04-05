"""
Bug报告生成模块 - 自动生成Issue
"""
import json
from typing import List, Dict, Any
from datetime import datetime


class IssueGenerator:
    """生成Bug报告和Issue"""
    
    def __init__(self):
        self.issues = []
    
    def generate_issue(self, failure: Dict[str, Any], test_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        为失败的测试生成Issue
        
        Args:
            failure: 失败信息
            test_results: 完整测试结果
            
        Returns:
            Issue字典
        """
        issue = {
            "id": f"BUG-{len(self.issues) + 1:03d}",
            "title": f"[Bug] {failure['test']} 测试失败",
            "severity": self._assess_severity(failure),
            "status": "open",
            "created_at": datetime.now().isoformat(),
            "description": self._generate_description(failure, test_results),
            "error_trace": failure.get("error", "N/A"),
            "test_name": failure["test"],
            "context": {
                "total_tests": test_results.get("passed", 0) + test_results.get("failed", 0),
                "passed": test_results.get("passed", 0),
                "failed": test_results.get("failed", 0),
                "failure_rate": f"{test_results.get('failed', 0) / max(test_results.get('passed', 1) + test_results.get('failed', 1), 1) * 100:.1f}%"
            }
        }
        
        self.issues.append(issue)
        return issue
    
    def _assess_severity(self, failure: Dict[str, Any]) -> str:
        """评估Bug严重程度"""
        error = failure.get("error", "").lower()
        
        if "zerodivision" in error or "type" in error:
            return "critical"
        elif "assertion" in error:
            return "high"
        else:
            return "medium"
    
    def _generate_description(self, failure: Dict[str, Any], test_results: Dict[str, Any]) -> str:
        """生成详细的Bug描述"""
        description = f"""
## Bug描述

**测试用例**: {failure['test']}
**严重程度**: {self._assess_severity(failure)}
**发现时间**: {failure.get('timestamp', 'N/A')}

## 错误信息

```
{failure.get('error', 'No error message available')}
```

## 复现步骤

1. 运行测试套件: `pytest test_app/ -v`
2. 观察测试 {failure['test']} 失败
3. 错误如上所示

## 影响范围

- 总测试数: {test_results.get('passed', 0) + test_results.get('failed', 0)}
- 通过率: {test_results.get('passed', 0)}/{test_results.get('passed', 0) + test_results.get('failed', 0)}
- 失败率: {test_results.get('failed', 0)}/{test_results.get('passed', 0) + test_results.get('failed', 0)}

## 建议优先级

需要立即修复以防止影响其他功能。
""".strip()
        
        return description
    
    def generate_summary(self, issues: List[Dict[str, Any]]) -> str:
        """生成Issue汇总"""
        if not issues:
            return "没有发现新的Bug"
        
        summary = f"## Bug报告汇总\n\n共发现 **{len(issues)}** 个问题:\n\n"
        
        for issue in issues:
            severity_icon = {
                "critical": "🔴",
                "high": "🟠",
                "medium": "🟡"
            }.get(issue["severity"], "⚪")
            
            summary += f"{severity_icon} **{issue['id']}**: {issue['title']}\n"
            summary += f"   - 严重程度: {issue['severity']}\n"
            summary += f"   - 状态: {issue['status']}\n\n"
        
        return summary
