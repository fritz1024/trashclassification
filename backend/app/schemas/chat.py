"""
AI聊天相关的Pydantic模型
"""
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class Message(BaseModel):
    """聊天消息模型"""
    role: str  # "user" 或 "assistant"
    content: str  # 消息内容


class ChatRequest(BaseModel):
    """聊天请求模型"""
    messages: List[Message]  # 对话历史


class ChatResponse(BaseModel):
    """聊天响应模型"""
    reply: str  # AI的回复
    success: bool = True  # 是否成功
    error: str = None  # 错误信息（如果有）


class ConversationCreate(BaseModel):
    """创建对话模型"""
    title: str
    messages: List[Message]


class ConversationUpdate(BaseModel):
    """更新对话模型"""
    title: Optional[str] = None
    messages: Optional[List[Message]] = None


class ConversationResponse(BaseModel):
    """对话响应模型"""
    id: int
    user_id: int
    title: str
    messages: List[dict]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
