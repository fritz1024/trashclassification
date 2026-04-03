"""
模型训练相关API路由
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional, List
from app.core.database import get_db
from app.models.database import User, TrainingDataset, TrainingJob, Prediction, Feedback
from app.api.auth import require_super_admin, require_admin_or_above
from datetime import datetime
import os
import shutil
from app.core.config import settings
from app.services.training_service import start_training

router = APIRouter(prefix="/api/admin/training", tags=["模型训练"])


@router.post("/datasets/from-history")
def create_dataset_from_history(
    name: str,
    min_images_per_class: int = Query(10, ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin)
):
    """从识别历史生成训练数据集（结合反馈纠正）"""
    try:
        from sqlalchemy import func, case
        from collections import Counter

        # 查询所有识别记录
        predictions = db.query(Prediction).all()

        # 统计每个类别的图片数量（结合反馈纠正）
        class_counter = Counter()
        for pred in predictions:
            # 查找是否有被采纳的反馈纠正
            feedback = (
                db.query(Feedback)
                .filter(
                    Feedback.prediction_id == pred.id,
                    Feedback.process_result == "adopted"
                )
                .first()
            )

            # 有反馈纠正则用纠正后的分类，否则用原始预测分类
            if feedback and feedback.correct_class:
                label = feedback.correct_class
            else:
                label = pred.predicted_class

            class_counter[label] += 1

        # 过滤满足最小图片数的类别
        valid_classes = {k: v for k, v in class_counter.items() if v >= min_images_per_class}

        if not valid_classes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"没有足够的数据，每个类别至少需要{min_images_per_class}张图片"
            )

        # 创建数据集记录
        dataset = TrainingDataset(
            name=name,
            source_type="history",
            class_count=len(valid_classes),
            image_count=sum(valid_classes.values()),
            created_by=current_user.id
        )
        db.add(dataset)
        db.commit()
        db.refresh(dataset)

        return {
            "id": dataset.id,
            "name": dataset.name,
            "class_count": dataset.class_count,
            "image_count": dataset.image_count,
            "classes": [{"name": k, "count": v} for k, v in valid_classes.items()]
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建数据集失败: {str(e)}"
        )


@router.get("/datasets")
def get_datasets(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin)
):
    """获取训练数据集列表"""
    total = db.query(TrainingDataset).count()
    datasets = (
        db.query(TrainingDataset)
        .order_by(desc(TrainingDataset.created_at))
        .offset(skip)
        .limit(limit)
        .all()
    )

    items = []
    for dataset in datasets:
        items.append({
            "id": dataset.id,
            "name": dataset.name,
            "source_type": dataset.source_type,
            "class_count": dataset.class_count,
            "image_count": dataset.image_count,
            "created_at": dataset.created_at,
            "creator_name": dataset.creator.username if dataset.creator else "未知"
        })

    return {"total": total, "items": items}


@router.get("/datasets/{dataset_id}/detail")
def get_dataset_detail(
    dataset_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin)
):
    """获取数据集详情"""
    dataset = db.query(TrainingDataset).filter(TrainingDataset.id == dataset_id).first()

    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="数据集不存在"
        )

    # 如果是从历史生成的数据集，统计类别信息（结合反馈纠正）
    classes = []
    if dataset.source_type == "history":
        from collections import Counter
        predictions = db.query(Prediction).all()
        class_counter = Counter()
        corrected_count = 0

        for pred in predictions:
            feedback = (
                db.query(Feedback)
                .filter(
                    Feedback.prediction_id == pred.id,
                    Feedback.process_result == "adopted"
                )
                .first()
            )
            if feedback and feedback.correct_class:
                label = feedback.correct_class
                corrected_count += 1
            else:
                label = pred.predicted_class
            class_counter[label] += 1

        classes = [{"name": k, "count": v} for k, v in class_counter.items()]

    return {
        "id": dataset.id,
        "name": dataset.name,
        "source_type": dataset.source_type,
        "class_count": dataset.class_count,
        "image_count": dataset.image_count,
        "created_at": dataset.created_at,
        "creator_name": dataset.creator.username if dataset.creator else "未知",
        "classes": classes
    }


@router.delete("/datasets/{dataset_id}")
def delete_dataset(
    dataset_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin)
):
    """删除训练数据集"""
    dataset = db.query(TrainingDataset).filter(TrainingDataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="数据集不存在"
        )

    # 检查是否有关联的训练任务
    job_count = db.query(TrainingJob).filter(TrainingJob.dataset_id == dataset_id).count()
    if job_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"该数据集有{job_count}个关联的训练任务，无法删除"
        )

    # 删除上传的文件（如果有）
    if dataset.file_path and os.path.exists(dataset.file_path):
        shutil.rmtree(dataset.file_path, ignore_errors=True)

    db.delete(dataset)
    db.commit()

    return {"message": "删除成功"}


@router.post("/jobs")
def create_training_job(
    dataset_id: int,
    name: Optional[str] = None,
    epochs: int = Query(10, ge=1, le=100),
    batch_size: int = Query(32, ge=1),
    learning_rate: float = Query(0.001, gt=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin)
):
    """创建训练任务"""
    # 检查数据集是否存在
    dataset = db.query(TrainingDataset).filter(TrainingDataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="数据集不存在"
        )

    # 生成模型名称
    if not name:
        # 获取最新的G编号
        last_job = db.query(TrainingJob).filter(TrainingJob.name.like('G%')).order_by(desc(TrainingJob.id)).first()
        if last_job and last_job.name.startswith('G'):
            try:
                last_num = int(last_job.name[1:])
                name = f"G{last_num + 1:04d}"
            except:
                name = "G0001"
        else:
            name = "G0001"

    # 创建训练任务
    job = TrainingJob(
        name=name,
        dataset_id=dataset_id,
        status="pending",
        training_params={
            "epochs": epochs,
            "batch_size": batch_size,
            "learning_rate": learning_rate
        },
        total_epochs=epochs,
        created_by=current_user.id
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    return {
        "id": job.id,
        "name": job.name,
        "status": job.status,
        "dataset_id": job.dataset_id,
        "training_params": job.training_params
    }


@router.get("/jobs")
def get_training_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status_filter: Optional[str] = Query(None, alias="status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin)
):
    """获取训练任务列表"""
    query = db.query(TrainingJob)

    if status_filter:
        query = query.filter(TrainingJob.status == status_filter)

    total = query.count()
    jobs = query.order_by(desc(TrainingJob.created_at)).offset(skip).limit(limit).all()

    items = []
    for job in jobs:
        items.append({
            "id": job.id,
            "name": job.name,
            "status": job.status,
            "progress": job.progress,
            "current_epoch": job.current_epoch,
            "total_epochs": job.total_epochs,
            "loss": job.loss,
            "accuracy": job.accuracy,
            "dataset_name": job.dataset.name if job.dataset else "未知",
            "created_at": job.created_at,
            "started_at": job.started_at,
            "completed_at": job.completed_at
        })

    return {"total": total, "items": items}


@router.get("/jobs/{job_id}")
def get_training_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin)
):
    """获取训练任务详情"""
    job = db.query(TrainingJob).filter(TrainingJob.id == job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="训练任务不存在"
        )

    return {
        "id": job.id,
        "name": job.name,
        "status": job.status,
        "progress": job.progress,
        "current_epoch": job.current_epoch,
        "total_epochs": job.total_epochs,
        "loss": job.loss,
        "accuracy": job.accuracy,
        "training_params": job.training_params,
        "model_path": job.model_path,
        "dataset": {
            "id": job.dataset.id,
            "name": job.dataset.name,
            "class_count": job.dataset.class_count,
            "image_count": job.dataset.image_count
        } if job.dataset else None,
        "created_at": job.created_at,
        "started_at": job.started_at,
        "completed_at": job.completed_at
    }


@router.post("/jobs/{job_id}/start")
def start_training_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin)
):
    """启动训练任务"""
    job = db.query(TrainingJob).filter(TrainingJob.id == job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="训练任务不存在"
        )

    if job.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只能启动待处理的任务"
        )

    try:
        start_training(job_id)
        return {"message": "训练已启动"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"启动训练失败: {str(e)}"
        )


@router.post("/jobs/{job_id}/cancel")
def cancel_training_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin)
):
    """取消训练任务"""
    job = db.query(TrainingJob).filter(TrainingJob.id == job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="训练任务不存在"
        )

    if job.status not in ["pending", "running"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只能取消待处理或运行中的任务"
        )

    job.status = "cancelled"
    job.completed_at = datetime.utcnow()
    db.commit()

    return {"message": "任务已取消"}


@router.delete("/jobs/{job_id}")
def delete_training_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin)
):
    """删除训练任务"""
    job = db.query(TrainingJob).filter(TrainingJob.id == job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="训练任务不存在"
        )

    # 删除模型文件
    if job.model_path and os.path.exists(job.model_path):
        os.remove(job.model_path)

    db.delete(job)
    db.commit()

    return {"message": "删除成功"}
