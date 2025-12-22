"""
初始化知识库数据
"""
from app.core.database import SessionLocal
from app.models.database import Knowledge

def init_knowledge():
    db = SessionLocal()

    # 检查是否已有数据
    existing = db.query(Knowledge).first()
    if existing:
        print("知识库已有数据，跳过初始化")
        db.close()
        return

    # 初始化知识数据
    knowledge_data = [
        # 可回收垃圾
        {
            "category": "recyclable",
            "title": "塑料瓶",
            "content": "塑料瓶是可回收垃圾，包括饮料瓶、矿泉水瓶等。",
            "examples": "可乐瓶、矿泉水瓶、洗发水瓶",
            "tips": "清空瓶内液体，压扁后投放"
        },
        {
            "category": "recyclable",
            "title": "纸张",
            "content": "干净的纸张、报纸、书本、纸箱等都是可回收垃圾。",
            "examples": "报纸、杂志、纸箱、办公用纸",
            "tips": "保持干燥，避免污染"
        },
        {
            "category": "recyclable",
            "title": "金属制品",
            "content": "金属罐、铁罐、铝罐等金属制品可以回收利用。",
            "examples": "易拉罐、铁罐、铝制品",
            "tips": "清洗干净后投放"
        },

        # 有害垃圾
        {
            "category": "harmful",
            "title": "电池",
            "content": "废旧电池含有重金属，属于有害垃圾，需要专门处理。",
            "examples": "干电池、纽扣电池、充电电池",
            "tips": "单独收集，投放到有害垃圾回收点"
        },
        {
            "category": "harmful",
            "title": "过期药品",
            "content": "过期的药品和药物包装属于有害垃圾。",
            "examples": "过期药片、药水、药膏",
            "tips": "连同包装一起投放"
        },
        {
            "category": "harmful",
            "title": "废旧灯管",
            "content": "节能灯、荧光灯管含有汞，属于有害垃圾。",
            "examples": "节能灯、荧光灯管、LED灯",
            "tips": "小心包装，避免破碎"
        },

        # 厨余垃圾
        {
            "category": "kitchen",
            "title": "果皮果核",
            "content": "水果的果皮、果核等属于厨余垃圾。",
            "examples": "苹果核、香蕉皮、西瓜皮",
            "tips": "沥干水分后投放"
        },
        {
            "category": "kitchen",
            "title": "剩菜剩饭",
            "content": "吃剩的饭菜、食物残渣属于厨余垃圾。",
            "examples": "剩饭、剩菜、面条",
            "tips": "去除包装物，沥干水分"
        },
        {
            "category": "kitchen",
            "title": "茶叶渣",
            "content": "泡过的茶叶、咖啡渣等属于厨余垃圾。",
            "examples": "茶叶渣、咖啡渣、中药渣",
            "tips": "沥干水分后投放"
        },

        # 其他垃圾
        {
            "category": "other",
            "title": "污染纸张",
            "content": "被污染的纸张、纸巾等属于其他垃圾。",
            "examples": "餐巾纸、卫生纸、湿纸巾",
            "tips": "直接投放到其他垃圾桶"
        },
        {
            "category": "other",
            "title": "烟蒂",
            "content": "香烟烟蒂属于其他垃圾。",
            "examples": "烟蒂、烟灰",
            "tips": "确保完全熄灭后投放"
        },
        {
            "category": "other",
            "title": "陶瓷制品",
            "content": "破损的陶瓷、瓷器等属于其他垃圾。",
            "examples": "碎碗、碎盘、陶瓷杯",
            "tips": "小心包装，避免划伤"
        }
    ]

    # 添加到数据库
    for data in knowledge_data:
        knowledge = Knowledge(**data)
        db.add(knowledge)

    db.commit()
    print(f"成功初始化 {len(knowledge_data)} 条知识数据")
    db.close()

if __name__ == "__main__":
    init_knowledge()
