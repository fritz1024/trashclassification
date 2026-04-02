"""
认证相关API路由
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.security.http import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional
import os
import uuid
from app.core.database import get_db
from app.core.security import verify_password, get_password_hash, create_access_token, decode_access_token
from app.core.redis_client import redis_client
from app.core.config import settings
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token, PasswordUpdate, UserUpdate
from app.models.database import User
from datetime import timedelta
from app.core.config import settings

router = APIRouter(prefix="/api/auth", tags=["认证"])
security = HTTPBearer()


# 依赖项：获取当前用户
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """获取当前登录用户"""
    token = credentials.credentials

    # 1. 先检查 Redis 中 token 是否有效
    if not redis_client.is_token_valid(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token已过期或无效，请重新登录"
        )

    # 2. 从 Redis 获取 user_id
    user_id = redis_client.get_user_id_by_token(token)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭证"
        )

    # 3. 从数据库获取用户信息
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在"
        )

    # 4. 延长 token 过期时间（活跃用户自动续期）
    redis_client.extend_token_expire(token)

    return user


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """获取当前激活用户"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="账号已被禁用"
        )
    return current_user


def require_admin(current_user: User = Depends(get_current_active_user)) -> User:
    """要求管理员权限"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限"
        )
    return current_user


def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer(auto_error=False)),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """获取当前用户（可选，不强制登录）"""
    if credentials is None:
        return None

    try:
        token = credentials.credentials

        # 检查 Redis 中 token 是否有效
        if not redis_client.is_token_valid(token):
            return None

        # 从 Redis 获取 user_id
        user_id = redis_client.get_user_id_by_token(token)
        if user_id is None:
            return None

        # 从数据库获取用户信息
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            return None

        # 延长 token 过期时间
        redis_client.extend_token_expire(token)

        return user
    except Exception:
        return None


@router.post("/register", response_model=UserResponse)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """用户注册"""
    # 检查用户名是否已存在
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )

    # 检查邮箱是否已存在
    if user_data.email:
        existing_email = db.query(User).filter(User.email == user_data.email).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已被使用"
            )

    # 创建新用户
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=get_password_hash(user_data.password),
        role="user"
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.post("/login", response_model=Token)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """用户登录"""
    # 查找用户
    user = db.query(User).filter(User.username == user_data.username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )

    # 验证密码
    if not verify_password(user_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )

    # 检查用户是否被禁用
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="账号已被禁用"
        )

    # 生成JWT token
    access_token = create_access_token(
        data={"sub": str(user.id), "username": user.username, "role": user.role}
    )

    # 将 token 存储到 Redis
    redis_client.set_token(
        token=access_token,
        user_id=user.id,
        expire_seconds=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }


@router.post("/logout")
def logout(current_user: User = Depends(get_current_user), credentials: HTTPAuthorizationCredentials = Depends(security)):
    """用户登出"""
    token = credentials.credentials

    # 从 Redis 删除 token
    redis_client.delete_token(token, current_user.id)

    return {"message": "登出成功"}


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """获取当前用户信息"""
    return current_user


@router.put("/password")
def update_password(
    password_data: PasswordUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """修改密码"""
    # 验证旧密码
    if not verify_password(password_data.old_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="旧密码错误"
        )

    # 更新密码
    current_user.password_hash = get_password_hash(password_data.new_password)
    db.commit()

    return {"message": "密码修改成功"}


@router.put("/profile", response_model=UserResponse)
def update_profile(
    profile_data: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """更新个人资料"""
    # 更新邮箱
    if profile_data.email is not None:
        # 检查邮箱是否已被其他用户使用
        if profile_data.email:
            existing = db.query(User).filter(
                User.email == profile_data.email,
                User.id != current_user.id
            ).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="邮箱已被其他用户使用"
                )
        current_user.email = profile_data.email

    db.commit()
    db.refresh(current_user)
    return current_user


@router.post("/avatar", response_model=UserResponse)
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """上传用户头像"""
    # 检查文件类型
    allowed = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in allowed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="仅支持 jpg/png/gif/webp 格式的图片"
        )

    # 检查文件大小 (2MB)
    contents = await file.read()
    if len(contents) > 2 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="头像文件不能超过 2MB"
        )

    # 保存文件
    avatar_dir = os.path.join(settings.UPLOAD_DIR, "avatars")
    os.makedirs(avatar_dir, exist_ok=True)

    filename = f"{current_user.id}_{uuid.uuid4().hex[:8]}{ext}"
    filepath = os.path.join(avatar_dir, filename)

    with open(filepath, "wb") as f:
        f.write(contents)

    # 删除旧头像文件
    if current_user.avatar:
        old_path = os.path.join(".", current_user.avatar)
        if os.path.exists(old_path):
            os.remove(old_path)

    # 更新数据库
    avatar_path = f"uploads/avatars/{filename}"
    current_user.avatar = avatar_path
    db.commit()
    db.refresh(current_user)

    return current_user
