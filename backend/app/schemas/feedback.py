"""
反馈相关的Pydantic模型
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class FeedbackCreate(BaseModel):
    """创建反馈"""
    prediction_id: int
    correct_class: str
    comment: Optional[str] = None


class FeedbackResponse(BaseModel):
    """反馈响应模型"""
    id: int
    user_id: int
    prediction_id: int
    correct_class: str
    comment: Optional[str] = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
