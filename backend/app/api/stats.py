"""
统计分析相关API路由
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from app.core.database import get_db
from app.models.database import User, Prediction, Feedback
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


@router.get("/user-activity")
def get_user_activity_stats(
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
) -> Dict:
    """获取用户活跃度分析数据（管理员）"""
    # 最近30天每日活跃用户数
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    daily_active_users = db.query(
        func.date(Prediction.created_at).label('date'),
        func.count(func.distinct(Prediction.user_id)).label('active_users')
    ).filter(
        Prediction.created_at >= thirty_days_ago,
        Prediction.user_id.isnot(None)
    ).group_by(
        func.date(Prediction.created_at)
    ).all()

    # 活跃用户排行榜（Top 10）
    top_active_users = db.query(
        User.id,
        User.username,
        func.count(Prediction.id).label('prediction_count')
    ).join(
        Prediction, User.id == Prediction.user_id
    ).filter(
        Prediction.created_at >= thirty_days_ago
    ).group_by(
        User.id, User.username
    ).order_by(
        func.count(Prediction.id).desc()
    ).limit(10).all()

    return {
        "daily_active_users": [
            {"date": str(date), "count": count}
            for date, count in daily_active_users
        ],
        "top_active_users": [
            {
                "user_id": user_id,
                "username": username,
                "prediction_count": count
            }
            for user_id, username, count in top_active_users
        ]
    }


@router.get("/accuracy")
def get_accuracy_stats(
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
) -> Dict:
    """获取识别准确率分析数据（基于置信度估算）"""
    # 总识别次数
    total_predictions = db.query(Prediction).count()

    # 按置信度区间统计
    confidence_ranges = [
        {"range": "90-100%", "min": 90, "max": 100},
        {"range": "80-90%", "min": 80, "max": 90},
        {"range": "70-80%", "min": 70, "max": 80},
        {"range": "60-70%", "min": 60, "max": 70},
        {"range": "0-60%", "min": 0, "max": 60}
    ]

    confidence_distribution = []
    for range_info in confidence_ranges:
        count = db.query(Prediction).filter(
            Prediction.confidence >= range_info["min"],
            Prediction.confidence < range_info["max"]
        ).count()
        confidence_distribution.append({
            "range": range_info["range"],
            "count": count,
            "percentage": round(count / total_predictions * 100, 2) if total_predictions > 0 else 0
        })

    # 高置信度识别数量（>=80%）
    high_confidence_count = db.query(Prediction).filter(
        Prediction.confidence >= 80
    ).count()

    # 平均置信度
    avg_confidence = db.query(
        func.avg(Prediction.confidence)
    ).scalar() or 0

    # 预估准确率（基于置信度的经验公式）
    # 高置信度(>=80%)的识别通常准确率较高
    estimated_accuracy = round(avg_confidence * 0.9, 2)  # 经验系数0.9

    return {
        "total_predictions": total_predictions,
        "high_confidence_count": high_confidence_count,
        "avg_confidence": round(avg_confidence, 2),
        "estimated_accuracy": estimated_accuracy,
        "confidence_distribution": confidence_distribution
    }
