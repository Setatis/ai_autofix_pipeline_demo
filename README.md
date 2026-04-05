# AI Auto-Fix Pipeline

> 大模型智能体 Harness 工程研究 - 同济大学 SITP 项目

基于大模型的智能代码修复系统，实现"监控检测 → AI分析 → 自动修复 → 部署验证"的完整闭环。

## 项目概述

本项目探索如何将大模型能力转化为可控、可靠、可复用的智能体系统，构建统一的 Harness（运行与控制框架），提升智能体的可控性、可评估性与可复现性。

### 核心能力

- **智能监控**：自动运行测试套件，检测失败用例
- **AI 分析**：调用大模型分析 Bug 根因，输出置信度
- **自动修复**：生成修复代码并自动应用
- **部署验证**：语法检查、导入测试、版本标记
- **报告生成**：输出详细的 Markdown 修复报告

## 快速开始

### 环境要求

- Python 3.8+
- pip

### 安装依赖

```bash
pip install openai pyyaml pytest flask flask-cors alibabacloud-esa20240910 alibabacloud-tea-openapi
```

### 运行 Demo

**方式一：Web 界面（推荐）**

```bash
cd ai_autofix_pipeline
python web_api.py
```

访问 http://localhost:5000 体验完整演示。

**方式二：命令行**

```bash
cd ai_autofix_pipeline
python demo_full_pipeline.py
```

## 项目结构

```
apply4sitp/
├── ai_autofix_pipeline/           # 核心代码
│   ├── core/                       # 核心模块
│   │   ├── monitor.py              # 测试监控
│   │   ├── ai_analyzer.py          # AI 分析器
│   │   ├── ai_fixer.py             # AI 修复器
│   │   ├── deployer.py             # 部署验证器
│   │   ├── verifier.py             # 验证器
│   │   ├── reporter.py             # 报告生成
│   │   └── issue_generator.py      # Issue 生成
│   ├── test_app/                   # 测试应用
│   │   ├── calculator.py           # 计算器（含预设 Bug）
│   │   └── test_calculator.py      # 测试用例
│   ├── reports/                    # 生成的报告
│   ├── web_api.py                  # Flask Web API
│   ├── demo_full_pipeline.py       # 命令行入口
│   └── config.yaml                 # 配置文件
├── web-demo/                       # 前端界面
│   └── index.html                  # Web Demo 页面
└── README.md                       # 项目文档
```

## 配置说明

### API 配置

编辑 `ai_autofix_pipeline/config.yaml`：

```yaml
api:
  provider: "siliconflow"           # 支持 openai, deepseek, zhipuai, siliconflow
  model: "Pro/zai-org/GLM-5"        # 模型名称
  api_key: "your-api-key"           # API Key
  base_url: "https://api.siliconflow.cn/v1"
  temperature: 0.2
  max_tokens: 2000

pipeline:
  max_retries: 3
  timeout_seconds: 300
  auto_commit: true
  auto_deploy: true
  run_tests: true

report:
  output_dir: "reports"
  format: "markdown"
  include_code_diff: true
```

## API 接口

### Web API

| 端点 | 方法 | 说明 |
|------|------|------|
| `/` | GET | 前端页面 |
| `/api/start` | POST | 启动 Pipeline |
| `/api/status` | GET | 获取当前状态 |
| `/api/stream` | GET | SSE 实时日志流 |
| `/api/reset` | POST | 重置测试文件 |

### 示例调用

```python
import requests

# 启动 Pipeline
response = requests.post('http://localhost:5000/api/start')
print(response.json())

# 获取状态
response = requests.get('http://localhost:5000/api/status')
print(response.json())

# 重置
response = requests.post('http://localhost:5000/api/reset')
print(response.json())
```

## 工作流程

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
│  │ 6.验证   │◀───│ 5.自动   │◀───│ 4.AI修复 │               │
│  │   测试   │    │   部署   │    │   代码   │               │
│  └──────────┘    └──────────┘    └──────────┘               │
│       │                                                      │
│       ▼                                                      │
│  ┌──────────┐                                               │
│  │ 7.生成   │                                               │
│  │   报告   │                                               │
│  └──────────┘                                               │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Demo 演示

### 预设 Bug

项目包含一个计算器应用 `calculator.py`，预设了 4 个典型 Bug：

| Bug | 方法 | 问题描述 |
|-----|------|----------|
| 1 | `divide` | 没有处理除零情况 |
| 2 | `power` | 没有验证输入类型 |
| 3 | `average` | 没有处理空列表 |
| 4 | `validate_input` | 只检查 None，没有检查类型 |

### 运行演示

1. 启动后端服务
2. 打开浏览器访问 http://localhost:5000
3. 点击「开始演示」按钮
4. 观察实时日志，AI 自动分析并修复 Bug
5. 查看修复报告

### 重置功能

点击「重置」按钮，系统会通过 Git 从 `bug-version` 分支恢复原始有 Bug 的代码，可重复演示。

## 本地运行

### 前端页面

前端页面位于 `web-demo/index.html`，可通过 Flask 服务访问：

```bash
cd ai_autofix_pipeline
python web_api.py
```

访问 http://localhost:5000 即可使用完整功能。

## 项目背景

本项目为同济大学 2026 年第二批 SITP（大学生创新训练计划）课题：

- **选题名称**：大模型智能体 Harness 工程研究
- **选题类型**：创新训练项目
- **指导教师**：黄凯锋（计算机科学与技术学院）
- **项目期限**：一年半期

### 研究目的

- 构建统一的 Harness（运行与控制框架）
- 提升智能体的可控性、可评估性与可复现性
- 降低大模型应用的不确定性

### 创新点

1. 提出统一 Harness 抽象模型
2. 实现自然语言驱动的控制逻辑
3. 构建可解释评测体系
4. 支持跨任务与跨模型的通用智能体工程框架

## 技术栈

- **后端**：Python, Flask, OpenAI SDK
- **前端**：HTML5, CSS3, JavaScript (原生)
- **AI**：GLM-5 (via SiliconFlow API)
- **测试**：pytest
- **后端**：Flask (本地开发服务器)

## 开发指南

### 扩展新的 AI Provider

在 `core/ai_analyzer.py` 和 `core/ai_fixer.py` 中添加新的 provider 支持。

### 添加新的测试用例

在 `test_app/test_calculator.py` 中添加新的测试方法：

```python
def test_new_feature(self):
    """测试新功能"""
    assert self.calc.new_feature() == expected_result
```

### 自定义报告格式

修改 `core/reporter.py` 中的模板生成逻辑。

## 许可证

本项目仅供学术研究使用。

## 联系方式

- 同济大学计算机科学与技术学院
- 指导教师：黄凯锋
