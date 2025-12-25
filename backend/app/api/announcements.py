"""
公告管理相关API路由
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.core.database import get_db
from app.models.database import Announcement
from app.api.auth import require_admin
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

router = APIRouter(prefix="/api/announcements", tags=["公告管理"])


class AnnouncementCreate(BaseModel):
    """创建公告请求模型"""
    title: str
    content: str
    type: str = "info"
    is_published: bool = True
    priority: int = 0


class AnnouncementUpdate(BaseModel):
    """更新公告请求模型"""
    title: Optional[str] = None
    content: Optional[str] = None
    type: Optional[str] = None
    is_published: Optional[bool] = None
    priority: Optional[int] = None


@router.get("/list")
def get_announcements(
    skip: int = 0,
    limit: int = 20,
    published_only: bool = False,
    db: Session = Depends(get_db)
):
    """获取公告列表（公开接口）"""
    query = db.query(Announcement)
    
    if published_only:
        query = query.filter(Announcement.is_published == True)
    
    total = query.count()
    announcements = query.order_by(
        desc(Announcement.priority),
        desc(Announcement.created_at)
    ).offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "items": [
            {
                "id": a.id,
                "title": a.title,
                "content": a.content,
                "type": a.type,
                "is_published": a.is_published,
                "priority": a.priority,
                "created_at": a.created_at,
                "updated_at": a.updated_at
            }
            for a in announcements
        ]
    }


@router.post("/create")
def create_announcement(
    announcement: AnnouncementCreate,
    db: Session = Depends(get_db),
    admin_user = Depends(require_admin)
):
    """创建公告（管理员）"""
    new_announcement = Announcement(
        title=announcement.title,
        content=announcement.content,
        type=announcement.type,
        is_published=announcement.is_published,
        priority=announcement.priority
    )
    
    db.add(new_announcement)
    db.commit()
    db.refresh(new_announcement)
    
    return {
        "message": "公告创建成功",
        "id": new_announcement.id
    }


@router.put("/update/{announcement_id}")
def update_announcement(
    announcement_id: int,
    announcement: AnnouncementUpdate,
    db: Session = Depends(get_db),
    admin_user = Depends(require_admin)
):
    """更新公告（管理员）"""
    db_announcement = db.query(Announcement).filter(Announcement.id == announcement_id).first()
    
    if not db_announcement:
        raise HTTPException(status_code=404, detail="公告不存在")
    
    if announcement.title is not None:
        db_announcement.title = announcement.title
    if announcement.content is not None:
        db_announcement.content = announcement.content
    if announcement.type is not None:
        db_announcement.type = announcement.type
    if announcement.is_published is not None:
        db_announcement.is_published = announcement.is_published
    if announcement.priority is not None:
        db_announcement.priority = announcement.priority
    
    db_announcement.updated_at = datetime.now()
    db.commit()
    
    return {"message": "公告更新成功"}


@router.delete("/delete/{announcement_id}")
def delete_announcement(
    announcement_id: int,
    db: Session = Depends(get_db),
    admin_user = Depends(require_admin)
):
    """删除公告（管理员）"""
    db_announcement = db.query(Announcement).filter(Announcement.id == announcement_id).first()
    
    if not db_announcement:
        raise HTTPException(status_code=404, detail="公告不存在")
    
    db.delete(db_announcement)
    db.commit()
    
    return {"message": "公告删除成功"}
