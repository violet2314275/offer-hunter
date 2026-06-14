# 🌐 Offer 捕手 - 部署指南

## 方案 A：Streamlit Cloud（推荐，免费 + 简单）

### 步骤

1. **推送代码到 GitHub**
   ```bash
   cd offer_hunter
   git init
   git add .
   git commit -m "Initial commit: Offer 捕手 v1.0"
   # 在 GitHub 上创建新仓库，然后：
   git remote add origin https://github.com/你的用户名/offer-hunter.git
   git push -u origin main
   ```

2. **访问 Streamlit Cloud**
   - 打开 https://share.streamlit.io
   - 用 GitHub 登录
   - 点击 "New app"

3. **配置部署**
   - Repository: 选择你刚推送的仓库
   - Branch: `main`
   - Main file path: `app.py`
   - 点击 "Advanced settings"

4. **配置密钥（重要！）**
   在 "Secrets" 中添加：
   ```toml
   DEEPSEEK_API_KEY = "sk-你的DeepSeek密钥"
   DEEPSEEK_BASE_URL = "https://api.deepseek.com"
   DEEPSEEK_MODEL = "deepseek-chat"
   ```

5. **点击 "Deploy"**
   - 等待 2-3 分钟
   - 获得公网链接：`https://xxx.streamlit.app`

---

## 方案 B：Vercel / Netlify（不适合）

> ⚠️ Streamlit 是 Python 服务端应用，不能用纯静态托管平台部署。

---

## 方案 C：自己的服务器（VPS）

如果有腾讯云/阿里云服务器：

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置 .env 文件（填入 API Key）

# 3. 后台运行（使用 nohup 或 screen）
nohup streamlit run app.py --server.port 8501 --server.address 0.0.0.0 &

# 4. 配置 Nginx 反向代理（可选）
```

Nginx 配置示例：
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 🔒 安全提示

- **不要**将 `.env` 文件推送到 GitHub（已经在 `.gitignore` 中）
- **不要**将 API Key 写进代码
- 部署时只用 Streamlit Cloud 的 "Secrets" 功能配置密钥

---

## 📋 交付检查清单

- [ ] 代码已推送到 GitHub 公开仓库
- [ ] Streamlit Cloud 部署成功
- [ ] 获得公网可访问链接
- [ ] 方案说明 PDF/DOC 已撰写
- [ ] （可选）演示视频已录制
