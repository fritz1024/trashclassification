"""
文档处理服务 - 处理上传的知识库文档
"""
from app.services.document_loader import TextSplitter
from app.services.vector_store import vector_store
from app.core.logger import logger
from sqlalchemy.orm import Session


def process_uploaded_document(db: Session, doc_id: int, file_path: str):
    """
    处理上传的文档：读取、分块、嵌入、存储

    Args:
        db: 数据库会话
        doc_id: 文档ID
        file_path: 文件路径
    """
    from app.models.database import KnowledgeDocument

    try:
        # 获取文档记录
        doc = db.query(KnowledgeDocument).filter(KnowledgeDocument.id == doc_id).first()
        if not doc:
            logger.error(f"文档 {doc_id} 不存在")
            return

        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 分块
        splitter = TextSplitter(chunk_size=800, chunk_overlap=100)
        chunks = splitter.split_text(content)

        if not chunks:
            doc.status = "failed"
            db.commit()
            logger.error(f"文档 {doc_id} 分块失败")
            return

        # 添加到向量库
        metadatas = [{'source': doc.original_filename, 'chunk_id': i} for i in range(len(chunks))]
        vector_store.add_document_chunks(doc_id, chunks, metadatas)

        # 更新数据库记录
        doc.chunk_count = len(chunks)
        doc.status = "processed"
        db.commit()

        logger.info(f"文档 {doc_id} 处理完成，共 {len(chunks)} 个分块")

    except Exception as e:
        logger.error(f"处理文档 {doc_id} 失败: {str(e)}", exc_info=True)
        doc = db.query(KnowledgeDocument).filter(KnowledgeDocument.id == doc_id).first()
        if doc:
            doc.status = "failed"
            db.commit()
        raise
