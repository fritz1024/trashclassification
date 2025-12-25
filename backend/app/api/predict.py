"""
图片识别相关API路由
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional, List
from app.core.database import get_db
from app.schemas.prediction import PredictionResponse, PredictionListResponse
from app.schemas.feedback import FeedbackCreate, FeedbackResponse
from app.models.database import User, Prediction, Feedback
from app.services.model_service import model_service
from app.services.export_service import export_service
from app.api.auth import get_current_user, get_current_user_optional
from app.api.model import get_current_model_config
import os
import uuid
import io
from datetime import datetime
from app.core.config import settings

router = APIRouter(prefix="/api/predict", tags=["识别"])


def save_upload_file(upload_file: UploadFile) -> str:
    """保存上传的文件"""
    # 检查文件扩展名
    file_ext = os.path.splitext(upload_file.filename)[1].lower()
    if file_ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的文件格式，仅支持: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )

    # 生成唯一文件名
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)

    # 确保上传目录存在
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

    # 保存文件
    with open(file_path, "wb") as f:
        f.write(upload_file.file.read())

    return file_path


@router.post("/single", response_model=PredictionResponse)
async def predict_single(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    单张图片识别
    游客和登录用户都可以使用，但只有登录用户会保存记录
    """
    try:
        # 保存上传的文件
        file_path = save_upload_file(file)

        # 模型推理
        class_id, confidence, top3_results = model_service.predict(file_path)
        class_name = model_service.get_class_name(class_id)

        # 获取当前使用的模型名称
        current_model_config = get_current_model_config()
        model_name = current_model_config.get("model_file", "best_model.pth")

        # 创建识别记录
        prediction = Prediction(
            user_id=current_user.id if current_user else None,
            image_path=file_path,
            predicted_class=class_name,
            predicted_class_id=class_id,
            confidence=confidence,
            top3_results=top3_results,
            model_name=model_name
        )

        db.add(prediction)
        db.commit()
        db.refresh(prediction)

        return prediction

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"识别失败: {str(e)}"
        )


@router.post("/batch", response_model=List[PredictionResponse])
async def predict_batch(
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # 批量识别需要登录
):
    """批量图片识别（需要登录）"""
    if len(files) > 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="单次最多上传10张图片"
        )

    # 获取当前使用的模型名称
    current_model_config = get_current_model_config()
    model_name = current_model_config.get("model_file", "best_model.pth")

    results = []

    for file in files:
        try:
            # 保存文件
            file_path = save_upload_file(file)

            # 模型推理
            class_id, confidence, top3_results = model_service.predict(file_path)
            class_name = model_service.get_class_name(class_id)

            # 创建识别记录
            prediction = Prediction(
                user_id=current_user.id,
                image_path=file_path,
                predicted_class=class_name,
                predicted_class_id=class_id,
                confidence=confidence,
                top3_results=top3_results,
                model_name=model_name
            )

            db.add(prediction)
            results.append(prediction)

        except Exception as e:
            # 单个文件失败不影响其他文件
            print(f"处理文件 {file.filename} 失败: {str(e)}")
            continue

    db.commit()

    return results


@router.get("/history", response_model=PredictionListResponse)
def get_prediction_history(
    skip: int = 0,
    limit: int = 20,
    predicted_class: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取用户识别历史（需要登录，支持筛选）"""
    # 构建查询
    query = db.query(Prediction).filter(Prediction.user_id == current_user.id)

    # 添加分类筛选
    if predicted_class:
        query = query.filter(Prediction.predicted_class.like(f"%{predicted_class}%"))

    # 添加日期范围筛选
    if start_date:
        query = query.filter(Prediction.created_at >= start_date)
    if end_date:
        # 结束日期包含当天，所以加一天
        from datetime import datetime, timedelta
        end_datetime = datetime.fromisoformat(end_date) + timedelta(days=1)
        query = query.filter(Prediction.created_at < end_datetime)

    # 查询总数
    total = query.count()

    # 查询记录
    predictions = (
        query
        .order_by(Prediction.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return {
        "total": total,
        "items": predictions
    }


@router.delete("/{prediction_id}")
def delete_prediction(
    prediction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除识别记录（需要登录）"""
    prediction = db.query(Prediction).filter(
        Prediction.id == prediction_id,
        Prediction.user_id == current_user.id
    ).first()

    if not prediction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="记录不存在"
        )

    # 删除图片文件
    if os.path.exists(prediction.image_path):
        os.remove(prediction.image_path)

    # 先删除关联的反馈记录
    db.query(Feedback).filter(Feedback.prediction_id == prediction_id).delete()

    # 再删除识别记录
    db.delete(prediction)
    db.commit()

    return {"message": "删除成功"}


@router.post("/feedback", response_model=FeedbackResponse)
def submit_feedback(
    feedback_data: FeedbackCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """提交识别反馈（需要登录）"""
    # 验证识别记录是否存在且属于当前用户
    prediction = db.query(Prediction).filter(
        Prediction.id == feedback_data.prediction_id,
        Prediction.user_id == current_user.id
    ).first()

    if not prediction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="识别记录不存在或无权访问"
        )

    # 检查是否已经提交过反馈
    existing_feedback = db.query(Feedback).filter(
        Feedback.prediction_id == feedback_data.prediction_id,
        Feedback.user_id == current_user.id
    ).first()

    if existing_feedback:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该识别记录已提交过反馈"
        )

    # 创建反馈记录
    feedback = Feedback(
        user_id=current_user.id,
        prediction_id=feedback_data.prediction_id,
        correct_class=feedback_data.correct_class,
        comment=feedback_data.comment,
        status="pending"
    )

    db.add(feedback)
    db.commit()
    db.refresh(feedback)

    return feedback


@router.get("/export")
def export_predictions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    导出用户识别历史为 CSV 文件（需要登录）
    """
    try:
        # 查询用户的所有识别记录
        predictions = (
            db.query(Prediction)
            .filter(Prediction.user_id == current_user.id)
            .order_by(Prediction.created_at.desc())
            .all()
        )

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
                'predicted_class': pred.predicted_class,
                'confidence': confidence_str,
                'created_at': pred.created_at,
                'image_path': os.path.basename(pred.image_path)
            })

        # 定义列
        columns = [
            {'key': 'id', 'label': 'ID'},
            {'key': 'predicted_class', 'label': '分类结果'},
            {'key': 'confidence', 'label': '置信度'},
            {'key': 'created_at', 'label': '识别时间'},
            {'key': 'image_path', 'label': '图片文件名'}
        ]

        # 导出为 CSV
        csv_data = export_service.export_to_csv(export_data, columns)

        # 生成文件名（URL 编码以支持中文）
        from urllib.parse import quote
        filename = f"识别历史_{current_user.username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
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
