"""
向量数据库服务 - 用于 RAG 检索
"""
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from typing import List, Dict
from app.core.logger import logger
import os


class VectorStore:
    """向量数据库服务类"""

    def __init__(self, persist_directory: str = "./chroma_db"):
        """
        初始化向量数据库

        Args:
            persist_directory: 数据库持久化目录
        """
        self.persist_directory = persist_directory

        # 创建持久化目录
        os.makedirs(persist_directory, exist_ok=True)

        # 初始化 ChromaDB 客户端
        self.client = chromadb.Client(Settings(
            persist_directory=persist_directory,
            anonymized_telemetry=False
        ))

        # 初始化嵌入模型（使用中文模型）
        logger.info("正在加载嵌入模型...")
        self.embedding_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        logger.info("嵌入模型加载完成")

        # 获取或创建集合
        self.collection_name = "trash_classification_docs"
        try:
            self.collection = self.client.get_collection(name=self.collection_name)
            logger.info(f"已加载现有集合: {self.collection_name}")
        except:
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "垃圾分类系统文档知识库"}
            )
            logger.info(f"已创建新集合: {self.collection_name}")

    def add_documents(self, documents: List[str], metadatas: List[Dict] = None, ids: List[str] = None):
        """
        添加文档到向量数据库

        Args:
            documents: 文档文本列表
            metadatas: 文档元数据列表
            ids: 文档ID列表
        """
        try:
            # 生成嵌入向量
            embeddings = self.embedding_model.encode(documents).tolist()

            # 如果没有提供ID，自动生成
            if ids is None:
                ids = [f"doc_{i}" for i in range(len(documents))]

            # 添加到集合
            self.collection.add(
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )

            logger.info(f"成功添加 {len(documents)} 个文档到向量数据库")

        except Exception as e:
            logger.error(f"添加文档失败: {str(e)}", exc_info=True)
            raise

    def search(self, query: str, n_results: int = 3) -> List[Dict]:
        """
        搜索相关文档

        Args:
            query: 查询文本
            n_results: 返回结果数量

        Returns:
            相关文档列表
        """
        try:
            # 生成查询向量
            query_embedding = self.embedding_model.encode([query]).tolist()

            # 搜索
            results = self.collection.query(
                query_embeddings=query_embedding,
                n_results=n_results
            )

            # 格式化结果
            documents = []
            if results['documents'] and len(results['documents']) > 0:
                for i, doc in enumerate(results['documents'][0]):
                    documents.append({
                        'content': doc,
                        'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                        'distance': results['distances'][0][i] if results['distances'] else 0
                    })

            logger.info(f"搜索查询: '{query}', 找到 {len(documents)} 个相关文档")
            return documents

        except Exception as e:
            logger.error(f"搜索文档失败: {str(e)}", exc_info=True)
            return []

    def clear(self):
        """清空集合"""
        try:
            self.client.delete_collection(name=self.collection_name)
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "垃圾分类系统文档知识库"}
            )
            logger.info("已清空向量数据库")
        except Exception as e:
            logger.error(f"清空数据库失败: {str(e)}", exc_info=True)
            raise

    def get_count(self) -> int:
        """获取文档数量"""
        try:
            return self.collection.count()
        except:
            return 0


# 创建全局向量数据库实例
vector_store = VectorStore()
