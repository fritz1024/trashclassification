"""
数据库初始化脚本
创建默认管理员账号和初始数据
"""
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine
from app.models.database import Base, User, Knowledge
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

        # 检查是否已有知识库数据
        knowledge_count = db.query(Knowledge).count()
        if knowledge_count == 0:
            # 添加初始知识库数据
            initial_knowledge = [
                {
                    "category": "可回收垃圾",
                    "title": "什么是可回收垃圾",
                    "content": "可回收垃圾是指适宜回收和资源化利用的生活废弃物。",
                    "examples": ["废纸", "塑料瓶", "玻璃瓶", "金属罐", "旧衣物"],
                    "tips": "投放前应清洗干净，保持干燥。纸类应叠放整齐，避免揉团。"
                },
                {
                    "category": "有害垃圾",
                    "title": "什么是有害垃圾",
                    "content": "有害垃圾是指对人体健康或自然环境造成直接或潜在危害的生活废弃物。",
                    "examples": ["废电池", "废灯管", "过期药品", "油漆桶", "杀虫剂"],
                    "tips": "投放时要轻拿轻放，避免破损。废灯管等易碎品应包裹后投放。"
                },
                {
                    "category": "厨余垃圾",
                    "title": "什么是厨余垃圾",
                    "content": "厨余垃圾是指家庭日常生活中产生的易腐性垃圾。",
                    "examples": ["剩菜剩饭", "果皮", "菜叶", "茶叶渣", "骨头"],
                    "tips": "投放前应沥干水分，去除包装物。大块骨头属于其他垃圾。"
                },
                {
                    "category": "其他垃圾",
                    "title": "什么是其他垃圾",
                    "content": "其他垃圾是指除可回收物、有害垃圾、厨余垃圾以外的生活废弃物。",
                    "examples": ["污损纸张", "一次性餐具", "烟蒂", "尘土", "陶瓷制品"],
                    "tips": "难以辨别类别的垃圾可投入其他垃圾桶。"
                }
            ]

            for item in initial_knowledge:
                knowledge = Knowledge(**item)
                db.add(knowledge)

            print("✓ 添加初始知识库数据")

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
