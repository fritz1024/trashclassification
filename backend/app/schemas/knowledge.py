"""
知识库文档相关的Pydantic模型
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class KnowledgeDocumentResponse(BaseModel):
    """知识库文档响应模型"""
    id: int
    filename: str
    original_filename: str
    file_path: str
    file_size: int
    file_type: str
    status: str
    uploaded_by: int
    chunk_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class KnowledgeDocumentList(BaseModel):
    """知识库文档列表响应"""
    total: int
    items: list[KnowledgeDocumentResponse]
