# RAG 知识库管理系统

## 简介

RAG (Retrieval-Augmented Generation) 系统允许 AI 助手基于上传的文档回答问题，提供更准确、更具体的答案。

## 快速开始

### 1. 安装依赖

```bash
pip install chromadb sentence-transformers
```

### 2. 配置环境变量

在 `backend/.env` 中添加：

```
ENABLE_RAG=true
DASHSCOPE_API_KEY=你的通义千问API密钥
```

### 3. 使用方法

**管理员操作：**
1. 登录管理后台
2. 进入"知识库管理"页面
3. 上传 .md 或 .txt 文件（垃圾分类相关知识）
4. 等待处理完成（状态变为"已完成"）

**用户使用：**
1. 进入 AI 助手页面
2. 提问相关问题
3. AI 会基于上传的文档回答

## 工作原理

```
上传文档 → 文本分块 → 生成向量嵌入 → 存入 ChromaDB
用户提问 → 向量搜索 → 检索相关文档 → 组合上下文 → AI 生成回答
```

## 技术栈

- **向量数据库**: ChromaDB
- **嵌入模型**: paraphrase-multilingual-MiniLM-L12-v2
- **AI 模型**: 通义千问
- **文本分块**: 800字符/块，重叠100字符

## API 接口

- `POST /api/admin/knowledge/upload` - 上传文档
- `GET /api/admin/knowledge` - 获取文档列表
- `DELETE /api/admin/knowledge/{id}` - 删除文档

## 文件说明

- `app/services/vector_store.py` - 向量库操作
- `app/services/document_processor.py` - 文档处理
- `app/services/ai_service.py` - AI 服务（集成 RAG）
- `app/api/knowledge.py` - 知识库管理接口
