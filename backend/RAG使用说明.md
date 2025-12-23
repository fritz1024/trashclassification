# RAG（检索增强生成）使用说明

## 什么是 RAG？

RAG（Retrieval-Augmented Generation）是一种让 AI 助手能够基于项目真实文档回答问题的技术。

**优势：**
- ✅ 回答更准确：基于项目实际文档，而不是手动编写的提示词
- ✅ 信息最新：文档更新后重新初始化即可，AI 自动获取最新信息
- ✅ 可扩展：可以添加更多文档到知识库

## 安装步骤

### 1. 安装依赖包

```powershell
cd backend
pip install -r requirements.txt
```

**注意：** 首次安装会下载嵌入模型（约 500MB），需要一些时间。

### 2. 初始化知识库

```powershell
python init_rag.py
```

这个脚本会：
1. 清空现有的向量数据库
2. 加载项目文档（README.md 等）
3. 将文档分割成小块
4. 生成向量嵌入并存储到数据库

**首次运行可能需要 5-10 分钟**（下载和加载嵌入模型）

### 3. 启动后端服务

```powershell
python main.py
```

现在 AI 助手就可以基于项目文档回答问题了！

## 工作原理

```
用户提问 → 向量检索 → 找到相关文档 → 注入到 AI 提示词 → AI 基于文档回答
```

**示例：**

用户问："如何使用识别功能？"

1. 系统从 README.md 中检索到相关章节
2. 将这些章节作为参考文档提供给 AI
3. AI 基于真实文档内容回答，而不是猜测

## 添加更多文档

如果你想让 AI 助手了解更多内容，可以：

1. 编辑 `backend/app/services/document_loader.py`
2. 在 `prepare_knowledge_base` 函数中添加更多文档路径：

```python
doc_files = [
    os.path.join(project_root, 'README.md'),
    os.path.join(project_root, 'docs', '开发方案.md'),  # 添加这行
    os.path.join(project_root, 'docs', '快速启动指南.md'),  # 添加这行
]
```

3. 重新运行 `python init_rag.py` 初始化知识库

## 更新知识库

当你修改了项目文档（如 README.md）后，需要重新初始化知识库：

```powershell
python init_rag.py
```

## 技术栈

- **ChromaDB**: 向量数据库，用于存储文档嵌入
- **Sentence Transformers**: 生成文本嵌入向量
- **paraphrase-multilingual-MiniLM-L12-v2**: 支持中文的嵌入模型

## 常见问题

### Q1: 初始化很慢？
A: 首次运行会下载嵌入模型（约 500MB），之后就快了。

### Q2: AI 回答不准确？
A: 检查 README.md 中的信息是否完整，然后重新运行 `python init_rag.py`

### Q3: 如何禁用 RAG？
A: 如果不想使用 RAG，不运行 `init_rag.py` 即可。AI 会使用默认的系统提示词。

### Q4: 向量数据库存储在哪里？
A: 存储在 `backend/chroma_db/` 目录，可以安全删除后重新初始化。

## 文件说明

- `backend/app/services/vector_store.py` - 向量数据库服务
- `backend/app/services/document_loader.py` - 文档加载和分割工具
- `backend/app/services/ai_service.py` - AI 服务（已集成 RAG）
- `backend/init_rag.py` - 知识库初始化脚本
- `backend/chroma_db/` - 向量数据库存储目录（自动创建）

## 测试 RAG 功能

初始化完成后，在前端 AI 助手中测试：

- 问："平台有哪些功能？" → 应该基于 README 准确回答
- 问："如何使用识别功能？" → 应该给出详细步骤
- 问："默认管理员账号是什么？" → 应该回答 admin / 123456

如果回答准确，说明 RAG 工作正常！
