"""
数据库模型定义
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class User(Base):
    """用户表"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default="user")  # user, admin
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    predictions = relationship("Prediction", back_populates="user")
    feedbacks = relationship("Feedback", back_populates="user")
    chat_conversations = relationship("ChatConversation", back_populates="user")


class Prediction(Base):
    """识别记录表"""
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # 可为空表示游客
    image_path = Column(String(255), nullable=False)
    predicted_class = Column(String(100), nullable=False)
    predicted_class_id = Column(Integer, nullable=False)
    confidence = Column(Float, nullable=False)
    top3_results = Column(JSON, nullable=True)  # 存储Top3结果
    is_correct = Column(Boolean, nullable=True)  # 用户反馈是否正确
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # 关系
    user = relationship("User", back_populates="predictions")
    feedbacks = relationship("Feedback", back_populates="prediction")


class Feedback(Base):
    """用户反馈表"""
    __tablename__ = "feedbacks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    prediction_id = Column(Integer, ForeignKey("predictions.id"), nullable=False)
    correct_class = Column(String(100), nullable=False)
    correct_class_id = Column(Integer, nullable=True)
    comment = Column(Text, nullable=True)
    status = Column(String(20), default="pending")  # pending, processed
    created_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)

    # 关系
    user = relationship("User", back_populates="feedbacks")
    prediction = relationship("Prediction", back_populates="feedbacks")


class Knowledge(Base):
    """垃圾分类知识库表"""
    __tablename__ = "knowledge"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String(50), nullable=False, index=True)  # 可回收/有害/厨余/其他
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    examples = Column(JSON, nullable=True)  # 示例列表
    tips = Column(Text, nullable=True)  # 处理建议
    image_url = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ChatConversation(Base):
    """AI 聊天对话表"""
    __tablename__ = "chat_conversations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(200), nullable=False)  # 对话标题
    messages = Column(JSON, nullable=False)  # 消息列表 [{"role": "user", "content": "..."}, ...]
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    user = relationship("User", back_populates="chat_conversations")
