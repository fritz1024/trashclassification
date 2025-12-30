"""
修复数据库中的时区问题
将所有 UTC 时间转换为本地时间（UTC+8）
"""
from app.core.database import SessionLocal
from app.models.database import ChatConversation, User, Prediction, Feedback, Knowledge
from datetime import timedelta

def fix_timezone():
    """将数据库中的 UTC 时间转换为本地时间（+8小时）"""
    db = SessionLocal()

    try:
        # 修复 ChatConversation 表
        conversations = db.query(ChatConversation).all()
        for conv in conversations:
            if conv.created_at:
                conv.created_at = conv.created_at + timedelta(hours=8)
            if conv.updated_at:
                conv.updated_at = conv.updated_at + timedelta(hours=8)
        print(f"已修复 {len(conversations)} 条对话记录")

        # 修复 User 表
        users = db.query(User).all()
        for user in users:
            if user.created_at:
                user.created_at = user.created_at + timedelta(hours=8)
            if user.updated_at:
                user.updated_at = user.updated_at + timedelta(hours=8)
        print(f"已修复 {len(users)} 条用户记录")

        # 修复 Prediction 表
        predictions = db.query(Prediction).all()
        for pred in predictions:
            if pred.created_at:
                pred.created_at = pred.created_at + timedelta(hours=8)
        print(f"已修复 {len(predictions)} 条识别记录")

        # 修复 Feedback 表
        feedbacks = db.query(Feedback).all()
        for fb in feedbacks:
            if fb.created_at:
                fb.created_at = fb.created_at + timedelta(hours=8)
            if fb.processed_at:
                fb.processed_at = fb.processed_at + timedelta(hours=8)
        print(f"已修复 {len(feedbacks)} 条反馈记录")

        # 修复 Knowledge 表
        knowledge = db.query(Knowledge).all()
        for k in knowledge:
            if k.created_at:
                k.created_at = k.created_at + timedelta(hours=8)
            if k.updated_at:
                k.updated_at = k.updated_at + timedelta(hours=8)
        print(f"已修复 {len(knowledge)} 条知识库记录")

        db.commit()
        print("\n✅ 时区修复完成！所有时间已转换为本地时间（UTC+8）")

    except Exception as e:
        db.rollback()
        print(f"\n❌ 修复失败: {str(e)}")
    finally:
        db.close()


if __name__ == "__main__":
    print("开始修复数据库时区问题...")
    print("将所有 UTC 时间转换为本地时间（+8小时）\n")

    confirm = input("确认执行？这将修改数据库中的所有时间记录 (y/n): ")
    if confirm.lower() == 'y':
        fix_timezone()
    else:
        print("已取消操作")
