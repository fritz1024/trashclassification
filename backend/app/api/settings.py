"""
系统设置API路由
"""
from fastapi import APIRouter

router = APIRouter(prefix="/api/settings", tags=["settings"])


@router.get("/")
def get_settings():
    """获取系统设置"""
    return {"message": "系统设置功能开发中"}
