"""
统计分析相关API路由
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import get_db
from app.models.database import User, Prediction
from app.api.auth import get_current_user, require_admin
from typing import Dict, List
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/stats", tags=["统计"])


@router.get("/user")
def get_user_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict:
    """获取用户个人统计数据"""
    # 总识别次数
    total_predictions = db.query(Prediction).filter(
        Prediction.user_id == current_user.id
    ).count()

    # 各类垃圾识别次数
    category_stats = db.query(
        Prediction.predicted_class,
        func.count(Prediction.id).label('count')
    ).filter(
        Prediction.user_id == current_user.id
    ).group_by(
        Prediction.predicted_class
    ).all()

    # 最近7天的识别趋势
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    daily_stats = db.query(
        func.date(Prediction.created_at).label('date'),
        func.count(Prediction.id).label('count')
    ).filter(
        Prediction.user_id == current_user.id,
        Prediction.created_at >= seven_days_ago
    ).group_by(
        func.date(Prediction.created_at)
    ).all()

    # 平均置信度
    avg_confidence = db.query(
        func.avg(Prediction.confidence)
    ).filter(
        Prediction.user_id == current_user.id
    ).scalar() or 0

    return {
        "total_predictions": total_predictions,
        "category_stats": [
            {"category": cat, "count": count}
            for cat, count in category_stats
        ],
        "daily_stats": [
            {"date": str(date), "count": count}
            for date, count in daily_stats
        ],
        "avg_confidence": round(avg_confidence, 2)
    }


@router.get("/global")
def get_global_stats(
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
) -> Dict:
    """获取全局统计数据（管理员）"""
    # 总用户数
    total_users = db.query(User).count()

    # 总识别次数
    total_predictions = db.query(Prediction).count()

    # 各类垃圾识别次数
    category_stats = db.query(
        Prediction.predicted_class,
        func.count(Prediction.id).label('count')
    ).group_by(
        Prediction.predicted_class
    ).order_by(
        func.count(Prediction.id).desc()
    ).limit(10).all()

    # 最近30天的识别趋势
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    daily_stats = db.query(
        func.date(Prediction.created_at).label('date'),
        func.count(Prediction.id).label('count')
    ).filter(
        Prediction.created_at >= thirty_days_ago
    ).group_by(
        func.date(Prediction.created_at)
    ).all()

    # 活跃用户数（最近7天有识别记录）
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    active_users = db.query(
        func.count(func.distinct(Prediction.user_id))
    ).filter(
        Prediction.created_at >= seven_days_ago,
        Prediction.user_id.isnot(None)
    ).scalar() or 0

    return {
        "total_users": total_users,
        "total_predictions": total_predictions,
        "active_users": active_users,
        "category_stats": [
            {"category": cat, "count": count}
            for cat, count in category_stats
        ],
        "daily_stats": [
            {"date": str(date), "count": count}
            for date, count in daily_stats
        ]
    }
