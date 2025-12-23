"""
初始化 RAG 知识库
将项目文档加载到向量数据库中
"""
import os
import sys

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.vector_store import vector_store
from app.services.document_loader import prepare_knowledge_base
from app.core.logger import logger


def init_knowledge_base():
    """初始化知识库"""
    try:
        logger.info("=" * 50)
        logger.info("开始初始化 RAG 知识库...")
        logger.info("=" * 50)

        # 获取项目根目录
        backend_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(backend_dir)

        logger.info(f"项目根目录: {project_root}")

        # 清空现有知识库
        logger.info("清空现有知识库...")
        vector_store.clear()

        # 准备文档
        logger.info("加载和分割文档...")
        chunks = prepare_knowledge_base(project_root)

        if not chunks:
            logger.error("没有找到任何文档，初始化失败")
            return False

        logger.info(f"共准备了 {len(chunks)} 个文档块")

        # 添加到向量数据库
        logger.info("将文档添加到向量数据库...")
        documents = [chunk['content'] for chunk in chunks]
        metadatas = [chunk['metadata'] for chunk in chunks]
        ids = [f"chunk_{i}" for i in range(len(chunks))]

        vector_store.add_documents(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )

        # 验证
        count = vector_store.get_count()
        logger.info(f"知识库中现有 {count} 个文档块")

        logger.info("=" * 50)
        logger.info("✅ RAG 知识库初始化完成！")
        logger.info("=" * 50)

        # 测试搜索
        logger.info("\n测试搜索功能...")
        test_queries = [
            "如何使用识别功能？",
            "平台有哪些功能？",
            "如何注册账号？"
        ]

        for query in test_queries:
            results = vector_store.search(query, n_results=2)
            logger.info(f"\n查询: {query}")
            logger.info(f"找到 {len(results)} 个相关文档")
            if results:
                logger.info(f"最相关文档预览: {results[0]['content'][:100]}...")

        return True

    except Exception as e:
        logger.error(f"初始化知识库失败: {str(e)}", exc_info=True)
        return False


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("RAG 知识库初始化工具")
    print("=" * 60)
    print("\n这将：")
    print("1. 清空现有的向量数据库")
    print("2. 加载项目文档（README.md 等）")
    print("3. 将文档分割成小块")
    print("4. 生成向量嵌入并存储到数据库")
    print("\n注意：首次运行会下载嵌入模型，可能需要几分钟时间\n")

    confirm = input("确认执行？(y/n): ")
    if confirm.lower() == 'y':
        success = init_knowledge_base()
        if success:
            print("\n✅ 初始化成功！AI 助手现在可以基于项目文档回答问题了。")
        else:
            print("\n❌ 初始化失败，请查看日志了解详情。")
    else:
        print("已取消操作")
