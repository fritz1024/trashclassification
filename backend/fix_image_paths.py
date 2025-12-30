"""
修复数据库中的图片路径（将反斜杠转换为正斜杠）
"""
from app.core.database import SessionLocal
from app.models.database import Prediction

def fix_image_paths():
    db = SessionLocal()
    try:
        # 查询所有记录
        predictions = db.query(Prediction).all()

        fixed_count = 0
        for pred in predictions:
            # 将反斜杠替换为正斜杠
            if '\\' in pred.image_path:
                old_path = pred.image_path
                pred.image_path = pred.image_path.replace('\\', '/')
                fixed_count += 1
                print(f"Fixed: {old_path} -> {pred.image_path}")

        db.commit()
        print(f"\nTotal fixed: {fixed_count} records")

    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_image_paths()
