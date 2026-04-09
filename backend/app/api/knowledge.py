"""
知识库管理API路由
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status, Query, Body
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional, List
import os
import time
from app.core.database import get_db
from app.models.database import User, KnowledgeDocument
from app.schemas.knowledge import KnowledgeDocumentResponse, KnowledgeDocumentList
from app.api.auth import require_admin
from app.core.logger import logger
from app.services.vector_store import vector_store

router = APIRouter(prefix="/api/admin/knowledge", tags=["知识库管理"])


@router.post("/upload", response_model=KnowledgeDocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """上传知识库文档"""
    # 验证文件类型
    allowed_extensions = {".md", ".txt"}
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail="只支持 .md 和 .txt 文件")

    # 验证文件大小
    contents = await file.read()
    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="文件大小不能超过 10MB")

    # 保存文件
    upload_dir = "uploads/documents"
    os.makedirs(upload_dir, exist_ok=True)

    filename = f"{int(time.time())}_{file.filename}"
    file_path = os.path.join(upload_dir, filename)

    with open(file_path, "wb") as f:
        f.write(contents)

    # 创建数据库记录
    doc = KnowledgeDocument(
        filename=filename,
        original_filename=file.filename,
        file_path=file_path,
        file_size=len(contents),
        file_type=ext,
        status="pending",
        uploaded_by=current_user.id
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    # 处理文档
    try:
        from app.services.document_processor import process_uploaded_document
        process_uploaded_document(db, doc.id, file_path)
    except Exception as e:
        logger.error(f"处理文档失败: {str(e)}")

    db.refresh(doc)
    return doc


@router.get("", response_model=KnowledgeDocumentList)
def get_documents(
    skip: int = 0,
    limit: int = 20,
    status: Optional[str] = None,
    file_type: Optional[str] = None,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """获取知识库文档列表"""
    query = db.query(KnowledgeDocument)

    if status:
        query = query.filter(KnowledgeDocument.status == status)
    if file_type:
        query = query.filter(KnowledgeDocument.file_type == file_type)

    total = query.count()
    items = query.order_by(KnowledgeDocument.created_at.desc()).offset(skip).limit(limit).all()

    return {"total": total, "items": items}


@router.get("/{doc_id}/content")
def get_document_content(
    doc_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """获取文档内容用于编辑"""
    doc = db.query(KnowledgeDocument).filter(KnowledgeDocument.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="文档不存在")

    try:
        with open(doc.file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return {"content": content}
    except Exception as e:
        logger.error(f"读取文件失败: {str(e)}")
        raise HTTPException(status_code=500, detail="读取文件失败")


@router.put("/{doc_id}", response_model=KnowledgeDocumentResponse)
def update_document(
    doc_id: int,
    content: str = Body(..., embed=True),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """更新文档内容"""
    doc = db.query(KnowledgeDocument).filter(KnowledgeDocument.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="文档不存在")

    try:
        # 保存新内容
        with open(doc.file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        # 更新文件大小
        doc.file_size = len(content.encode('utf-8'))
        doc.status = "pending"
        db.commit()

        # 删除旧向量
        vector_store.delete_document(doc_id)

        # 重新处理
        from app.services.document_processor import process_uploaded_document
        process_uploaded_document(db, doc_id, doc.file_path)

        db.refresh(doc)
        return doc
    except Exception as e:
        logger.error(f"更新文档失败: {str(e)}")
        raise HTTPException(status_code=500, detail="更新文档失败")


@router.delete("/{doc_id}")
def delete_document(
    doc_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """删除知识库文档"""
    doc = db.query(KnowledgeDocument).filter(KnowledgeDocument.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="文档不存在")

    # 从向量库删除
    try:
        vector_store.delete_document(doc_id)
    except Exception as e:
        logger.error(f"从向量库删除文档失败: {str(e)}")

    # 删除文件
    if os.path.exists(doc.file_path):
        os.remove(doc.file_path)

    # 删除数据库记录
    db.delete(doc)
    db.commit()

    return {"message": "文档已删除"}
