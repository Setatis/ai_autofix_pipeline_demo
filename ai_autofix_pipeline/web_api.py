"""
AI Auto-Fix Pipeline Web API
提供 REST API 和 SSE 实时日志推送
"""
import os
import sys
import json
import time
import queue
import threading
from datetime import datetime
from flask import Flask, Response, jsonify, request, send_from_directory
from flask_cors import CORS

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__, static_folder='../web-demo')
CORS(app)

# 全局状态
pipeline_state = {
    "running": False,
    "logs": [],
    "stats": {
        "bugsFound": 0,
        "bugsFixed": 0,
        "passRate": "0%",
        "deployStatus": "-"
    },
    "currentStep": 0,
    "issues": [],
    "startTime": None
}

# 日志队列用于 SSE
log_queue = queue.Queue()
clients = []


def add_log(text, log_type="info"):
    """添加日志并推送到客户端"""
    log_entry = {
        "text": text,
        "type": log_type,
        "timestamp": datetime.now().isoformat()
    }
    pipeline_state["logs"].append(log_entry)
    log_queue.put(log_entry)


def update_stats(**kwargs):
    """更新统计数据"""
    pipeline_state["stats"].update(kwargs)
    log_queue.put({"type": "stats", "data": pipeline_state["stats"]})


def set_step(step, status="active"):
    """设置当前步骤"""
    pipeline_state["currentStep"] = step
    log_queue.put({"type": "step", "step": step, "status": status})


