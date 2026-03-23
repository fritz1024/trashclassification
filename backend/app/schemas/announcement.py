"""
公告相关的Pydantic模型
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class AnnouncementCreate(BaseModel):
    """创建公告"""
    title: str
    content: str
    type: str = "info"
    is_published: bool = True
    priority: int = 0


class AnnouncementUpdate(BaseModel):
    """更新公告"""
    title: Optional[str] = None
    content: Optional[str] = None
    type: Optional[str] = None
    is_published: Optional[bool] = None
    priority: Optional[int] = None


class AnnouncementResponse(BaseModel):
    """公告响应"""
    id: int
    title: str
    content: str
    type: str
    is_published: bool
    priority: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AnnouncementListResponse(BaseModel):
    """公告列表响应"""
    total: int
    items: List[AnnouncementResponse]
