# 垃圾分类识别系统

基于 MobileNetV2 深度学习模型的智能垃圾分类识别系统，包含用户端和管理端。

## 项目简介

本系统使用 MobileNetV2 模型进行垃圾分类识别，准确率达 80%。支持单张和批量图片识别，提供识别历史、数据统计、知识科普等功能。

### 技术栈

**后端：**
- FastAPI - Web框架
- PyTorch - 深度学习框架
- SQLite - 数据库
- SQLAlchemy - ORM

**前端：**
- Vue 3 - 前端框架
- Element Plus - UI组件库
- ECharts - 数据可视化
- Vite - 构建工具

## 项目结构

```
trash-classify/
├── backend/                 # 后端代码
│   ├── app/
│   │   ├── api/            # API路由
│   │   ├── models/         # 数据库模型
│   │   ├── schemas/        # Pydantic模型
│   │   ├── services/       # 业务逻辑
│   │   ├── core/           # 核心配置
│   │   └── utils/          # 工具函数
│   ├── ml_models/          # 机器学习模型
│   ├── uploads/            # 上传文件存储
│   ├── main.py             # 入口文件
│   ├── init_db.py          # 数据库初始化
│   ├── .env.example        # 环境变量配置模板
│   └── requirements.txt    # Python依赖
├── frontend/               # 前端代码（用户端+管理端）
│   ├── src/
│   │   ├── views/          # 页面组件
│   │   ├── components/     # 公共组件
│   │   ├── router/         # 路由配置
│   │   ├── store/          # 状态管理
│   │   └── api/            # API接口
│   └── package.json
├── model/                  # 模型文件和训练脚本
│   ├── best_model.pth      # 训练好的模型
│   ├── train.py            # 训练脚本
│   └── classname.txt       # 类别名称
├── data/                   # 数据集文件
│   ├── train.csv           # 训练集
│   ├── val.csv             # 验证集
│   └── test.csv            # 测试集
├── docs/                   # 项目文档
│   ├── 开发方案.md          # 详细开发方案
│   └── 快速启动指南.md      # 快速启动指南
├── .gitignore              # Git忽略文件配置
└── README.md
```

## 快速开始

### 环境要求

- Python 3.8+
- Node.js 16+
- pip
- npm

### 1. 后端启动

```bash
# 进入后端目录
cd backend

# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 复制环境变量配置文件
cp .env.example .env

# 初始化数据库（创建表和默认管理员账号）
python init_db.py

# 启动后端服务
python main.py
# 或使用 uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

后端服务将在 http://localhost:8000 启动

API文档：http://localhost:8000/docs

### 2. 前端启动

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端将在 http://localhost:5173 启动（包含用户端和管理端）

### 3. 默认账号

**管理员账号：**
- 用户名：admin
- 密码：123456

**注意：** 生产环境请立即修改默认密码！

## 主要功能

### 用户端功能

1. **智能识别**
   - 单张图片识别（游客可用）
   - 批量图片识别（需登录）
   - 实时摄像头识别
   - Top-3 预测结果展示

2. **识别历史**（需登录）
   - 查看历史识别记录
   - 删除记录
   - 筛选和搜索

3. **数据统计**（需登录）
   - 个人识别次数统计
   - 分类占比图表
   - 识别趋势分析

4. **知识科普**（游客可用）
   - 垃圾分类知识库
   - 分类浏览
   - 处理建议

5. **用户中心**（需登录）
   - 个人信息管理
   - 修改密码

### 管理端功能

1. **数据概览**
   - 全局统计数据
   - 分类统计图表
   - 识别趋势分析

2. **识别记录管理**
   - 查看所有识别记录
   - 数据导出

3. **用户管理**
   - 用户列表
   - 启用/禁用用户

4. **反馈管理**
   - 查看用户反馈
   - 处理错误标注

5. **知识库管理**
   - 添加/编辑知识条目
   - 分类管理

## API接口

### 认证相关
- `POST /api/auth/register` - 用户注册
- `POST /api/auth/login` - 用户登录
- `GET /api/auth/me` - 获取当前用户信息

### 识别相关
- `POST /api/predict/single` - 单张图片识别
- `POST /api/predict/batch` - 批量识别
- `GET /api/predict/history` - 获取识别历史
- `DELETE /api/predict/{id}` - 删除识别记录

### 统计相关
- `GET /api/stats/user` - 用户统计
- `GET /api/stats/global` - 全局统计（管理员）

详细API文档请访问：http://localhost:8000/docs

## 开发指南

### 后端开发

1. 添加新的API路由：在 `backend/app/api/` 目录下创建新文件
2. 添加数据库模型：在 `backend/app/models/database.py` 中定义
3. 添加Pydantic模型：在 `backend/app/schemas/` 目录下创建
4. 业务逻辑：在 `backend/app/services/` 目录下实现

### 前端开发

1. 添加新页面：在 `src/views/` 目录下创建 Vue 组件
2. 添加路由：在 `src/router/index.js` 中配置
3. 添加API接口：在 `src/api/` 目录下定义
4. 状态管理：在 `src/store/` 目录下使用 Pinia

## 部署

### 生产环境部署

1. **后端部署**

```bash
# 安装依赖
pip install -r requirements.txt

# 修改配置文件
# 修改 .env 中的 SECRET_KEY 和其他配置

# 使用 gunicorn 部署
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

2. **前端部署**

```bash
# 进入前端目录
cd frontend
npm run build
# 将 dist 目录部署到 Web 服务器
```

3. **使用 Nginx 反向代理**

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 前端静态文件
    location / {
        root /path/to/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # API代理
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # 上传文件
    location /uploads {
        proxy_pass http://localhost:8000;
    }
}
```

## 常见问题

### Q1: 模型加载失败？
A: 确保 `best_model.pth` 文件在正确的位置，检查 `.env` 中的 `MODEL_PATH` 配置。

### Q2: 前端无法连接后端？
A: 检查后端是否正常启动，确认端口号是否正确，查看浏览器控制台的错误信息。

### Q3: 数据库初始化失败？
A: 删除 `trash_classify.db` 文件，重新运行 `python init_db.py`。

### Q4: 图片上传失败？
A: 检查 `uploads` 目录是否存在且有写入权限，确认文件大小不超过限制（默认10MB）。

### Q5: 如何修改模型类别数量？
A: 修改 `.env` 中的 `NUM_CLASSES` 参数，并更新模型文件。

## 性能优化建议

1. **模型推理优化**
   - 使用 GPU 加速（如果可用）
   - 模型量化
   - 批量推理

2. **数据库优化**
   - 添加索引
   - 使用连接池
   - 定期清理历史数据

3. **前端优化**
   - 图片懒加载
   - 路由懒加载
   - 使用 CDN

4. **缓存策略**
   - Redis 缓存热点数据
   - 浏览器缓存静态资源

## 安全建议

1. 修改默认管理员密码
2. 使用强密码策略
3. 启用 HTTPS
4. 配置 CORS 白名单
5. 定期备份数据库
6. 限制文件上传大小和类型
7. 使用环境变量管理敏感信息

## 贡献指南

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License

## 联系方式

如有问题，请联系：[你的邮箱]

---

**注意：** 本项目为毕业设计项目，仅供学习和研究使用。
