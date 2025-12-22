"""
知识相关的Pydantic模型
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class KnowledgeCreate(BaseModel):
    """创建知识模型"""
    category: str
    title: str
    content: str
    examples: Optional[str] = None
    tips: Optional[str] = None


class KnowledgeUpdate(BaseModel):
    """更新知识模型"""
    category: Optional[str] = None
    title: Optional[str] = None
    content: Optional[str] = None
    examples: Optional[str] = None
    tips: Optional[str] = None


class KnowledgeResponse(BaseModel):
    """知识响应模型"""
    id: int
    category: str
    title: str
    content: str
    examples: Optional[str] = None
    tips: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
