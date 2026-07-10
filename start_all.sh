#!/bin/bash
# 一键启动前后端
cd "$(dirname "$0")"

# 把 Python 用户 bin 加入 PATH（macOS 上 streamlit/uvicorn 默认装这里）
export PATH="$HOME/Library/Python/3.13/bin:$PATH"

# 检查命令是否存在
if ! command -v uvicorn >/dev/null 2>&1; then
  echo "❌ uvicorn 未安装，请先执行："
  echo "   pip3 install -r backend/requirements.txt -r requirements.txt"
  exit 1
fi
if ! command -v streamlit >/dev/null 2>&1; then
  echo "❌ streamlit 未安装，请先执行："
  echo "   pip3 install -r backend/requirements.txt -r requirements.txt"
  exit 1
fi

trap "kill 0" EXIT

echo "🚀 启动 FastAPI 后端（端口 8000）..."
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

sleep 3

echo "🚀 启动 Streamlit 前端（端口 8501）..."
streamlit run run.py --server.headless true &
FRONTEND_PID=$!

echo ""
echo "================================================"
echo "✅ MornDigest 服务已全部启动！"
echo "================================================"
echo "   🖥️  前端 UI:  http://localhost:8501"
echo "   ⚙️  后端 API: http://localhost:8000"
echo "   📖  API 文档: http://localhost:8000/docs   ⭐"
echo "   💚  健康检查: http://localhost:8000/health"
echo "================================================"
echo "按 Ctrl+C 停止所有服务"
echo ""

wait
