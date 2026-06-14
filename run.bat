@echo off
echo ===================================
echo   Offer 捕手 - 启动脚本
echo ===================================

REM 检查 Python 是否可用
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python，请先安装 Python 3.8+
    pause
    exit /b 1
)

REM 安装依赖
echo [1/3] 正在安装依赖...
pip install -r requirements.txt -q
if errorlevel 1 (
    echo [错误] 依赖安装失败，请检查网络连接
    pause
    exit /b 1
)
echo 依赖安装完成！

REM 检查 .env 文件
if not exist .env (
    echo [警告] 未找到 .env 文件，将使用 .env.example 作为模板...
    copy .env.example .env
    echo 请编辑 .env 文件，填入你的 DeepSeek API Key
    notepad .env
)

REM 启动 Streamlit
echo [2/3] 正在启动 Streamlit 应用...
echo.
echo 启动后，浏览器会自动打开 http://localhost:8501
echo 按 Ctrl+C 可停止服务
echo.
streamlit run app.py --server.port 8501

pause
