"""
识别相关的Pydantic模型
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class PredictionResult(BaseModel):
    """单个预测结果"""
    class_name: str
    class_id: int
    confidence: float


class PredictionResponse(BaseModel):
    """识别响应模型"""
    id: int
    image_path: str
    predicted_class: str
    predicted_class_id: int
    confidence: float
    top3_results: List[PredictionResult]
    created_at: datetime
    user_id: Optional[int] = None
    username: Optional[str] = None

    class Config:
        from_attributes = True


class PredictionCreate(BaseModel):
    """识别创建模型（内部使用）"""
    user_id: Optional[int] = None
    image_path: str
    predicted_class: str
    predicted_class_id: int
    confidence: float
    top3_results: List[dict]


class PredictionListResponse(BaseModel):
    """识别列表响应"""
    total: int
    items: List[PredictionResponse]
