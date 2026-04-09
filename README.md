# 垃圾分类识别系统 (Trash Classification System)

基于深度学习（PyTorch + MobileNetV2）和 大语言模型 RAG（检索增强生成）的垃圾分类与智能问答系统。项目包含 Web 端（用户端 + 管理后台）和微信小程序端。

## ✨ 核心功能

*   **智能识别**：支持单张/批量图片上传，利用离线训练的深度学习模型进行高精度垃圾分类识别。
*   **AI 助手 (RAG)**：基于通义千问大模型和本地 ChromaDB 向量知识库，提供垃圾分类相关的智能问答。
*   **多端支持**：提供 Vue3 响应式 Web 页面（涵盖用户中心与管理后台）以及 uni-app 跨平台小程序。
*   **后台管理**：支持用户管理、识别记录管理、反馈处理、知识库文档管理及模型配置等功能。

## 📂 项目结构

```text
trashclassification/
├── backend/                 # 后端代码 (FastAPI + PyTorch)
│   ├── app/                 # 核心业务逻辑与 API 路由
│   ├── db/                  # 数据库文件及初始化脚本
│   ├── ml_models/           # 机器学习模型权重目录
│   ├── uploads/             # 上传的图片与知识库文档存储
│   └── main.py              # 后端服务入口
├── frontend/                # Web 前端工程 (Vue 3 + Element Plus)
├── miniprogram/             # 小程序工程 (uni-app)
├── model_training/          # 离线模型训练脚本
├── data/                    # 训练与验证数据集

```

## 🚀 快速启动

### 1. 后端服务 (Backend)

环境要求：Python 3.8+

```bash
# 进入后端目录
cd backend

# 创建并激活虚拟环境 (可选但推荐)
python -m venv venv
source venv/bin/activate  # Windows 用户使用 venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量（可选，修改 .env 文件中的配置如 DASHSCOPE_API_KEY）
cp .env.example .env

# 初始化数据库（将自动创建默认管理员账号和数据表）
python db/init_db.py

# 启动后端服务
python main.py
# 或者使用: uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

后端服务将在 `http://localhost:8000` 启动，API 接口文档可通过 `http://localhost:8000/docs` 查看。

### 2. Web 前端 (Frontend)

环境要求：Node.js 16+

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端将在 `http://localhost:5173` 启动。
*   用户端入口：`http://localhost:5173/`
*   管理端入口：`http://localhost:5173/admin`

### 3. 小程序端 (Miniprogram)

环境要求：Node.js 16+, 微信开发者工具

```bash
# 进入小程序目录
cd miniprogram

# 安装依赖
npm install

# 编译到微信小程序
npm run dev:mp-weixin
```

编译完成后，使用微信开发者工具导入 `miniprogram/dist/dev/mp-weixin` 目录即可进行预览和调试。

## 默认账号

数据库初始化（`python db/init_db.py`）后，默认生成以下账号：

*   **超级管理员**：
    *   用户名：`superadmin`
    *   密码：`123456`
*   **普通管理员**：
    *   用户名：`admin`
    *   密码：`123456`

*(注：普通用户可通过 Web 端或小程序端自行注册)*

## ❓ 常见问题 (FAQ)

**Q1: AI 助手无法回复或提示服务不可用？**
A: 检查 `backend/.env` 中的 `DASHSCOPE_API_KEY` 是否已正确配置，并确认后端网络能正常访问阿里云通义千问接口。

**Q2: 向量知识库功能怎么使用？**
A: 在管理后台 -> 知识库管理中上传 `.md` 或 `.txt` 格式的文档，系统会自动将其切分并存入向量数据库 (`backend/chroma_db`)。上传完成后，AI 助手在回答用户问题时会自动检索并参考这些文档。

**Q3: 数据库初始化失败？**
A: 确保 `backend/db/` 目录有写入权限。如果需要重置整个数据库，可以删除 `backend/db/trash_classify.db` 文件，然后重新运行 `python db/init_db.py`。

**Q4: 图片或知识库文档上传失败？**
A: 检查 `backend/uploads` 目录是否存在且有写入权限，同时确认文件大小没有超过系统限制（默认 10MB）。
