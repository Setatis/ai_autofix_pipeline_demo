"""
AI Auto-Fix Pipeline - 完整演示脚本

展示完整的Bug自动修复流程:
1. 监控检测 -> 2. 问题提交 -> 3. AI分析 -> 4. AI修复 -> 5. 自动部署 -> 6. 验证测试 -> 7. 生成报告
"""
import os
import sys
import io
import yaml
from datetime import datetime

# 设置标准输出编码为 UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.monitor import Monitor
from core.issue_generator import IssueGenerator
from core.ai_analyzer import AIAnalyzer
from core.ai_fixer import AIFixer
from core.deployer import Deployer
from core.verifier import Verifier
from core.reporter import Reporter


class AutoFixPipeline:
    """自动修复Pipeline"""
    
    def __init__(self, config_path: str = "config.yaml"):
        """初始化Pipeline"""
        # 加载配置
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        # 初始化各模块
        self.monitor = Monitor()
        self.issue_generator = IssueGenerator()
        self.ai_analyzer = AIAnalyzer(self.config.get('api', {}))
        self.ai_fixer = AIFixer(self.config.get('api', {}))
        self.deployer = Deployer(self.config.get('pipeline', {}))
        self.verifier = Verifier()
        self.reporter = Reporter(self.config.get('report', {}).get('output_dir', 'reports'))
        
        # Pipeline数据收集
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
        """执行完整Pipeline"""
        print("\n" + "="*60)
        print("[AI] AI Auto-Fix Pipeline - 智能体自动修复系统")
        print("="*60)
        print(f"启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            # 步骤1: 监控检测
            test_results = self.monitor.run_tests()
            failures = self.monitor.detect_failures(test_results)
            
            if not failures:
                print("\n[OK] 所有测试通过,无需修复!")
                return
            
            # 步骤2: 生成Bug报告
            print("\n" + "="*60)
            print("[+] 步骤2: 生成Bug报告")
            print("="*60)
            
            for failure in failures:
                issue = self.issue_generator.generate_issue(failure, test_results)
                self.pipeline_data["issues"].append(issue)
                print(f"   [*] 已生成Issue: {issue['id']}")
            
            print(f"\n[OK] 共生成 {len(self.pipeline_data['issues'])} 个Issue")
            
            # 步骤3-6: 对每个Bug执行分析->修复->部署->验证
            for issue in self.pipeline_data["issues"]:
                print("\n" + "="*60)
                print(f"[>] 处理 {issue['id']}")
                print("="*60)
                
                # 读取源代码
                source_code = self._read_source_code("test_app/calculator.py")
                
                # 步骤3: AI分析
                analysis = self.ai_analyzer.analyze_bug(issue, source_code)
                self.pipeline_data["analyses"].append(analysis)
                
                # 步骤4: AI修复
                fix_result = self.ai_fixer.generate_fix(issue, analysis, source_code)
                if fix_result.get("success"):
                    # 应用修复
                    success = self.ai_fixer.apply_fix(fix_result, "test_app/calculator.py")
                    fix_result["applied"] = success
                    self.pipeline_data["fixes"].append(fix_result)
                    
                    if success:
                        # 步骤5: 部署
                        deployment = self.deployer.deploy(fix_result)
                        self.pipeline_data["deployment"] = deployment
                        
                        if deployment.get("success"):
                            # 步骤6: 验证
                            verification = self.verifier.verify_fix(issue)
                            self.pipeline_data["verifications"].append(verification)
            
            # 步骤7: 运行完整测试套件
            final_tests = self.verifier.run_full_test_suite()
            self.pipeline_data["final_tests"] = final_tests
            
            # 步骤8: 生成报告
            self.pipeline_data["end_time"] = datetime.now().isoformat()
            report_file = self.reporter.generate_report(self.pipeline_data)
            
            # 输出总结
            self._print_summary()
            
        except Exception as e:
            print(f"\n[ERR] Pipeline执行失败: {e}")
            import traceback
            traceback.print_exc()
    
    def _read_source_code(self, file_path: str) -> str:
        """读取源代码文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"[ERR] 读取文件失败 {file_path}: {e}")
            return ""
    
    def _print_summary(self):
        """打印执行总结"""
        print("\n" + "="*60)
        print("[*] Pipeline执行总结")
        print("="*60)
        
        print(f"\n[TIME] 执行时间:")
        print(f"   开始: {self.pipeline_data['start_time']}")
        print(f"   结束: {self.pipeline_data['end_time']}")
        
        print(f"\n[BUG] Bug处理:")
        print(f"   发现: {len(self.pipeline_data['issues'])} 个")
        print(f"   分析: {len(self.pipeline_data['analyses'])} 个")
        print(f"   修复: {len(self.pipeline_data['fixes'])} 个")
        
        successful_fixes = len([f for f in self.pipeline_data['fixes'] if f.get('applied')])
        print(f"   应用: {successful_fixes} 个")
        
        successful_verifications = len([v for v in self.pipeline_data['verifications'] if v.get('success')])
        print(f"   验证通过: {successful_verifications} 个")
        
        print(f"\n[DEPLOY] 部署状态: {'[OK] 成功' if self.pipeline_data['deployment'].get('success') else '[ERR] 失败'}")
        
        final_tests = self.pipeline_data.get('final_tests', {})
        print(f"\n[TEST] 最终测试:")
        print(f"   通过: {final_tests.get('passed', 0)}")
        print(f"   失败: {final_tests.get('failed', 0)}")
        
        print("\n" + "="*60)
        print("[OK] Pipeline执行完成!")
        print("="*60)


def main():
    """主函数"""
    # 检查配置
    config_path = "config.yaml"
    if not os.path.exists(config_path):
        print(f"[ERR] 配置文件不存在: {config_path}")
        sys.exit(1)
    
    # 创建并运行Pipeline
    pipeline = AutoFixPipeline(config_path)
    pipeline.run()


if __name__ == "__main__":
    main()
