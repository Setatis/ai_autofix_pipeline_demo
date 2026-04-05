# AI Auto-Fix Pipeline

> 基于大模型的智能代码自动修复系统

一个展示 AI 如何自动检测、分析并修复代码 Bug 的演示项目。实现"测试监控 → AI分析 → 自动修复 → 验证"的完整闭环。

## 项目简介

本项目演示如何利用大语言模型（LLM）构建智能代码修复系统，能够：

- 🔍 **自动检测**：运行测试套件，识别失败的测试用例
- 🧠 **AI 分析**：调用大模型分析 Bug 根因，输出详细诊断
- 🔧 **自动修复**：生成修复代码并自动应用到源文件
- ✅ **验证测试**：运行测试验证修复是否成功
- 📊 **实时展示**：通过 Web 界面实时查看修复过程

## 快速开始

### 环境要求

- Python 3.8+
- pip

### 安装依赖

```bash
pip install openai pyyaml pytest flask flask-cors
```

### 配置 API Key

编辑 `ai_autofix_pipeline/config.yaml`，填入你的 API Key：

```yaml
api:
  provider: "siliconflow"           # 支持 openai, deepseek, zhipuai, siliconflow
  model: "Pro/zai-org/GLM-5"        # 使用的模型
  api_key: "your-api-key-here"      # 替换为你的 API Key
  base_url: "https://api.siliconflow.cn/v1"
  temperature: 0.2
  max_tokens: 2000
```

### 运行演示

**Web 界面（推荐）**

```bash
cd ai_autofix_pipeline
python web_api.py
```

访问 http://localhost:5000 体验完整的 Web 演示。

**命令行模式**

```bash
cd ai_autofix_pipeline
python demo_full_pipeline.py
```

## 演示流程

```
┌─────────────────────────────────────────────────────────────┐
│                    AI Auto-Fix Pipeline                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐               │
│  │ 1.监控   │───▶│ 2.生成   │───▶│ 3.AI分析 │               │
│  │   检测   │    │   Issue  │    │   根因   │               │
│  └──────────┘    └──────────┘    └──────────┘               │
│                                        │                     │
│                                        ▼                     │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐               │
│  │ 5.验证   │◀───│ 4.AI修复 │◀───│          │               │
│  │   测试   │    │   代码   │    │          │               │
│  └──────────┘    └──────────┘    └──────────┘               │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 测试用例

项目包含一个计算器应用，预设了一个典型 Bug：

**Bug：除零错误**
```python
def divide(self, a, b):
    """除法 - Bug: 没有处理除零情况"""
    return a / b  # 当 b=0 时会抛出 ZeroDivisionError
```

**期望行为**：应该抛出 `ValueError("Divider cannot be zero")`

AI 会自动分析这个问题，并生成正确的修复代码。

## 项目结构

```
ai_autofix_pipeline/
├── core/                       # 核心模块
│   ├── monitor.py              # 测试监控 - 运行 pytest 并解析结果
│   ├── ai_analyzer.py          # AI 分析器 - 调用大模型分析 Bug
│   ├── ai_fixer.py             # AI 修复器 - 生成修复代码
│   ├── deployer.py             # 部署验证器 - 本地验证
│   ├── verifier.py             # 验证器 - 验证修复是否成功
│   ├── reporter.py             # 报告生成器
│   └── issue_generator.py      # Issue 生成器
├── test_app/                   # 测试应用
│   ├── calculator.py           # 计算器（含预设 Bug）
│   ├── calculator_original.py  # 原始版本（用于重置）
│   └── test_calculator.py      # 测试用例
├── web_api.py                  # Flask Web API 服务
├── demo_full_pipeline.py       # 命令行演示入口
├── config.yaml                 # 配置文件
└── README.md                   # 说明文档
```

## Web API

### 接口列表

| 端点 | 方法 | 说明 |
|------|------|------|
| `/` | GET | 前端页面 |
| `/api/start` | POST | 启动 Pipeline |
| `/api/status` | GET | 获取当前状态 |
| `/api/stream` | GET | SSE 实时日志流 |
| `/api/reset` | POST | 重置测试文件 |

### 使用示例

```python
import requests

# 启动 Pipeline
requests.post('http://localhost:5000/api/start')

# 获取状态
response = requests.get('http://localhost:5000/api/status')
print(response.json())

# 重置（恢复原始有 Bug 的代码）
requests.post('http://localhost:5000/api/reset')
```

## 技术栈

- **后端**：Python, Flask
- **前端**：HTML5, CSS3, JavaScript (原生)
- **AI**：GLM-5 / GPT-3.5 / DeepSeek 等（通过 OpenAI SDK）
- **测试**：pytest
- **通信**：SSE (Server-Sent Events) 实时日志推送

## 核心模块

### 1. Monitor（监控模块）
- 运行 pytest 测试套件
- 解析测试输出，识别失败用例
- 提取失败信息和测试名称

### 2. AI Analyzer（AI 分析模块）
- 调用大模型 API 分析 Bug 根因
- 输出结构化的诊断信息
- 提供置信度评估

### 3. AI Fixer（AI 修复模块）
- 根据分析结果生成修复代码
- 支持多种编程语言
- 自动应用修复到源文件

### 4. Verifier（验证模块）
- 运行特定测试验证修复
- 对比修复前后的测试结果
- 提供验证报告

## 开发指南

### 扩展 AI Provider

在 `core/ai_analyzer.py` 和 `core/ai_fixer.py` 中可以添加新的 AI 服务支持：

```python
# 支持的 provider
# - openai: OpenAI API
# - siliconflow: SiliconFlow API
# - deepseek: DeepSeek API
# - zhipuai: 智谱 AI API
```

### 添加测试用例

在 `test_app/test_calculator.py` 中添加新的测试：

```python
def test_new_feature(self):
    """测试新功能"""
    result = self.calc.new_feature()
    assert result == expected_value
```

### 修改配置

所有配置都在 `config.yaml` 中：

```yaml
pipeline:
  max_retries: 3                    # 最大重试次数
  timeout_seconds: 300              # 超时时间（秒）
  auto_commit: true                 # 自动提交
  auto_deploy: true                 # 自动部署
  run_tests: true                   # 运行测试

report:
  output_dir: "reports"             # 报告输出目录
  format: "markdown"                # 报告格式
  include_code_diff: true           # 包含代码差异
```

## 演示说明

### 运行完整演示

1. 启动服务：`python web_api.py`
2. 打开浏览器：http://localhost:5000
3. 点击「开始演示」按钮
4. 观察实时日志流
5. 查看 AI 的分析和修复过程

### 重置演示

点击「重置」按钮可恢复原始有 Bug 的代码，便于重复演示。

## 注意事项

- 使用前需要配置有效的 API Key
- 推荐使用 SiliconFlow、OpenAI 或 DeepSeek 等支持的 AI 服务
- 本项目为演示用途，生产环境需要增强错误处理和安全性
- 修复结果依赖于 AI 模型的准确性，建议人工审核

## 许可证

本项目仅供学习和演示使用。