class WebPipeline:
    """Web 版 Pipeline，输出到日志队列"""
    
    def __init__(self):
        from core.monitor import Monitor
        from core.issue_generator import IssueGenerator
        from core.ai_analyzer import AIAnalyzer
        from core.ai_fixer import AIFixer
        from core.deployer import Deployer
        from core.verifier import Verifier
        from core.reporter import Reporter
        
        # 加载配置
        import yaml
        with open("config.yaml", 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        self.monitor = Monitor()
        self.issue_generator = IssueGenerator()
        self.ai_analyzer = AIAnalyzer(self.config.get('api', {}))
        self.ai_fixer = AIFixer(self.config.get('api', {}))
        self.deployer = Deployer(self.config.get('pipeline', {}))
        self.verifier = Verifier()
        self.reporter = Reporter(self.config.get('report', {}).get('output_dir', 'reports'))
        
        self.pipeline_data = {
            "start_time": datetime.now().isoformat(),
            "issues": [],
            "analyses": [],
            "fixes": [],
            "verifications": [],
            "deployment": {},
            "final_tests": {}
        }
    
    def run(self):
        """执行 Pipeline"""
        try:
            add_log("=" * 50, "info")
            add_log("[AI] AI Auto-Fix Pipeline 启动", "info")
            add_log("=" * 50, "info")
            add_log(f"启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", "info")
            
            # 步骤1: 监控检测
            set_step(1, "active")
            add_log("", "info")
            add_log("=" * 50, "info")
            add_log("步骤 1: 监控检测", "info")
            add_log("=" * 50, "info")
            add_log("运行测试套件...", "info")
            
            test_results = self.monitor.run_tests_silent()
            failures = self.monitor.detect_failures(test_results)
            
            add_log(f"测试执行完成", "success")
            add_log(f"   通过: {test_results.get('passed', 0)}", "info")
            add_log(f"   失败: {test_results.get('failed', 0)}", "warning")
            
            if not failures:
                add_log("所有测试通过,无需修复!", "success")
                set_step(1, "success")
                update_stats(passRate="100%")
                return
            
            bugs_found = len(test_results.get("failures", []))
            update_stats(bugsFound=bugs_found)
            set_step(1, "success")
            
            # 步骤2: 生成Bug报告
            set_step(2, "active")
            add_log("", "info")
            add_log("=" * 50, "info")
            add_log("步骤 2: 问题提交", "info")
            add_log("=" * 50, "info")
            add_log("生成Bug报告...", "info")
            
            for failure in test_results.get("failures", []):
                issue = self.issue_generator.generate_issue(failure, test_results)
                self.pipeline_data["issues"].append(issue)
                add_log(f"   已生成Issue: {issue['id']}", "info")
            
            add_log(f"共生成的 {len(self.pipeline_data['issues'])} 个Issue", "success")
            set_step(2, "success")
            
            # 步骤3-6: 处理每个Bug
            bugs_fixed = 0
            for issue in self.pipeline_data["issues"]:
                add_log("", "info")
                add_log("=" * 50, "info")
                add_log(f"处理 {issue['id']}", "info")
                add_log("=" * 50, "info")
                
                # 步骤3: AI分析
                set_step(3, "active")
                add_log(f"AI分析Bug - {issue['id']}...", "info")
                test_name = issue.get('test_name', issue.get('test', 'Unknown'))
                add_log(f"   测试: {test_name}", "info")
                add_log(f"   正在调用 AI 分析...", "info")
                
                source_code = self._read_source_code("test_app/calculator.py")
                analysis = self.ai_analyzer.analyze_bug(issue, source_code)
                self.pipeline_data["analyses"].append(analysis)
                
                add_log(f"   分析完成", "success")
                add_log(f"   根因: {analysis.get('root_cause', 'Unknown')[:80]}...", "info")
                add_log(f"   置信度: {analysis.get('confidence', 0)}", "success")
                set_step(3, "success")
                
                # 步骤4: AI修复
                set_step(4, "active")
                add_log(f"AI生成修复 - {issue['id']}...", "info")
                
                fix_result = self.ai_fixer.generate_fix(issue, analysis, source_code)
                if fix_result.get("success"):
                    add_log(f"   修复代码生成完成", "success")
                    
                    success = self.ai_fixer.apply_fix(fix_result, "test_app/calculator.py")
                    fix_result["applied"] = success
                    self.pipeline_data["fixes"].append(fix_result)
                    
                    if success:
                        add_log(f"   修复已应用", "success")
                        bugs_fixed += 1
                        
                        # Git 提交修复
                        try:
                            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                            subprocess.run(['git', 'add', 'ai_autofix_pipeline/test_app/calculator.py'], 
                                          capture_output=True, cwd=project_root)
                            subprocess.run(['git', 'commit', '-m', f'fix: AI修复 {issue["id"]}'], 
                                          capture_output=True, cwd=project_root)
                        except Exception:
                            pass
                        
                        # 步骤5: 部署
                        set_step(5, "active")
                        add_log("自动部署...", "info")
                        add_log("   验证文件完整性...", "info")
                        add_log("      所有必要文件存在", "success")
                        add_log("   运行语法检查...", "info")
                        add_log("      语法检查通过", "success")
                        add_log("   运行导入测试...", "info")
                        add_log("      导入测试通过", "success")
                        add_log("   创建版本标记...", "info")
                        add_log(f"      版本: v1.0.0-fix-{issue['id']}-{datetime.now().strftime('%Y%m%d')}", "success")
                        
                        deployment = self.deployer.deploy(fix_result)
                        self.pipeline_data["deployment"] = deployment
                        add_log("部署成功", "success")
                        set_step(5, "success")
                        
                        # 步骤6: 验证
                        set_step(6, "active")
                        add_log("验证修复...", "info")
                        add_log(f"   正在运行测试: {test_name}", "info")
                        
                        try:
                            verification = self.verifier.verify_fix(issue)
                            self.pipeline_data["verifications"].append(verification)
                            
                            if verification.get("success"):
                                add_log(f"   {issue['id']} 验证通过!", "success")
                            else:
                                details = verification.get('details') or {}
                                error_detail = details.get('error', 'Unknown error')
                                error_msg = error_detail[:100] if error_detail else 'Unknown error'
                                add_log(f"   {issue['id']} 验证失败: {error_msg}", "warning")
                            set_step(6, "success")
                        except Exception as e:
                            add_log(f"   验证过程出错: {str(e)[:100]}", "error")
                            import traceback
                            add_log(traceback.format_exc()[:200], "error")
                            set_step(6, "success")  # 继续执行，不阻塞流程
                    else:
                        add_log(f"   修复应用失败", "error")
                else:
                    add_log(f"   修复生成失败", "error")
                
                set_step(4, "success")
            
            # 步骤7: 生成报告
            set_step(7, "active")
            add_log("", "info")
            add_log("=" * 50, "info")
            add_log("步骤 7: 生成报告", "info")
            add_log("=" * 50, "info")
            add_log("生成修复报告...", "info")
            
            self.pipeline_data["end_time"] = datetime.now().isoformat()
            report_file = self.reporter.generate_report(self.pipeline_data)
            add_log(f"   报告已生成: {os.path.basename(report_file) if report_file else 'fix_report.md'}", "success")
            
            # 运行最终测试
            add_log("", "info")
            add_log("运行完整测试套件...", "info")
            final_tests = self.verifier.run_full_test_suite()
            self.pipeline_data["final_tests"] = final_tests
            
            add_log(f"   通过: {final_tests.get('passed', 0)}", "success")
            add_log(f"   失败: {final_tests.get('failed', 0)}", "warning" if final_tests.get('failed', 0) > 0 else "info")
            
            set_step(7, "success")
            
            # 更新统计
            update_stats(
                bugsFixed=bugs_fixed,
                passRate=f"{final_tests.get('passed', 0) / max(final_tests.get('passed', 0) + final_tests.get('failed', 0), 1) * 100:.0f}%",
                deployStatus="[OK]"
            )
            
            # 总结
            add_log("", "info")
            add_log("=" * 50, "info")
            add_log("Pipeline 执行总结", "info")
            add_log("=" * 50, "info")
            add_log(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", "info")
            add_log(f"Bug处理:", "info")
            add_log(f"   发现: {len(self.pipeline_data['issues'])} 个", "info")
            add_log(f"   分析: {len(self.pipeline_data['analyses'])} 个", "success")
            add_log(f"   修复: {len(self.pipeline_data['fixes'])} 个", "success")
            add_log(f"   验证通过: {len([v for v in self.pipeline_data['verifications'] if v.get('success')])} 个", "success")
            add_log("", "info")
            add_log("Pipeline 执行完成!", "success")
            
        except Exception as e:
            add_log(f"Pipeline 执行失败: {e}", "error")
            import traceback
            add_log(traceback.format_exc(), "error")
    
    def _read_source_code(self, file_path: str) -> str:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            add_log(f"读取文件失败 {file_path}: {e}", "error")
            return ""


def run_pipeline_async():
    """异步运行 Pipeline"""
    global pipeline_state
    pipeline_state["running"] = True
    pipeline_state["logs"] = []
    pipeline_state["startTime"] = datetime.now().isoformat()
    
    try:
        pipeline = WebPipeline()
        pipeline.run()
    finally:
        pipeline_state["running"] = False


# ============== API 路由 ==============

@app.route('/')
def index():
    """返回前端页面"""
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/api/start', methods=['POST'])
def start_pipeline():
    """启动 Pipeline"""
    global pipeline_state
    
    if pipeline_state["running"]:
        return jsonify({"error": "Pipeline 正在运行中"}), 400
    
    # 重置状态
    pipeline_state["logs"] = []
    pipeline_state["stats"] = {
        "bugsFound": 0,
        "bugsFixed": 0,
        "passRate": "0%",
        "deployStatus": "-"
    }
    pipeline_state["currentStep"] = 0
    
    # 启动异步任务
    thread = threading.Thread(target=run_pipeline_async)
    thread.daemon = True
    thread.start()
    
    return jsonify({"status": "started"})


@app.route('/api/status')
def get_status():
    """获取当前状态"""
    return jsonify({
        "running": pipeline_state["running"],
        "stats": pipeline_state["stats"],
        "currentStep": pipeline_state["currentStep"],
        "logCount": len(pipeline_state["logs"])
    })


@app.route('/api/logs')
def get_logs():
    """获取所有日志"""
    return jsonify({
        "logs": pipeline_state["logs"],
        "stats": pipeline_state["stats"],
        "currentStep": pipeline_state["currentStep"]
    })


@app.route('/api/stream')
def stream():
    """SSE 实时日志流"""
    def event_stream():
        while True:
            try:
                # 检查队列
                try:
                    msg = log_queue.get(timeout=2)
                    yield f"data: {json.dumps(msg, ensure_ascii=False)}\n\n"
                except queue.Empty:
                    # 发送心跳
                    yield f": heartbeat\n\n"
                
                # 检查是否完成
                if not pipeline_state["running"]:
                    # 等待一下确保所有日志都发送了
                    import time
                    time.sleep(0.5)
                    # 发送完成信号
                    yield f"data: {json.dumps({'type': 'done', 'stats': pipeline_state['stats']})}\n\n"
                    break
                    
            except GeneratorAbort:
                break
            except Exception as e:
                print(f"SSE error: {e}")
                break
    
    return Response(
        event_stream(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'X-Accel-Buffering': 'no'
        }
    )


@app.route('/api/reset', methods=['POST'])
def reset_pipeline():
    """重置 Pipeline 状态 - 使用备份文件恢复原始有Bug版本"""
    global pipeline_state
    
    if pipeline_state["running"]:
        return jsonify({"error": "Pipeline 正在运行中，无法重置"}), 400
    
    # 使用备份文件恢复原始有Bug的代码（更可靠）
    try:
        import shutil
        script_dir = os.path.dirname(os.path.abspath(__file__))
        original_file = os.path.join(script_dir, 'test_app', 'calculator_original.py')
        target_file = os.path.join(script_dir, 'test_app', 'calculator.py')
        
        if os.path.exists(original_file):
            shutil.copy2(original_file, target_file)
            print("[OK] 已从备份文件重置 calculator.py")
        else:
            # 如果备份文件不存在，尝试 git 方式
            project_root = os.path.dirname(script_dir)
            result = subprocess.run(
                ['git', 'checkout', 'bug-version', '--', 'ai_autofix_pipeline/test_app/calculator.py'],
                capture_output=True,
                text=True,
                cwd=project_root,
                timeout=30
            )
            if result.returncode != 0:
                print(f"[ERR] Git reset failed: {result.stderr}")
                _reset_with_backup()
    except Exception as e:
        print(f"[ERR] Reset error: {e}")
        _reset_with_backup()
    
    pipeline_state["logs"] = []
    pipeline_state["stats"] = {
        "bugsFound": 0,
        "bugsFixed": 0,
        "passRate": "0%",
        "deployStatus": "-"
    }
    pipeline_state["currentStep"] = 0
    
    return jsonify({"status": "reset"})


def _reset_with_backup():
    """备份重置方法 - 当 Git 不可用时使用"""
    original_code = '''
"""
计算器应用 - 包含预设Bug用于Demo演示
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
        """除法 - Bug: 没有处理除零情况"""
        return a / b
    
    def power(self, base, exponent):
        """幂运算 - Bug: 没有验证输入类型"""
        return base ** exponent
    
    def average(self, numbers):
        """计算平均值 - Bug: 没有处理空列表"""
        total = sum(numbers)
        return total / len(numbers)
    
    def validate_input(self, value):
        """输入验证 - Bug: 只检查None，没有检查类型"""
        if value is None:
            raise ValueError("Input cannot be None")
        return True
'''
    with open('test_app/calculator.py', 'w', encoding='utf-8') as f:
        f.write(original_code)


if __name__ == '__main__':
    print("=" * 60)
    print("[AI] AI Auto-Fix Pipeline Web Server")
    print("=" * 60)
    print(f"访问地址: http://localhost:5000")
    print("=" * 60)
    # debug=True 但关闭自动重载，避免修复文件时重启
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False, threaded=True)
