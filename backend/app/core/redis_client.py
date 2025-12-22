"""
Redis 工具类
用于管理 token 和在线用户
"""
import redis
from typing import Optional
from app.core.config import settings


class RedisClient:
    """Redis 客户端"""

    def __init__(self):
        self.client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            password=settings.REDIS_PASSWORD,
            decode_responses=True  # 自动解码为字符串
        )

    def set_token(self, token: str, user_id: int, expire_seconds: int = None):
        """
        存储 token

        Args:
            token: JWT token
            user_id: 用户ID
            expire_seconds: 过期时间（秒），默认使用配置的过期时间
        """
        if expire_seconds is None:
            expire_seconds = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60

        # 存储 token -> user_id 映射
        self.client.setex(
            f"token:{token}",
            expire_seconds,
            str(user_id)
        )

        # 存储 user_id -> token 映射（用于单点登录）
        self.client.setex(
            f"user:{user_id}:token",
            expire_seconds,
            token
        )

    def get_user_id_by_token(self, token: str) -> Optional[int]:
        """
        通过 token 获取用户ID

        Args:
            token: JWT token

        Returns:
            用户ID，如果 token 不存在或已过期则返回 None
        """
        user_id = self.client.get(f"token:{token}")
        return int(user_id) if user_id else None

    def delete_token(self, token: str, user_id: int = None):
        """
        删除 token（用户登出）

        Args:
            token: JWT token
            user_id: 用户ID（可选）
        """
        # 如果没有提供 user_id，先从 Redis 获取
        if user_id is None:
            user_id = self.get_user_id_by_token(token)

        # 删除 token
        self.client.delete(f"token:{token}")

        # 删除用户的 token 映射
        if user_id:
            self.client.delete(f"user:{user_id}:token")

    def is_token_valid(self, token: str) -> bool:
        """
        检查 token 是否有效

        Args:
            token: JWT token

        Returns:
            True 如果 token 有效，否则 False
        """
        return self.client.exists(f"token:{token}") > 0

    def kick_user(self, user_id: int):
        """
        踢用户下线（管理员功能）

        Args:
            user_id: 用户ID
        """
        # 获取用户的 token
        token = self.client.get(f"user:{user_id}:token")
        if token:
            # 删除 token
            self.delete_token(token, user_id)

    def get_online_users_count(self) -> int:
        """
        获取在线用户数量

        Returns:
            在线用户数量
        """
        # 统计所有 user:*:token 的数量
        keys = self.client.keys("user:*:token")
        return len(keys)

    def get_online_users(self) -> list:
        """
        获取所有在线用户ID列表

        Returns:
            在线用户ID列表
        """
        keys = self.client.keys("user:*:token")
        user_ids = []
        for key in keys:
            # 从 key 中提取 user_id
            # key 格式: user:123:token
            parts = key.split(":")
            if len(parts) == 3:
                user_ids.append(int(parts[1]))
        return user_ids

    def extend_token_expire(self, token: str, expire_seconds: int = None):
        """
        延长 token 过期时间

        Args:
            token: JWT token
            expire_seconds: 新的过期时间（秒）
        """
        if expire_seconds is None:
            expire_seconds = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60

        user_id = self.get_user_id_by_token(token)
        if user_id:
            # 延长 token 过期时间
            self.client.expire(f"token:{token}", expire_seconds)
            self.client.expire(f"user:{user_id}:token", expire_seconds)


# 全局 Redis 客户端实例
redis_client = RedisClient()
