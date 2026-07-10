#!/bin/bash
# ==========================================
# MornDigest 云服务器一键部署脚本
# 适用系统：Ubuntu 22.04 / Debian 11
# 用法：ssh root@服务器IP 后执行此脚本
# ==========================================

set -e

echo "============================================="
echo "🚀 MornDigest 云服务器一键部署"
echo "============================================="

# 1. 更新系统
echo "📦 更新系统..."
apt update -y && apt upgrade -y

# 2. 安装 Python 和依赖
echo "🐍 安装 Python 3.11..."
apt install -y python3 python3-pip python3-venv git nginx

# 3. 克隆代码（你的仓库已经 push 到 GitHub）
echo "📥 克隆项目代码..."
cd /opt
if [ ! -d "MornDigest" ]; then
  git clone https://github.com/Bistu-OSSDT-2026/MornDigest.git
  cd MornDigest
else
  cd MornDigest
  git pull origin main
fi

# 4. 创建虚拟环境
echo "🔧 创建 Python 虚拟环境..."
python3 -m venv venv
source venv/bin/activate

# 5. 安装依赖
echo "📦 安装 Python 依赖..."
pip install --upgrade pip -q
pip install -r backend/requirements.txt -r requirements.txt -q

# 6. 创建 .env
if [ ! -f ".env" ]; then
  echo "⚠️  创建 .env 文件，请稍后编辑填入 API Key..."
  cp .env.example .env
  echo "📝 完成后请执行：nano /opt/MornDigest/.env"
fi

# 7. 创建 systemd 服务（开机自启）
echo "⚙️  创建 systemd 服务..."

cat > /etc/systemd/system/morndigest-backend.service << 'SERVICE'
[Unit]
Description=MornDigest FastAPI Backend
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/MornDigest
Environment="PATH=/opt/MornDigest/venv/bin:/usr/bin"
ExecStart=/opt/MornDigest/venv/bin/uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 2
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
SERVICE

cat > /etc/systemd/system/morndigest-frontend.service << 'SERVICE'
[Unit]
Description=MornDigest Streamlit Frontend
After=network.target morndigest-backend.service

[Service]
Type=simple
User=root
WorkingDirectory=/opt/MornDigest
Environment="PATH=/opt/MornDigest/venv/bin:/usr/bin"
ExecStart=/opt/MornDigest/venv/bin/streamlit run run.py --server.port 8501 --server.address 0.0.0.0 --server.headless true
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
SERVICE

# 8. 配置 Nginx 反向代理（让 80 端口能访问前端+API）
echo "🌐 配置 Nginx 反向代理..."

cat > /etc/nginx/sites-available/morndigest << 'NGINX'
server {
    listen 80;
    server_name _;

    # 前端
    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # API 文档
    location /docs {
        proxy_pass http://127.0.0.1:8000/docs;
    }
    location /openapi.json {
        proxy_pass http://127.0.0.1:8000/openapi.json;
    }

    # API 接口
    location /api/ {
        proxy_pass http://127.0.0.1:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # 健康检查
    location /health {
        proxy_pass http://127.0.0.1:8000/health;
    }
}
NGINX

ln -sf /etc/nginx/sites-available/morndigest /etc/nginx/sites-enabled/morndigest
rm -f /etc/nginx/sites-enabled/default

# 9. 启动服务
echo "🚀 启动所有服务..."
systemctl daemon-reload
systemctl enable morndigest-backend morndigest-frontend nginx
systemctl start morndigest-backend
sleep 3
systemctl start morndigest-frontend
systemctl restart nginx

# 10. 配置防火墙
echo "🔓 开放防火墙端口..."
ufw allow 80/tcp 2>/dev/null || true
ufw allow 22/tcp 2>/dev/null || true

echo ""
echo "============================================="
echo "✅ 部署完成！"
echo "============================================="
echo ""
echo "📝 下一步：编辑 .env 填入 API Key"
echo "   nano /opt/MornDigest/.env"
echo "   （填完后执行：systemctl restart morndigest-backend）"
echo ""
echo "🌐 访问地址（替换 YOUR_IP 为你的服务器 IP）："
echo "   前端:  http://YOUR_IP/"
echo "   API:   http://YOUR_IP/docs"
echo "   健康:  http://YOUR_IP/health"
echo ""
echo "🔧 常用管理命令："
echo "   systemctl status morndigest-backend   # 查看后端状态"
echo "   systemctl status morndigest-frontend  # 查看前端状态"
echo "   journalctl -u morndigest-backend -f   # 查看后端日志"
echo "   systemctl restart morndigest-backend  # 重启后端"
echo "============================================="
