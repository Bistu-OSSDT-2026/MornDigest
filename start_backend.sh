#!/bin/bash
# ==========================================
# MornDigest - 后端启动脚本
# ==========================================

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# 检查 .env
if [ ! -f ".env" ]; then
  echo "⚠️  未找到 .env 文件"
  echo "📋 复制 .env.example 为 .env..."
  cp .env.example .env
  echo "✅ 已生成 .env，请编辑填入真实 API Key"
  exit 1
fi

# 安装依赖
echo "📦 检查依赖..."
pip install -r backend/requirements.txt -q

# 启动服务
echo ""
echo "🚀 启动 MornDigest FastAPI 后端..."
echo "📖 API 文档: http://localhost:8000/docs"
echo "🌐 Web 前端: http://localhost:8000/"
echo "🔍 健康检查: http://localhost:8000/health"
echo ""

uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
