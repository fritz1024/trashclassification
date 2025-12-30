"""
更新知识库分类为英文值
"""
from app.core.database import SessionLocal
from app.models.database import Knowledge

def update_categories():
    db = SessionLocal()

    # 分类映射
    category_map = {
        '可回收垃圾': 'recyclable',
        '有害垃圾': 'harmful',
        '厨余垃圾': 'kitchen',
        '其他垃圾': 'other'
    }

    # 查询所有知识
    knowledge_list = db.query(Knowledge).all()

    updated_count = 0
    for knowledge in knowledge_list:
        if knowledge.category in category_map:
            old_category = knowledge.category
            knowledge.category = category_map[old_category]
            updated_count += 1
            print(f"更新 ID {knowledge.id}: {old_category} -> {knowledge.category}")

    db.commit()
    print(f"\n成功更新 {updated_count} 条记录")
    db.close()

if __name__ == "__main__":
    update_categories()
