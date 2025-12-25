"""
知识相关的Pydantic模型
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class KnowledgeCreate(BaseModel):
    """创建知识模型（博文形式）"""
    category: str
    title: str
    summary: Optional[str] = None
    content: str  # 富文本内容
    cover_image: Optional[str] = None
    author: Optional[str] = "系统管理员"
    is_published: Optional[bool] = True
    examples: Optional[List[str]] = None  # 保留兼容
    tips: Optional[str] = None  # 保留兼容


class KnowledgeUpdate(BaseModel):
    """更新知识模型"""
    category: Optional[str] = None
    title: Optional[str] = None
    summary: Optional[str] = None
    content: Optional[str] = None
    cover_image: Optional[str] = None
    author: Optional[str] = None
    is_published: Optional[bool] = None
    examples: Optional[List[str]] = None
    tips: Optional[str] = None


class KnowledgeResponse(BaseModel):
    """知识响应模型"""
    id: int
    category: str
    title: str
    summary: Optional[str] = None
    content: str
    cover_image: Optional[str] = None
    author: str
    view_count: int
    is_published: bool
    examples: Optional[List[str]] = None
    tips: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
