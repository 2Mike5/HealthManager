"""
food_seed_data.py — 常见食物营养数据
用于初始化 food_database 表
"""

FOOD_SEED_DATA = [
    # 主食
    {'name': '米饭', 'calories_per_100g': 116, 'protein_per_100g': 2.6, 'fat_per_100g': 0.3, 'carbs_per_100g': 25.9, 'category': '主食'},
    {'name': '馒头', 'calories_per_100g': 221, 'protein_per_100g': 7.0, 'fat_per_100g': 1.1, 'carbs_per_100g': 45.7, 'category': '主食'},
    {'name': '面条(煮)', 'calories_per_100g': 110, 'protein_per_100g': 3.4, 'fat_per_100g': 0.3, 'carbs_per_100g': 24.3, 'category': '主食'},
    {'name': '油条', 'calories_per_100g': 386, 'protein_per_100g': 6.9, 'fat_per_100g': 17.6, 'carbs_per_100g': 51.0, 'category': '主食'},
    {'name': '小米粥', 'calories_per_100g': 46, 'protein_per_100g': 1.4, 'fat_per_100g': 0.7, 'carbs_per_100g': 8.4, 'category': '主食'},
    {'name': '全麦面包', 'calories_per_100g': 246, 'protein_per_100g': 8.5, 'fat_per_100g': 3.4, 'carbs_per_100g': 44.0, 'category': '主食'},
    {'name': '白粥', 'calories_per_100g': 38, 'protein_per_100g': 0.9, 'fat_per_100g': 0.2, 'carbs_per_100g': 8.2, 'category': '主食'},
    {'name': '饺子(猪肉)', 'calories_per_100g': 240, 'protein_per_100g': 10.0, 'fat_per_100g': 10.0, 'carbs_per_100g': 27.0, 'category': '主食'},
    {'name': '包子(猪肉)', 'calories_per_100g': 226, 'protein_per_100g': 8.0, 'fat_per_100g': 8.0, 'carbs_per_100g': 30.0, 'category': '主食'},
    {'name': '馄饨', 'calories_per_100g': 130, 'protein_per_100g': 5.0, 'fat_per_100g': 3.0, 'carbs_per_100g': 20.0, 'category': '主食'},
    {'name': '鸡蛋炒饭', 'calories_per_100g': 180, 'protein_per_100g': 6.0, 'fat_per_100g': 5.0, 'carbs_per_100g': 28.0, 'category': '主食'},
    # 肉类
    {'name': '鸡胸肉', 'calories_per_100g': 133, 'protein_per_100g': 31.0, 'fat_per_100g': 3.6, 'carbs_per_100g': 0, 'category': '肉类'},
    {'name': '鸡腿', 'calories_per_100g': 181, 'protein_per_100g': 26.0, 'fat_per_100g': 8.0, 'carbs_per_100g': 0, 'category': '肉类'},
    {'name': '猪瘦肉', 'calories_per_100g': 143, 'protein_per_100g': 20.3, 'fat_per_100g': 6.2, 'carbs_per_100g': 1.5, 'category': '肉类'},
    {'name': '猪五花肉', 'calories_per_100g': 395, 'protein_per_100g': 14.0, 'fat_per_100g': 37.0, 'carbs_per_100g': 2.5, 'category': '肉类'},
    {'name': '牛瘦肉', 'calories_per_100g': 125, 'protein_per_100g': 20.2, 'fat_per_100g': 4.2, 'carbs_per_100g': 0.2, 'category': '肉类'},
    {'name': '牛排', 'calories_per_100g': 271, 'protein_per_100g': 25.0, 'fat_per_100g': 19.0, 'carbs_per_100g': 0, 'category': '肉类'},
    {'name': '羊腿肉', 'calories_per_100g': 158, 'protein_per_100g': 20.0, 'fat_per_100g': 8.0, 'carbs_per_100g': 0, 'category': '肉类'},
    {'name': '排骨', 'calories_per_100g': 264, 'protein_per_100g': 18.0, 'fat_per_100g': 20.0, 'carbs_per_100g': 2.0, 'category': '肉类'},
    {'name': '培根', 'calories_per_100g': 541, 'protein_per_100g': 12.0, 'fat_per_100g': 49.0, 'carbs_per_100g': 1.3, 'category': '肉类'},
    {'name': '火腿', 'calories_per_100g': 330, 'protein_per_100g': 14.0, 'fat_per_100g': 30.0, 'carbs_per_100g': 1.0, 'category': '肉类'},
    # 水产
    {'name': '三文鱼', 'calories_per_100g': 208, 'protein_per_100g': 20.4, 'fat_per_100g': 13.4, 'carbs_per_100g': 0, 'category': '水产'},
    {'name': '虾仁', 'calories_per_100g': 93, 'protein_per_100g': 20.1, 'fat_per_100g': 0.7, 'carbs_per_100g': 0.2, 'category': '水产'},
    {'name': '带鱼', 'calories_per_100g': 127, 'protein_per_100g': 17.7, 'fat_per_100g': 4.9, 'carbs_per_100g': 0, 'category': '水产'},
    {'name': '鲈鱼', 'calories_per_100g': 105, 'protein_per_100g': 18.6, 'fat_per_100g': 3.4, 'carbs_per_100g': 0, 'category': '水产'},
    {'name': '金枪鱼', 'calories_per_100g': 144, 'protein_per_100g': 23.3, 'fat_per_100g': 4.9, 'carbs_per_100g': 0, 'category': '水产'},
    {'name': '鲫鱼', 'calories_per_100g': 108, 'protein_per_100g': 17.4, 'fat_per_100g': 3.6, 'carbs_per_100g': 0, 'category': '水产'},
    {'name': '蛤蜊', 'calories_per_100g': 62, 'protein_per_100g': 10.0, 'fat_per_100g': 1.0, 'carbs_per_100g': 2.8, 'category': '水产'},
    # 蔬菜
    {'name': '西兰花', 'calories_per_100g': 34, 'protein_per_100g': 2.8, 'fat_per_100g': 0.4, 'carbs_per_100g': 6.6, 'category': '蔬菜'},
    {'name': '菠菜', 'calories_per_100g': 23, 'protein_per_100g': 2.9, 'fat_per_100g': 0.3, 'carbs_per_100g': 3.6, 'category': '蔬菜'},
    {'name': '西红柿', 'calories_per_100g': 18, 'protein_per_100g': 0.9, 'fat_per_100g': 0.2, 'carbs_per_100g': 3.9, 'category': '蔬菜'},
    {'name': '黄瓜', 'calories_per_100g': 15, 'protein_per_100g': 0.8, 'fat_per_100g': 0.1, 'carbs_per_100g': 2.9, 'category': '蔬菜'},
    {'name': '胡萝卜', 'calories_per_100g': 41, 'protein_per_100g': 1.0, 'fat_per_100g': 0.2, 'carbs_per_100g': 9.6, 'category': '蔬菜'},
    {'name': '白菜', 'calories_per_100g': 17, 'protein_per_100g': 1.5, 'fat_per_100g': 0.2, 'carbs_per_100g': 3.1, 'category': '蔬菜'},
    {'name': '生菜', 'calories_per_100g': 15, 'protein_per_100g': 1.3, 'fat_per_100g': 0.2, 'carbs_per_100g': 2.0, 'category': '蔬菜'},
    {'name': '土豆', 'calories_per_100g': 81, 'protein_per_100g': 2.0, 'fat_per_100g': 0.2, 'carbs_per_100g': 17.5, 'category': '蔬菜'},
    {'name': '茄子', 'calories_per_100g': 25, 'protein_per_100g': 1.0, 'fat_per_100g': 0.2, 'carbs_per_100g': 5.7, 'category': '蔬菜'},
    {'name': '青椒', 'calories_per_100g': 22, 'protein_per_100g': 1.0, 'fat_per_100g': 0.2, 'carbs_per_100g': 4.6, 'category': '蔬菜'},
    {'name': '豆芽', 'calories_per_100g': 18, 'protein_per_100g': 1.8, 'fat_per_100g': 0.1, 'carbs_per_100g': 2.8, 'category': '蔬菜'},
    {'name': '芹菜', 'calories_per_100g': 14, 'protein_per_100g': 0.8, 'fat_per_100g': 0.1, 'carbs_per_100g': 3.0, 'category': '蔬菜'},
    {'name': '玉米', 'calories_per_100g': 96, 'protein_per_100g': 3.3, 'fat_per_100g': 1.2, 'carbs_per_100g': 19.0, 'category': '蔬菜'},
    {'name': '南瓜', 'calories_per_100g': 22, 'protein_per_100g': 0.7, 'fat_per_100g': 0.1, 'carbs_per_100g': 5.3, 'category': '蔬菜'},
    # 水果
    {'name': '苹果', 'calories_per_100g': 52, 'protein_per_100g': 0.3, 'fat_per_100g': 0.2, 'carbs_per_100g': 13.8, 'category': '水果'},
    {'name': '香蕉', 'calories_per_100g': 89, 'protein_per_100g': 1.1, 'fat_per_100g': 0.3, 'carbs_per_100g': 22.8, 'category': '水果'},
    {'name': '橙子', 'calories_per_100g': 47, 'protein_per_100g': 0.9, 'fat_per_100g': 0.1, 'carbs_per_100g': 11.8, 'category': '水果'},
    {'name': '葡萄', 'calories_per_100g': 69, 'protein_per_100g': 0.7, 'fat_per_100g': 0.2, 'carbs_per_100g': 18.1, 'category': '水果'},
    {'name': '西瓜', 'calories_per_100g': 30, 'protein_per_100g': 0.6, 'fat_per_100g': 0.2, 'carbs_per_100g': 7.6, 'category': '水果'},
    {'name': '草莓', 'calories_per_100g': 32, 'protein_per_100g': 0.7, 'fat_per_100g': 0.3, 'carbs_per_100g': 7.7, 'category': '水果'},
    {'name': '蓝莓', 'calories_per_100g': 57, 'protein_per_100g': 0.7, 'fat_per_100g': 0.3, 'carbs_per_100g': 14.5, 'category': '水果'},
    {'name': '猕猴桃', 'calories_per_100g': 61, 'protein_per_100g': 1.1, 'fat_per_100g': 0.5, 'carbs_per_100g': 14.7, 'category': '水果'},
    {'name': '柚子', 'calories_per_100g': 38, 'protein_per_100g': 0.8, 'fat_per_100g': 0.1, 'carbs_per_100g': 9.6, 'category': '水果'},
    {'name': '火龙果', 'calories_per_100g': 55, 'protein_per_100g': 1.1, 'fat_per_100g': 0.4, 'carbs_per_100g': 12.0, 'category': '水果'},
    # 乳制品
    {'name': '牛奶(全脂)', 'calories_per_100g': 66, 'protein_per_100g': 3.2, 'fat_per_100g': 3.6, 'carbs_per_100g': 4.8, 'category': '乳制品'},
    {'name': '牛奶(脱脂)', 'calories_per_100g': 34, 'protein_per_100g': 3.4, 'fat_per_100g': 0.1, 'carbs_per_100g': 5.0, 'category': '乳制品'},
    {'name': '酸奶(原味)', 'calories_per_100g': 63, 'protein_per_100g': 3.5, 'fat_per_100g': 1.5, 'carbs_per_100g': 8.5, 'category': '乳制品'},
    {'name': '奶酪', 'calories_per_100g': 350, 'protein_per_100g': 25.0, 'fat_per_100g': 27.0, 'carbs_per_100g': 2.5, 'category': '乳制品'},
    {'name': '黄油', 'calories_per_100g': 717, 'protein_per_100g': 0.9, 'fat_per_100g': 81.0, 'carbs_per_100g': 0.1, 'category': '乳制品'},
    # 蛋类
    {'name': '鸡蛋', 'calories_per_100g': 144, 'protein_per_100g': 13.3, 'fat_per_100g': 8.8, 'carbs_per_100g': 2.8, 'category': '蛋类'},
    {'name': '鸭蛋', 'calories_per_100g': 180, 'protein_per_100g': 12.6, 'fat_per_100g': 13.0, 'carbs_per_100g': 3.1, 'category': '蛋类'},
    {'name': '鹌鹑蛋', 'calories_per_100g': 160, 'protein_per_100g': 12.8, 'fat_per_100g': 11.1, 'carbs_per_100g': 1.0, 'category': '蛋类'},
    # 豆制品
    {'name': '豆腐', 'calories_per_100g': 81, 'protein_per_100g': 8.1, 'fat_per_100g': 3.7, 'carbs_per_100g': 4.2, 'category': '豆制品'},
    {'name': '豆浆', 'calories_per_100g': 31, 'protein_per_100g': 2.9, 'fat_per_100g': 1.2, 'carbs_per_100g': 1.8, 'category': '豆制品'},
    {'name': '豆腐干', 'calories_per_100g': 140, 'protein_per_100g': 16.2, 'fat_per_100g': 7.5, 'carbs_per_100g': 4.0, 'category': '豆制品'},
    {'name': '毛豆', 'calories_per_100g': 131, 'protein_per_100g': 11.9, 'fat_per_100g': 5.0, 'carbs_per_100g': 10.5, 'category': '豆制品'},
    # 零食
    {'name': '薯片', 'calories_per_100g': 536, 'protein_per_100g': 7.0, 'fat_per_100g': 34.0, 'carbs_per_100g': 49.0, 'category': '零食'},
    {'name': '巧克力', 'calories_per_100g': 546, 'protein_per_100g': 4.9, 'fat_per_100g': 31.0, 'carbs_per_100g': 59.0, 'category': '零食'},
    {'name': '饼干', 'calories_per_100g': 433, 'protein_per_100g': 8.0, 'fat_per_100g': 16.0, 'carbs_per_100g': 66.0, 'category': '零食'},
    {'name': '蛋糕', 'calories_per_100g': 347, 'protein_per_100g': 5.3, 'fat_per_100g': 14.0, 'carbs_per_100g': 53.0, 'category': '零食'},
    {'name': '冰淇淋', 'calories_per_100g': 207, 'protein_per_100g': 3.5, 'fat_per_100g': 11.0, 'carbs_per_100g': 24.0, 'category': '零食'},
    {'name': '坚果(混合)', 'calories_per_100g': 553, 'protein_per_100g': 15.0, 'fat_per_100g': 49.0, 'carbs_per_100g': 18.0, 'category': '零食'},
    {'name': '腰果', 'calories_per_100g': 553, 'protein_per_100g': 18.2, 'fat_per_100g': 43.8, 'carbs_per_100g': 30.2, 'category': '零食'},
    {'name': '杏仁', 'calories_per_100g': 578, 'protein_per_100g': 21.2, 'fat_per_100g': 49.9, 'carbs_per_100g': 21.7, 'category': '零食'},
    # 饮品
    {'name': '矿泉水', 'calories_per_100g': 0, 'protein_per_100g': 0, 'fat_per_100g': 0, 'carbs_per_100g': 0, 'category': '饮品'},
    {'name': '可乐', 'calories_per_100g': 42, 'protein_per_100g': 0, 'fat_per_100g': 0, 'carbs_per_100g': 10.6, 'category': '饮品'},
    {'name': '橙汁', 'calories_per_100g': 45, 'protein_per_100g': 0.7, 'fat_per_100g': 0.2, 'carbs_per_100g': 10.4, 'category': '饮品'},
    {'name': '绿茶(无糖)', 'calories_per_100g': 1, 'protein_per_100g': 0, 'fat_per_100g': 0, 'carbs_per_100g': 0.1, 'category': '饮品'},
    {'name': '咖啡(黑)', 'calories_per_100g': 2, 'protein_per_100g': 0.1, 'fat_per_100g': 0, 'carbs_per_100g': 0, 'category': '饮品'},
    {'name': '拿铁咖啡', 'calories_per_100g': 52, 'protein_per_100g': 3.0, 'fat_per_100g': 2.0, 'carbs_per_100g': 5.0, 'category': '饮品'},
    {'name': '啤酒', 'calories_per_100g': 43, 'protein_per_100g': 0.5, 'fat_per_100g': 0, 'carbs_per_100g': 3.6, 'category': '饮品'},
    # 调味品
    {'name': '花生油', 'calories_per_100g': 899, 'protein_per_100g': 0, 'fat_per_100g': 99.9, 'carbs_per_100g': 0, 'category': '调味品'},
    {'name': '酱油', 'calories_per_100g': 53, 'protein_per_100g': 8.0, 'fat_per_100g': 0.1, 'carbs_per_100g': 4.9, 'category': '调味品'},
    {'name': '醋', 'calories_per_100g': 30, 'protein_per_100g': 0.4, 'fat_per_100g': 0, 'carbs_per_100g': 4.7, 'category': '调味品'},
    {'name': '蜂蜜', 'calories_per_100g': 304, 'protein_per_100g': 0.3, 'fat_per_100g': 0, 'carbs_per_100g': 82.1, 'category': '调味品'},
    {'name': '白糖', 'calories_per_100g': 387, 'protein_per_100g': 0, 'fat_per_100g': 0, 'carbs_per_100g': 100.0, 'category': '调味品'},
    {'name': '盐', 'calories_per_100g': 0, 'protein_per_100g': 0, 'fat_per_100g': 0, 'carbs_per_100g': 0, 'category': '调味品'},
]


def seed_food_database():
    """向 food_database 写入种子数据（幂等）"""
    from models import get_db
    db = get_db()
    existing = db.execute("SELECT COUNT(*) as cnt FROM food_database").fetchone()
    if existing and existing['cnt'] > 0:
        db.close()
        return
    for item in FOOD_SEED_DATA:
        try:
            db.execute("""
                INSERT INTO food_database (name, calories_per_100g, protein_per_100g, fat_per_100g, carbs_per_100g, category)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (item['name'], item['calories_per_100g'], item['protein_per_100g'],
                  item['fat_per_100g'], item['carbs_per_100g'], item['category']))
        except Exception:
            pass
    db.commit()
    db.close()
