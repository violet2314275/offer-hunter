#!/bin/bash
echo "==================================="
echo "  Offer 捕手 - 启动脚本"
echo "==================================="

# 检查 Python 是否可用
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未找到 Python3，请先安装 Python 3.8+"
    exit 1
fi

# 安装依赖
echo "[1/3] 正在安装依赖..."
pip3 install -r requirements.txt -q
if [ $? -ne 0 ]; then
    echo "[错误] 依赖安装失败，请检查网络连接"
    exit 1
fi
echo "依赖安装完成！"

# 检查 .env 文件
if [ ! -f .env ]; then
    echo "[警告] 未找到 .env 文件，将使用 .env.example 作为模板..."
    cp .env.example .env
    echo "请编辑 .env 文件，填入你的 DeepSeek API Key"
    ${EDITOR:-nano} .env
fi

# 启动 Streamlit
echo "[2/3] 正在启动 Streamlit 应用..."
echo ""
echo "启动后，浏览器会自动打开 http://localhost:8501"
echo "按 Ctrl+C 可停止服务"
echo ""
streamlit run app.py --server.port 8501
