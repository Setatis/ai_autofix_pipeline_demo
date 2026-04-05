"""
报告生成模块 - 生成完整的修复报告
"""
import os
from typing import Dict, Any, List
from datetime import datetime


class Reporter:
    """生成修复报告"""
    
    def __init__(self, output_dir: str = "reports"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def generate_report(self, pipeline_data: Dict[str, Any]) -> str:
        """生成完整的修复报告"""
        print(f"\n📊 步骤7: 生成修复报告")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = os.path.join(self.output_dir, f"fix_report_{timestamp}.md")
        
        report = self._build_report(pipeline_data)
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"   ✅ 报告已生成: {report_file}")
        return report_file
    
    def _build_report(self, data: Dict[str, Any]) -> str:
        """构建报告内容"""
        report = f"""# AI Auto-Fix Pipeline - 修复报告

**生成时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**报告版本**: v1.0

---

## 执行概览

| 指标 | 值 |
|------|-----|
| 发现Bug数 | {len(data.get('issues', []))} |
| 分析Bug数 | {len(data.get('analyses', []))} |
| 修复Bug数 | {len(data.get('fixes', []))} |
| 验证通过 | {len([v for v in data.get('verifications', []) if v.get('success')])} |
| 部署成功 | {data.get('deployment', {}).get('success', False)} |

---

## Bug清单

"""
        for i, issue in enumerate(data.get('issues', []), 1):
            report += f"### Bug #{i}: {issue['id']}\n\n"
            report += f"- **测试**: {issue['test_name']}\n"
            report += f"- **严重程度**: {issue['severity']}\n"
            report += f"- **状态**: {issue['status']}\n"
            report += f"- **发现时间**: {issue['created_at']}\n\n"
            
            report += f"**错误信息**:\n```\n{issue.get('error_trace', 'N/A')[:300]}\n```\n\n"
            
            analysis = next((a for a in data.get('analyses', []) if a.get('issue_id') == issue['id']), None)
            if analysis:
                report += f"**AI分析**:\n"
                report += f"- 根因: {analysis.get('root_cause', 'N/A')}\n"
                report += f"- 位置: {analysis.get('bug_location', 'N/A')}\n"
                report += f"- 置信度: {analysis.get('confidence', 0)}\n\n"
            
            fix = next((f for f in data.get('fixes', []) if f.get('issue_id') == issue['id']), None)
            if fix:
                report += f"**修复方案**:\n"
                report += f"- 修改类型: {fix.get('change_type', 'N/A')}\n"
                report += f"- 代码变更: {fix.get('lines_changed', 0)} 行\n\n"
            
            verification = next((v for v in data.get('verifications', []) if v.get('issue_id') == issue['id']), None)
            if verification:
                status = "✅ 通过" if verification.get('success') else "❌ 失败"
                report += f"**验证结果**: {status}\n\n"
            
            report += "---\n\n"
        
        report += "## 部署信息\n\n"
        deployment = data.get('deployment', {})
        report += f"- **部署状态**: {'✅ 成功' if deployment.get('success') else '❌ 失败'}\n"
        report += f"- **版本号**: {deployment.get('version', 'N/A')}\n"
        report += f"- **部署时间**: {deployment.get('timestamp', 'N/A')}\n\n"
        
        if deployment.get('steps'):
            report += "**部署步骤**:\n\n"
            for step in deployment['steps']:
                icon = "✅" if step.get('success') else "❌"
                report += f"- {icon} {step['step']}\n"
            report += "\n"
        
        report += "## 测试总结\n\n"
        test_results = data.get('final_tests', {})
        report += f"- **通过**: {test_results.get('passed', 0)}\n"
        report += f"- **失败**: {test_results.get('failed', 0)}\n"
        report += f"- **通过率**: {self._calc_pass_rate(test_results)}\n\n"
        
        report += "## 改进建议\n\n"
        report += "1. 添加更多边界条件测试\n"
        report += "2. 考虑引入类型提示(Type Hints)\n"
        report += "3. 增加代码覆盖率\n"
        report += "4. 建立持续集成流程\n\n"
        
        report += "---\n\n"
        report += "## 附录\n\n"
        report += "### 工具链\n\n"
        report += "- **AI模型**: GLM-5 (SiliconFlow)\n"
        report += "- **测试框架**: Pytest\n"
        report += "- **部署方式**: 本地验证\n"
        report += "- **版本控制**: Git\n\n"
        
        report += "---\n*本报告由AI Auto-Fix Pipeline自动生成*\n"
        
        return report
    
    def _calc_pass_rate(self, test_results: Dict[str, Any]) -> str:
        """计算通过率"""
        passed = test_results.get('passed', 0)
        failed = test_results.get('failed', 0)
        total = passed + failed
        if total == 0:
            return "0%"
        return f"{passed/total*100:.1f}%"
