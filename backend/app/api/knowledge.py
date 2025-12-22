"""
知识库API路由（用户端）
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.models.database import Knowledge
from sqlalchemy import desc

router = APIRouter(prefix="/api/knowledge", tags=["知识库"])


@router.get("")
def get_knowledge_list(
    category: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """获取知识库列表（用户端）"""
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

    # 格式化返回数据
    items = []
    for knowledge in knowledge_list:
        item = {
            "id": knowledge.id,
            "category": knowledge.category,
            "title": knowledge.title,
            "content": knowledge.content,
            "examples": knowledge.examples if knowledge.examples else [],
            "tips": knowledge.tips,
            "created_at": knowledge.created_at
        }
        items.append(item)

    return {
        "total": total,
        "items": items
    }
