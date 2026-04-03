"""
数据库迁移脚本：为 feedbacks 表添加新字段
"""
import sqlite3
import os

# 数据库文件路径
DB_PATH = os.path.join(os.path.dirname(__file__), "trash_classify.db")

def migrate():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # 添加新字段
        print("开始迁移数据库...")

        cursor.execute("ALTER TABLE feedbacks ADD COLUMN processed_by INTEGER")
        print("✓ 添加 processed_by 字段")

        cursor.execute("ALTER TABLE feedbacks ADD COLUMN process_result VARCHAR(20)")
        print("✓ 添加 process_result 字段")

        cursor.execute("ALTER TABLE feedbacks ADD COLUMN process_comment TEXT")
        print("✓ 添加 process_comment 字段")

        cursor.execute("ALTER TABLE feedbacks ADD COLUMN notified BOOLEAN DEFAULT 0")
        print("✓ 添加 notified 字段")

        cursor.execute("ALTER TABLE feedbacks ADD COLUMN processed_at DATETIME")
        print("✓ 添加 processed_at 字段")

        conn.commit()
        print("\n数据库迁移成功！")

    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print(f"字段已存在，跳过: {e}")
        else:
            print(f"迁移失败: {e}")
            conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
