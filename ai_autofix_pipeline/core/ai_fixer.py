"""
AI修复模块 - 自动生成并应用修复代码
"""
import os
from typing import Dict, Any
from openai import OpenAI


class AIFixer:
    """使用AI自动修复Bug"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.client = OpenAI(
            api_key=config.get("api_key", ""),
            base_url=config.get("base_url", "https://api.openai.com/v1")
        )
        self.model = config.get("model", "gpt-3.5-turbo")
        self.temperature = config.get("temperature", 0.2)
        self.fix_results = []
    
    def generate_fix(self, issue: Dict[str, Any], analysis: Dict[str, Any], 
                    source_code: str) -> Dict[str, Any]:
        """
        生成修复代码
        
        Args:
            issue: Bug Issue
            analysis: AI分析结果
            source_code: 源代码
            
        Returns:
            修复结果
        """
        print(f"\n🔧 步骤4: AI生成修复 - {issue['id']}")
        print(f"   根因: {analysis.get('root_cause', 'N/A')[:80]}...")
        
        prompt = self._build_fix_prompt(issue, analysis, source_code)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.config.get("max_tokens", 2000)
            )
            
            fix_result = self._parse_fix(response.choices[0].message.content, source_code)
            fix_result["issue_id"] = issue["id"]
            fix_result["test_name"] = issue["test_name"]
            
            self.fix_results.append(fix_result)
            
            print(f"   ✅ 修复代码生成完成")
            print(f"   修改类型: {fix_result.get('change_type', 'N/A')}")
            print(f"   代码行数: {fix_result.get('lines_changed', 0)}")
            
            return fix_result
            
        except Exception as e:
            print(f"   ❌ 修复生成失败: {e}")
            return {
                "issue_id": issue["id"],
                "success": False,
                "error": str(e)
            }
    
    def apply_fix(self, fix_result: Dict[str, Any], file_path: str) -> bool:
        """
        应用修复到文件
        
        Args:
            fix_result: 修复结果
            file_path: 目标文件路径
            
        Returns:
            是否成功
        """
        print(f"\n   📝 应用修复到 {file_path}")
        
        try:
            if "fixed_code" not in fix_result:
                print(f"   ❌ 没有可用的修复代码")
                return False
            
            # 备份原文件
            import shutil
            backup_path = file_path + ".backup"
            shutil.copy(file_path, backup_path)
            print(f"   💾 已备份原文件到 {backup_path}")
            
            # 写入修复后的代码
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(fix_result["fixed_code"])
            
            print(f"   ✅ 修复已应用")
            return True
            
        except Exception as e:
            print(f"   ❌ 应用修复失败: {e}")
            return False
    
    def _get_system_prompt(self) -> str:
        """获取系统提示词"""
        return """你是一个资深的软件工程师。你的任务是:
1. 根据Bug分析结果生成修复代码
2. 确保修复代码完整、可运行
3. 保持代码风格一致
4. 添加必要的错误处理和边界检查
5. 添加注释说明修复内容

请返回完整的修复后代码,用```python标记。"""
    
    def _build_fix_prompt(self, issue: Dict[str, Any], analysis: Dict[str, Any], 
                         source_code: str) -> str:
        """构建修复提示词"""
        return f"""请修复以下Bug:

## Bug信息
**测试**: {issue['test_name']}
**错误**: {issue['error_trace']}

## AI分析结果
**根因**: {analysis.get('root_cause', 'N/A')}
**位置**: {analysis.get('bug_location', 'N/A')}
**建议**: {analysis.get('suggestion', 'N/A')}

## 当前源代码
```python
{source_code}
```

## 修复要求
1. 修复指出的Bug
2. 添加适当的错误处理
3. 添加输入验证
4. 保持代码风格一致
5. 返回完整的修复后代码

请返回完整的Python代码。"""
    
    def _parse_fix(self, response: str, original_code: str) -> Dict[str, Any]:
        """解析修复代码"""
        # 提取代码块
        if "```python" in response:
            fixed_code = response.split("```python")[1].split("```")[0]
        elif "```" in response:
            fixed_code = response.split("```")[1].split("```")[0]
        else:
            fixed_code = response
        
        # 计算变更
        original_lines = original_code.split('\n')
        fixed_lines = fixed_code.split('\n')
        lines_changed = abs(len(fixed_lines) - len(original_lines))
        
        # 简单分类变更类型
        if "def " in fixed_code and "def " not in original_code:
            change_type = "添加函数"
        elif "if " in fixed_code and "if " not in original_code:
            change_type = "添加条件检查"
        elif "try:" in fixed_code and "try:" not in original_code:
            change_type = "添加异常处理"
        else:
            change_type = "代码修改"
        
        return {
            "success": True,
            "fixed_code": fixed_code,
            "change_type": change_type,
            "lines_changed": lines_changed,
            "full_response": response
        }
