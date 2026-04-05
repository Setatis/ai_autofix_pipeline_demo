"""
AI分析模块 - 使用大模型定位Bug根因
"""
import os
from typing import Dict, Any, List
from openai import OpenAI


class AIAnalyzer:
    """使用AI分析Bug根因"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.client = OpenAI(
            api_key=config.get("api_key", ""),
            base_url=config.get("base_url", "https://api.openai.com/v1")
        )
        self.model = config.get("model", "gpt-3.5-turbo")
        self.temperature = config.get("temperature", 0.2)
        self.analysis_results = []
    
    def analyze_bug(self, issue: Dict[str, Any], source_code: str) -> Dict[str, Any]:
        """
        分析Bug并定位根因
        
        Args:
            issue: Bug Issue信息
            source_code: 相关源代码
            
        Returns:
            分析结果
        """
        print(f"\n🧠 步骤3: AI分析Bug - {issue['id']}")
        print(f"   测试: {issue['test_name']}")
        
        prompt = self._build_analysis_prompt(issue, source_code)
        
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
            
            analysis = self._parse_analysis(response.choices[0].message.content)
            analysis["issue_id"] = issue["id"]
            analysis["test_name"] = issue["test_name"]
            
            self.analysis_results.append(analysis)
            
            print(f"   ✅ 分析完成")
            print(f"   根因: {analysis.get('root_cause', 'N/A')[:100]}...")
            print(f"   位置: {analysis.get('bug_location', 'N/A')}")
            print(f"   置信度: {analysis.get('confidence', 0)}")
            
            return analysis
            
        except Exception as e:
            print(f"   ❌ AI分析失败: {e}")
            return {
                "issue_id": issue["id"],
                "test_name": issue["test_name"],
                "root_cause": f"分析失败: {str(e)}",
                "bug_location": "Unknown",
                "confidence": 0,
                "explanation": str(e)
            }
    
    def _get_system_prompt(self) -> str:
        """获取系统提示词"""
        return """你是一个资深的软件工程师和Bug分析专家。你的任务是:
1. 分析测试失败的错误信息
2. 阅读相关源代码
3. 精确定位Bug的位置和根本原因
4. 提供清晰的解释

请以JSON格式返回分析结果,包含以下字段:
- root_cause: 根本原因描述
- bug_location: Bug位置(文件和行号)
- explanation: 详细解释
- confidence: 置信度(0-1)
- suggestion: 修复建议"""
    
    def _build_analysis_prompt(self, issue: Dict[str, Any], source_code: str) -> str:
        """构建分析提示词"""
        return f"""请分析以下Bug:

## Bug信息
**测试用例**: {issue['test_name']}
**错误信息**: 
{issue['error_trace']}

## 相关源代码
```python
{source_code}
```

## 分析要求
1. 精确定位Bug在哪一行
2. 解释为什么会发生这个错误
3. 说明应该如何修复
4. 给出修复建议

请以JSON格式返回分析结果。"""
    
    def _parse_analysis(self, response: str) -> Dict[str, Any]:
        """解析AI响应"""
        import json
        
        # 尝试从响应中提取JSON
        try:
            # 查找JSON块
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0]
            else:
                json_str = response
            
            analysis = json.loads(json_str)
            return analysis
        except:
            # 如果解析失败,返回简化版本
            return {
                "root_cause": response[:200],
                "bug_location": "需要手动检查",
                "explanation": response,
                "confidence": 0.5,
                "suggestion": "需要人工审查"
            }
