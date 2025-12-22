"""
管理端API路由
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import Optional, List
from datetime import datetime, timedelta
from app.core.database import get_db
from app.models.database import User, Prediction, Feedback, Knowledge
from app.api.auth import require_admin
from app.schemas.prediction import PredictionListResponse
from app.schemas.knowledge import KnowledgeCreate, KnowledgeUpdate

router = APIRouter(prefix="/api/admin", tags=["管理端"])


@router.get("/predictions", response_model=PredictionListResponse)
def get_all_predictions(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    user_id: Optional[int] = None,
    predicted_class: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """获取所有识别记录（管理员）"""
    query = db.query(Prediction)

    # 按用户筛选
    if user_id:
        query = query.filter(Prediction.user_id == user_id)

    # 按分类筛选
    if predicted_class:
        query = query.filter(Prediction.predicted_class.like(f"%{predicted_class}%"))

    # 按日期筛选
    if start_date:
        query = query.filter(Prediction.created_at >= start_date)
    if end_date:
        query = query.filter(Prediction.created_at <= end_date)

    # 查询总数
    total = query.count()

    # 查询记录
    predictions = (
        query
        .order_by(desc(Prediction.created_at))
        .offset(skip)
        .limit(limit)
        .all()
    )

    # 为每条记录添加用户名
    items = []
    for prediction in predictions:
        prediction_dict = {
            "id": prediction.id,
            "image_path": prediction.image_path,
            "predicted_class": prediction.predicted_class,
            "predicted_class_id": prediction.predicted_class_id,
            "confidence": prediction.confidence,
            "top3_results": prediction.top3_results,
            "created_at": prediction.created_at,
            "user_id": prediction.user_id,
            "username": prediction.user.username if prediction.user else "游客"
        }
        items.append(prediction_dict)

    return {
        "total": total,
        "items": items
    }


@router.delete("/predictions/{prediction_id}")
def delete_prediction_admin(
    prediction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """删除识别记录（管理员）"""
    prediction = db.query(Prediction).filter(Prediction.id == prediction_id).first()

    if not prediction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="记录不存在"
        )

    # 删除图片文件
    import os
    if os.path.exists(prediction.image_path):
        os.remove(prediction.image_path)

    # 删除数据库记录
    db.delete(prediction)
    db.commit()

    return {"message": "删除成功"}


@router.get("/users")
def get_all_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    role: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """获取所有用户（管理员）"""
    query = db.query(User)

    # 按角色筛选
    if role:
        query = query.filter(User.role == role)

    # 按状态筛选
    if is_active is not None:
        query = query.filter(User.is_active == is_active)

    # 查询总数
    total = query.count()

    # 查询用户列表
    users = (
        query
        .order_by(desc(User.created_at))
        .offset(skip)
        .limit(limit)
        .all()
    )

    # 为每个用户添加识别次数统计
    result = []
    for user in users:
        prediction_count = db.query(Prediction).filter(Prediction.user_id == user.id).count()
        user_dict = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "is_active": user.is_active,
            "created_at": user.created_at,
            "prediction_count": prediction_count
        }
        result.append(user_dict)

    return {
        "total": total,
        "items": result
    }


@router.put("/users/{user_id}/status")
def update_user_status(
    user_id: int,
    is_active: bool,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """更新用户状态（管理员）"""
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    # 不能禁用自己
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能修改自己的状态"
        )

    user.is_active = is_active
    db.commit()

    return {"message": "状态更新成功"}


@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """删除用户（管理员）"""
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    # 不能删除自己
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能删除自己"
        )

    # 删除用户的所有识别记录
    predictions = db.query(Prediction).filter(Prediction.user_id == user_id).all()
    for prediction in predictions:
        import os
        if os.path.exists(prediction.image_path):
            os.remove(prediction.image_path)
        db.delete(prediction)

    # 删除用户
    db.delete(user)
    db.commit()

    return {"message": "用户删除成功"}


@router.get("/feedbacks")
def get_all_feedbacks(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status_filter: Optional[str] = Query(None, alias="status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """获取所有反馈（管理员）"""
    query = db.query(Feedback)

    # 按状态筛选
    if status_filter:
        query = query.filter(Feedback.status == status_filter)

    # 查询总数
    total = query.count()

    # 查询反馈列表
    feedbacks = (
        query
        .order_by(desc(Feedback.created_at))
        .offset(skip)
        .limit(limit)
        .all()
    )

    # 为每条反馈添加用户名和识别记录详情
    items = []
    for feedback in feedbacks:
        feedback_dict = {
            "id": feedback.id,
            "user_id": feedback.user_id,
            "username": feedback.user.username if feedback.user else "未知用户",
            "prediction_id": feedback.prediction_id,
            "correct_class": feedback.correct_class,
            "comment": feedback.comment,
            "status": feedback.status,
            "created_at": feedback.created_at,
            "prediction_detail": None
        }

        # 添加识别记录详情
        if feedback.prediction:
            feedback_dict["prediction_detail"] = {
                "id": feedback.prediction.id,
                "image_path": feedback.prediction.image_path,
                "predicted_class": feedback.prediction.predicted_class,
                "confidence": feedback.prediction.confidence,
                "created_at": feedback.prediction.created_at
            }

        items.append(feedback_dict)

    return {
        "total": total,
        "items": items
    }


@router.put("/feedbacks/{feedback_id}")
def update_feedback_status(
    feedback_id: int,
    status_value: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """更新反馈状态（管理员）"""
    feedback = db.query(Feedback).filter(Feedback.id == feedback_id).first()

    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="反馈不存在"
        )

    feedback.status = status_value
    if status_value == "processed":
        feedback.processed_at = datetime.now()

    db.commit()

    return {"message": "状态更新成功"}


@router.get("/knowledge")
def get_all_knowledge_admin(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    category: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """获取所有知识（管理员）"""
    query = db.query(Knowledge)

    # 按分类筛选
    if category:
        query = query.filter(Knowledge.category == category)

    # 查询总数
    total = query.count()

    # 查询知识列表
    knowledge_list = (
        query
        .order_by(desc(Knowledge.created_at))
        .offset(skip)
        .limit(limit)
        .all()
    )

    return {
        "total": total,
        "items": knowledge_list
    }


@router.post("/knowledge")
def create_knowledge(
    knowledge_data: KnowledgeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """创建知识（管理员）"""
    knowledge = Knowledge(
        category=knowledge_data.category,
        title=knowledge_data.title,
        content=knowledge_data.content,
        examples=knowledge_data.examples,
        tips=knowledge_data.tips
    )

    db.add(knowledge)
    db.commit()
    db.refresh(knowledge)

    return knowledge


@router.put("/knowledge/{knowledge_id}")
def update_knowledge(
    knowledge_id: int,
    knowledge_data: KnowledgeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """更新知识（管理员）"""
    knowledge = db.query(Knowledge).filter(Knowledge.id == knowledge_id).first()

    if not knowledge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="知识不存在"
        )

    if knowledge_data.category is not None:
        knowledge.category = knowledge_data.category
    if knowledge_data.title is not None:
        knowledge.title = knowledge_data.title
    if knowledge_data.content is not None:
        knowledge.content = knowledge_data.content
    if knowledge_data.examples is not None:
        knowledge.examples = knowledge_data.examples
    if knowledge_data.tips is not None:
        knowledge.tips = knowledge_data.tips

    knowledge.updated_at = datetime.now()
    db.commit()

    return knowledge


@router.delete("/knowledge/{knowledge_id}")
def delete_knowledge(
    knowledge_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """删除知识（管理员）"""
    knowledge = db.query(Knowledge).filter(Knowledge.id == knowledge_id).first()

    if not knowledge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="知识不存在"
        )

    db.delete(knowledge)
    db.commit()

    return {"message": "删除成功"}
