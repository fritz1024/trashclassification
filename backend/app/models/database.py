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
    role = Column(String(20), default="user")  # user, admin, super_admin
    avatar = Column(String(255), nullable=True)  # 头像路径
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    predictions = relationship("Prediction", back_populates="user")
    feedbacks = relationship("Feedback", back_populates="user", foreign_keys="Feedback.user_id")
    chat_conversations = relationship("ChatConversation", back_populates="user")
    knowledge_documents = relationship("KnowledgeDocument", back_populates="uploader")


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
    model_name = Column(String(100), nullable=True)  # 使用的模型名称
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
    processed_by = Column(Integer, ForeignKey("users.id"), nullable=True)  # 处理人
    process_result = Column(String(20), nullable=True)  # adopted, rejected, invalid
    process_comment = Column(Text, nullable=True)  # 处理意见
    notified = Column(Boolean, default=False)  # 是否已通知用户
    created_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)

    # 关系
    user = relationship("User", back_populates="feedbacks", foreign_keys=[user_id])
    prediction = relationship("Prediction", back_populates="feedbacks")


class ChatConversation(Base):
    """AI 聊天对话表"""
    __tablename__ = "chat_conversations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(200), nullable=False)  # 对话标题
    messages = Column(JSON, nullable=False)  # 消息列表 [{"role": "user", "content": "..."}, ...]
    created_at = Column(DateTime, default=datetime.now, index=True)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # 关系
    user = relationship("User", back_populates="chat_conversations")

class Announcement(Base):
    """系统公告表"""
    __tablename__ = "announcements"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)  # 公告标题
    content = Column(Text, nullable=False)  # 公告内容（富文本HTML）
    is_published = Column(Boolean, default=True)  # 是否发布
    created_at = Column(DateTime, default=datetime.now, index=True)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class KnowledgeDocument(Base):
    """知识库文档表"""
    __tablename__ = "knowledge_documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)
    file_type = Column(String(10), nullable=False)
    status = Column(String(20), default="pending")  # pending, processed, failed
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    chunk_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    uploader = relationship("User", back_populates="knowledge_documents")


class TrainingDataset(Base):
    """训练数据集表"""
    __tablename__ = "training_datasets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    source_type = Column(String(20), nullable=False)  # history, upload
    file_path = Column(String(500), nullable=True)  # 上传数据集的路径
    class_count = Column(Integer, default=0)
    image_count = Column(Integer, default=0)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # 关系
    creator = relationship("User")


class TrainingJob(Base):
    """训练任务表"""
    __tablename__ = "training_jobs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)  # 模型名称，如 G0001
    dataset_id = Column(Integer, ForeignKey("training_datasets.id"), nullable=False)
    status = Column(String(20), default="pending")  # pending, running, completed, failed, cancelled
    training_params = Column(JSON, nullable=True)  # 训练参数
    progress = Column(Float, default=0.0)  # 训练进度 0-100
    current_epoch = Column(Integer, default=0)
    total_epochs = Column(Integer, default=10)
    loss = Column(Float, nullable=True)
    accuracy = Column(Float, nullable=True)
    model_path = Column(String(500), nullable=True)  # 训练完成后的模型路径
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # 关系
    dataset = relationship("TrainingDataset")
    creator = relationship("User")
