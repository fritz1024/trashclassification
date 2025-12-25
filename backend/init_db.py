"""
数据库初始化脚本
创建默认管理员账号和初始数据
"""
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine
from app.models.database import Base, User
from app.core.security import get_password_hash


def init_db():
    """初始化数据库"""
    # 创建所有表
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        # 检查是否已有管理员
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            # 创建默认管理员账号
            admin = User(
                username="admin",
                email="admin@example.com",
                password_hash=get_password_hash("123456"),
                role="admin",
                is_active=True
            )
            db.add(admin)
            print("✓ 创建默认管理员账号: admin / 123456")
        db.commit()
        print("\n数据库初始化完成！")

    except Exception as e:
        print(f"初始化失败: {str(e)}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print("开始初始化数据库...")
    init_db()
