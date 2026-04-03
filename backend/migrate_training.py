"""
数据库迁移脚本：添加训练相关表
"""
import sqlite3
import os

# 数据库文件路径
DB_PATH = os.path.join(os.path.dirname(__file__), "trash_classify.db")

def migrate():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        print("开始迁移数据库...")

        # 创建训练数据集表
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS training_datasets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(255) NOT NULL,
            source_type VARCHAR(20) NOT NULL,
            file_path VARCHAR(500),
            class_count INTEGER DEFAULT 0,
            image_count INTEGER DEFAULT 0,
            created_by INTEGER NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (created_by) REFERENCES users(id)
        )
        """)
        print("✓ 创建 training_datasets 表")

        # 创建训练任务表
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS training_jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(255) NOT NULL,
            dataset_id INTEGER NOT NULL,
            status VARCHAR(20) DEFAULT 'pending',
            training_params TEXT,
            progress REAL DEFAULT 0.0,
            current_epoch INTEGER DEFAULT 0,
            total_epochs INTEGER DEFAULT 10,
            loss REAL,
            accuracy REAL,
            model_path VARCHAR(500),
            created_by INTEGER NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            started_at DATETIME,
            completed_at DATETIME,
            FOREIGN KEY (dataset_id) REFERENCES training_datasets(id),
            FOREIGN KEY (created_by) REFERENCES users(id)
        )
        """)
        print("✓ 创建 training_jobs 表")

        # 创建索引
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_training_datasets_created_at ON training_datasets(created_at)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_training_jobs_created_at ON training_jobs(created_at)")
        print("✓ 创建索引")

        conn.commit()
        print("\n数据库迁移成功！")

    except sqlite3.Error as e:
        print(f"迁移失败: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
