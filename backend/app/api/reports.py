"""
报表相关API路由
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.core.database import get_db
from app.models.database import User, Prediction, Feedback
from app.api.auth import require_admin
from datetime import datetime, timedelta
from typing import Optional
import io
import csv

router = APIRouter(prefix="/api/reports", tags=["报表"])


@router.get("/weekly")
def get_weekly_report(
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    """生成周报数据"""
    # 获取最近7天的数据
    seven_days_ago = datetime.now() - timedelta(days=7)

    # 本周识别总数
    total_predictions = db.query(Prediction).filter(
        Prediction.created_at >= seven_days_ago
    ).count()

    # 本周新增用户
    new_users = db.query(User).filter(
        User.created_at >= seven_days_ago
    ).count()

    # 本周活跃用户
    active_users = db.query(
        func.count(func.distinct(Prediction.user_id))
    ).filter(
        Prediction.created_at >= seven_days_ago,
        Prediction.user_id.isnot(None)
    ).scalar() or 0

    # 每日识别趋势
    daily_stats = db.query(
        func.date(Prediction.created_at).label('date'),
        func.count(Prediction.id).label('count')
    ).filter(
        Prediction.created_at >= seven_days_ago
    ).group_by(
        func.date(Prediction.created_at)
    ).all()

    # 分类统计
    category_stats = db.query(
        Prediction.predicted_class,
        func.count(Prediction.id).label('count')
    ).filter(
        Prediction.created_at >= seven_days_ago
    ).group_by(
        Prediction.predicted_class
    ).order_by(
        func.count(Prediction.id).desc()
    ).limit(10).all()

    return {
        "period": "weekly",
        "start_date": seven_days_ago.strftime("%Y-%m-%d"),
        "end_date": datetime.now().strftime("%Y-%m-%d"),
        "summary": {
            "total_predictions": total_predictions,
            "new_users": new_users,
            "active_users": active_users
        },
        "daily_stats": [
            {"date": str(date), "count": count}
            for date, count in daily_stats
        ],
        "category_stats": [
            {"category": cat, "count": count}
            for cat, count in category_stats
        ]
    }


@router.get("/monthly")
def get_monthly_report(
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    """生成月报数据"""
    # 获取最近30天的数据
    thirty_days_ago = datetime.now() - timedelta(days=30)

    # 本月识别总数
    total_predictions = db.query(Prediction).filter(
        Prediction.created_at >= thirty_days_ago
    ).count()

    # 本月新增用户
    new_users = db.query(User).filter(
        User.created_at >= thirty_days_ago
    ).count()

    # 本月活跃用户
    active_users = db.query(
        func.count(func.distinct(Prediction.user_id))
    ).filter(
        Prediction.created_at >= thirty_days_ago,
        Prediction.user_id.isnot(None)
    ).scalar() or 0

    # 每日识别趋势
    daily_stats = db.query(
        func.date(Prediction.created_at).label('date'),
        func.count(Prediction.id).label('count')
    ).filter(
        Prediction.created_at >= thirty_days_ago
    ).group_by(
        func.date(Prediction.created_at)
    ).all()

    # 分类统计
    category_stats = db.query(
        Prediction.predicted_class,
        func.count(Prediction.id).label('count')
    ).filter(
        Prediction.created_at >= thirty_days_ago
    ).group_by(
        Prediction.predicted_class
    ).order_by(
        func.count(Prediction.id).desc()
    ).all()

    return {
        "period": "monthly",
        "start_date": thirty_days_ago.strftime("%Y-%m-%d"),
        "end_date": datetime.now().strftime("%Y-%m-%d"),
        "summary": {
            "total_predictions": total_predictions,
            "new_users": new_users,
            "active_users": active_users
        },
        "daily_stats": [
            {"date": str(date), "count": count}
            for date, count in daily_stats
        ],
        "category_stats": [
            {"category": cat, "count": count}
            for cat, count in category_stats
        ]
    }


@router.get("/custom")
def get_custom_report(
    start_date: str = Query(..., description="开始日期 YYYY-MM-DD"),
    end_date: str = Query(..., description="结束日期 YYYY-MM-DD"),
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    """生成自定义时间段报表"""
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
    except ValueError:
        raise HTTPException(status_code=400, detail="日期格式错误，请使用 YYYY-MM-DD")

    # 时间段识别总数
    total_predictions = db.query(Prediction).filter(
        Prediction.created_at >= start,
        Prediction.created_at < end
    ).count()

    # 时间段新增用户
    new_users = db.query(User).filter(
        User.created_at >= start,
        User.created_at < end
    ).count()

    # 时间段活跃用户
    active_users = db.query(
        func.count(func.distinct(Prediction.user_id))
    ).filter(
        Prediction.created_at >= start,
        Prediction.created_at < end,
        Prediction.user_id.isnot(None)
    ).scalar() or 0

    # 每日识别趋势
    daily_stats = db.query(
        func.date(Prediction.created_at).label('date'),
        func.count(Prediction.id).label('count')
    ).filter(
        Prediction.created_at >= start,
        Prediction.created_at < end
    ).group_by(
        func.date(Prediction.created_at)
    ).all()

    # 分类统计
    category_stats = db.query(
        Prediction.predicted_class,
        func.count(Prediction.id).label('count')
    ).filter(
        Prediction.created_at >= start,
        Prediction.created_at < end
    ).group_by(
        Prediction.predicted_class
    ).order_by(
        func.count(Prediction.id).desc()
    ).all()

    return {
        "period": "custom",
        "start_date": start_date,
        "end_date": end_date,
        "summary": {
            "total_predictions": total_predictions,
            "new_users": new_users,
            "active_users": active_users
        },
        "daily_stats": [
            {"date": str(date), "count": count}
            for date, count in daily_stats
        ],
        "category_stats": [
            {"category": cat, "count": count}
            for cat, count in category_stats
        ]
    }
