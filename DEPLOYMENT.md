# 🚀 MornDigest 公网部署指南

本指南教你把 MornDigest 部署到公网，让**任何人任何时间**都能访问，**不需要你的电脑开着**。

---

## 🎯 推荐方案：前端 Streamlit Cloud + 后端 Render（永久免费）

| 组件 | 平台 | 费用 | 地址样例 |
|------|------|------|---------|
| 前端 (Streamlit) | [share.streamlit.io](https://share.streamlit.io) | 免费 | `https://morndigest.streamlit.app` |
| 后端 (FastAPI) | [render.com](https://render.com) | 免费额度 | `https://morndigest-backend.onrender.com` |

---

## 📦 前置准备（一次性）

### 1. 注册账号
- **GitHub** 账号：你已经有了（`zhangnaowan-lht`）
- **Streamlit Cloud**：用 GitHub 登录 https://share.streamlit.io
- **Render**：用 GitHub 登录 https://render.com

### 2. 准备 API Key
确保 `.env` 里有这些值（部署时需要用到）：
```bash
ANTHROPIC_API_KEY=sk-ant-xxx
ANTHROPIC_BASE_URL=https://api.anthropic.com
QWEATHER_KEY=你的和风天气key
QWEATHER_API_HOST=mt3aartb6n.re.qweatherapi.com
NEWS_KEY=你的聚合数据key
```

---

## 🚀 部署步骤

### Step 1：推送代码到 GitHub（已完成 ✅）

代码已经在 `Bistu-OSSDT-2026/MornDigest` 仓库的 `main` 分支。

### Step 2：部署后端到 Render

1. 登录 https://dashboard.render.com
2. 点击 **New +** → **Blueprint**
3. 选择 **Connect repository** → 选 `Bistu-OSSDT-2026/MornDigest`
4. Render 会自动识别项目根目录的 `render.yaml`
5. 点击 **Apply** 开始部署
6. 等待 5-10 分钟，部署成功后你会得到一个 URL，例如：
   ```
   https://morndigest-backend.onrender.com
   ```
7. **填写环境变量**（在 Render Dashboard → Environment）：
   - `ANTHROPIC_API_KEY`：你的 Claude Key
   - `QWEATHER_KEY`：你的和风天气 Key
   - `NEWS_KEY`：你的聚合数据 Key
   - 其他已有默认值不用改
8. 测试后端：访问 `https://morndigest-backend.onrender.com/health`

### Step 3：部署前端到 Streamlit Cloud

1. 登录 https://share.streamlit.io
2. 点击 **New app**
3. 填写：
   - **Repository**：`Bistu-OSSDT-2026/MornDigest`
   - **Branch**：`main`
   - **Main file path**：`run.py`
   - **App URL**（自定义）：`morndigest`（最终地址会是 `morndigest.streamlit.app`）
4. 点击 **Advanced settings** → **Secrets**，粘贴：
   ```toml
   MORNDIGEST_API_URL = "https://morndigest-backend.onrender.com"
   ```
   ⚠️ 把这个 URL 换成 Step 2 拿到的真实后端地址
5. 点击 **Deploy!**
6. 等待 3-5 分钟，部署成功后访问：
   ```
   https://morndigest.streamlit.app
   ```

---

## ✅ 完成！永久公网地址

任何人任何时间都可以打开：

```
🌐 https://morndigest.streamlit.app
```

而且这个地址**永远不变**，即使你电脑关机了也能用。

---

## 🔄 后续更新代码

直接 `git push` 到 `main` 分支，两个平台都会自动重新部署：
```bash
cd /Users/lhtt/Desktop/MornDigest
git add .
git commit -m "更新说明"
git push origin main
```

---

## 🆘 常见问题

### Q1：免费版 Render 有什么限制？
A：免费版会在 15 分钟无访问后休眠，下次访问需要 30 秒唤醒。日常使用没问题。

### Q2：Streamlit Cloud 有什么限制？
A：1GB 内存、无限带宽、永久免费。比个人电脑 7×24 开着的体验还好。

### Q3：想绑定自己的域名（如 morndigest.com）？
A：两个平台都支持自定义域名，DNS 加个 CNAME 记录即可。

### Q4：API Key 安全吗？
A：完全安全。两个平台都通过加密的 Secrets 管理，不会泄露到代码里。

---

## 🎁 备选方案

如果不想用 Streamlit Cloud + Render，还可以：

### 方案 B：云服务器一键部署（更可控）
```bash
# 1. 买云服务器（阿里云/腾讯云学生机 ¥9.9/月）
# 2. SSH 连上
ssh root@你的服务器IP

# 3. 一键部署
curl -O https://raw.githubusercontent.com/Bistu-OSSDT-2026/MornDigest/main/deploy_cloud.sh
bash deploy_cloud.sh
```

### 方案 C：临时演示（5分钟搞定）
```bash
# 本机起隧道，无需任何账号
ssh -R 80:127.0.0.1:8501 serveo.net
# 会得到一个 https://xxx.serveousercontent.com 临时地址
```
