"""
向量数据库服务 - 用于 RAG 检索
"""
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Optional
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
        self._embedding_model = None
        self._client = None
        self._collection = None
        self.collection_name = "trash_classification_docs"

    @property
    def client(self):
        """懒加载 ChromaDB 客户端"""
        if self._client is None:
            os.makedirs(self.persist_directory, exist_ok=True)
            self._client = chromadb.Client(Settings(
                persist_directory=self.persist_directory,
                anonymized_telemetry=False
            ))
        return self._client

    @property
    def collection(self):
        """懒加载集合"""
        if self._collection is None:
            try:
                self._collection = self.client.get_collection(name=self.collection_name)
                logger.info(f"已加载现有集合: {self.collection_name}")
            except:
                self._collection = self.client.create_collection(
                    name=self.collection_name,
                    metadata={"description": "垃圾分类系统文档知识库"}
                )
                logger.info(f"已创建新集合: {self.collection_name}")
        return self._collection

    @property
    def embedding_model(self):
        """懒加载嵌入模型"""
        if self._embedding_model is None:
            from sentence_transformers import SentenceTransformer
            logger.info("正在加载嵌入模型...")
            self._embedding_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
            logger.info("嵌入模型加载完成")
        return self._embedding_model

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

    def add_document_chunks(self, doc_id: int, chunks: List[str], metadatas: List[Dict] = None):
        """
        添加文档分块到向量数据库

        Args:
            doc_id: 文档ID
            chunks: 文档分块列表
            metadatas: 分块元数据列表
        """
        try:
            if metadatas is None:
                metadatas = [{}] * len(chunks)

            # 在每个metadata中添加doc_id
            for metadata in metadatas:
                metadata['doc_id'] = doc_id

            # 生成唯一ID
            ids = [f"doc_{doc_id}_chunk_{i}" for i in range(len(chunks))]

            # 添加到向量库
            self.add_documents(chunks, metadatas, ids)
            logger.info(f"文档 {doc_id} 的 {len(chunks)} 个分块已添加到向量库")

        except Exception as e:
            logger.error(f"添加文档分块失败: {str(e)}", exc_info=True)
            raise

    def delete_document(self, doc_id: int):
        """
        删除指定文档的所有分块

        Args:
            doc_id: 文档ID
        """
        try:
            # 查询该文档的所有分块
            results = self.collection.get(where={"doc_id": doc_id})

            if results['ids']:
                # 删除所有分块
                self.collection.delete(ids=results['ids'])
                logger.info(f"已删除文档 {doc_id} 的 {len(results['ids'])} 个分块")
                return len(results['ids'])
            else:
                logger.info(f"文档 {doc_id} 没有找到分块")
                return 0

        except Exception as e:
            logger.error(f"删除文档分块失败: {str(e)}", exc_info=True)
            raise

    def get_document_chunk_count(self, doc_id: int) -> int:
        """
        获取指定文档的分块数量

        Args:
            doc_id: 文档ID

        Returns:
            分块数量
        """
        try:
            results = self.collection.get(where={"doc_id": doc_id})
            return len(results['ids']) if results['ids'] else 0
        except Exception as e:
            logger.error(f"获取文档分块数量失败: {str(e)}", exc_info=True)
            return 0


# 创建全局向量数据库实例
vector_store = VectorStore()
