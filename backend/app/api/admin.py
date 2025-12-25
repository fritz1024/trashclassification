"""
管理端API路由
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import Optional, List
from datetime import datetime, timedelta
from pydantic import BaseModel
from app.core.database import get_db
from app.models.database import User, Prediction, Feedback
from app.api.auth import require_admin
from app.schemas.prediction import PredictionListResponse
from app.services.export_service import export_service
import io
import os

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


class PasswordResetRequest(BaseModel):
    """重置密码请求模型"""
    new_password: str


@router.put("/users/{user_id}/password")
def reset_user_password(
    user_id: int,
    password_data: PasswordResetRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """重置用户密码（管理员）"""
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    # 加密新密码
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    user.password_hash = pwd_context.hash(password_data.new_password)

    db.commit()

    return {"message": "密码重置成功"}


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


@router.get("/predictions/export")
def export_all_predictions(
    user_id: Optional[int] = None,
    predicted_class: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    导出所有识别记录为 CSV 文件（管理员）
    支持筛选条件
    """
    try:
        query = db.query(Prediction)

        # 应用筛选条件
        if user_id:
            query = query.filter(Prediction.user_id == user_id)
        if predicted_class:
            query = query.filter(Prediction.predicted_class.like(f"%{predicted_class}%"))
        if start_date:
            query = query.filter(Prediction.created_at >= start_date)
        if end_date:
            query = query.filter(Prediction.created_at <= end_date)

        # 查询所有记录
        predictions = query.order_by(desc(Prediction.created_at)).all()

        # 准备导出数据
        export_data = []
        for pred in predictions:
            # 安全处理置信度格式
            confidence_value = pred.confidence
            if confidence_value > 1:
                # 如果已经是百分比格式（如 95.0）
                confidence_str = f"{confidence_value:.2f}%"
            else:
                # 如果是小数格式（如 0.95）
                confidence_str = f"{confidence_value * 100:.2f}%"

            export_data.append({
                'id': pred.id,
                'username': pred.user.username if pred.user else '游客',
                'predicted_class': pred.predicted_class,
                'confidence': confidence_str,
                'created_at': pred.created_at,
                'image_path': os.path.basename(pred.image_path)
            })

        # 定义列
        columns = [
            {'key': 'id', 'label': 'ID'},
            {'key': 'username', 'label': '用户名'},
            {'key': 'predicted_class', 'label': '分类结果'},
            {'key': 'confidence', 'label': '置信度'},
            {'key': 'created_at', 'label': '识别时间'},
            {'key': 'image_path', 'label': '图片文件名'}
        ]

        # 导出为 CSV
        csv_data = export_service.export_to_csv(export_data, columns)

        # 生成文件名（URL 编码以支持中文）
        from urllib.parse import quote
        filename = f"识别记录_全部_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        encoded_filename = quote(filename)

        # 返回文件流
        return StreamingResponse(
            io.BytesIO(csv_data),
            media_type="text/csv; charset=utf-8",
            headers={
                "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"
            }
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"导出失败: {str(e)}"
        )
