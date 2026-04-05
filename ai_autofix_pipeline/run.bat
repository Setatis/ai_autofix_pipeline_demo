@echo off
chcp 65001 >nul
cd /d %~dp0
echo ============================================================
echo    AI Auto-Fix Pipeline - 智能体自动修复系统
echo ============================================================
echo.
echo 正在启动 Pipeline...
echo.
set PYTHONIOENCODING=utf-8
python demo_full_pipeline.py
echo.
echo ============================================================
echo Pipeline 执行完成！
echo 请查看 reports 目录获取详细报告
echo ============================================================
pause
