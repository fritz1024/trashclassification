"""
知识库表结构迁移脚本
添加博文相关字段: summary, cover_image, author, view_count, is_published
"""
import sqlite3
from pathlib import Path

def migrate_knowledge_table():
    db_path = Path(__file__).parent / "trash_classify.db"

    if not db_path.exists():
        print("数据库文件不存在，无需迁移")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # 检查表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='knowledge'")
        if not cursor.fetchone():
            print("knowledge 表不存在，无需迁移")
            return

        # 获取现有列
        cursor.execute("PRAGMA table_info(knowledge)")
        existing_columns = {row[1] for row in cursor.fetchall()}

        # 需要添加的新列
        new_columns = {
            'summary': 'ALTER TABLE knowledge ADD COLUMN summary VARCHAR(500)',
            'cover_image': 'ALTER TABLE knowledge ADD COLUMN cover_image VARCHAR(255)',
            'author': 'ALTER TABLE knowledge ADD COLUMN author VARCHAR(100) DEFAULT "系统管理员"',
            'view_count': 'ALTER TABLE knowledge ADD COLUMN view_count INTEGER DEFAULT 0',
            'is_published': 'ALTER TABLE knowledge ADD COLUMN is_published BOOLEAN DEFAULT 1'
        }

        # 添加缺失的列
        for col_name, sql in new_columns.items():
            if col_name not in existing_columns:
                print(f"添加列: {col_name}")
                cursor.execute(sql)

        conn.commit()
        print("[SUCCESS] Knowledge table migration completed")

    except Exception as e:
        conn.rollback()
        print(f"[ERROR] Migration failed: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_knowledge_table()
