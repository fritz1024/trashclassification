"""
AI聊天相关的Pydantic模型
"""
from pydantic import BaseModel
from typing import List


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
