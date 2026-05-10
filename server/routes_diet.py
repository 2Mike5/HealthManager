"""
routes_diet.py — 饮食记录 + 食物库 API
"""
from datetime import datetime
from flask import Blueprint, request, jsonify
from auth import require_auth, success, error
from models import get_db

diet_bp = Blueprint('diet', __name__, url_prefix='/api/diet')


@diet_bp.route('/records', methods=['POST'])
@require_auth
def create_diet_record():
    data = request.get_json(silent=True) or {}
    date = data.get('date', datetime.now().strftime('%Y-%m-%d'))
    meal_type = data.get('meal_type')
    food_name = data.get('food_name')

    if not meal_type:
        return error(400, '餐次不能为空')
    if not food_name:
        return error(400, '食物名称不能为空')

    db = get_db()
    db.execute("""
        INSERT INTO diet_records
            (user_id, date, meal_type, food_name, amount, unit,
             calories, protein, fat, carbs)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        request.user_id, date, meal_type, food_name,
        data.get('amount', 100), data.get('unit', 'g'),
        data.get('calories', 0), data.get('protein', 0),
        data.get('fat', 0), data.get('carbs', 0)
    ))
    db.commit()
    row = db.execute(
        "SELECT * FROM diet_records WHERE id = last_insert_rowid()"
    ).fetchone()
    db.close()
    return success(dict(row), '添加成功'), 201


@diet_bp.route('/records', methods=['GET'])
@require_auth
def list_diet_records():
    date = request.args.get('date')
    start = request.args.get('start_date')
    end = request.args.get('end_date')
    meal_type = request.args.get('meal_type')

    db = get_db()
    query = "SELECT * FROM diet_records WHERE user_id = ?"
    params = [request.user_id]
    if date:
        query += " AND date = ?"
        params.append(date)
    if start:
        query += " AND date >= ?"
        params.append(start)
    if end:
        query += " AND date <= ?"
        params.append(end)
    if meal_type:
        query += " AND meal_type = ?"
        params.append(meal_type)
    query += " ORDER BY date DESC, id ASC"
    rows = db.execute(query, params).fetchall()
    db.close()
    return success([dict(r) for r in rows])


@diet_bp.route('/records/<int:did>', methods=['DELETE'])
@require_auth
def delete_diet_record(did):
    db = get_db()
    row = db.execute(
        "SELECT id FROM diet_records WHERE id = ? AND user_id = ?",
        (did, request.user_id)
    ).fetchone()
    if row is None:
        db.close()
        return error(404, '记录不存在')
    db.execute("DELETE FROM diet_records WHERE id = ?", (did,))
    db.commit()
    db.close()
    return success(None, '删除成功')


@diet_bp.route('/summary', methods=['GET'])
@require_auth
def diet_summary():
    date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    db = get_db()
    rows = db.execute(
        "SELECT * FROM diet_records WHERE user_id = ? AND date = ?",
        (request.user_id, date)
    ).fetchall()

    total_calories = 0
    total_protein = 0
    total_fat = 0
    total_carbs = 0
    by_meal = {}

    for r in rows:
        total_calories += r['calories'] or 0
        total_protein += r['protein'] or 0
        total_fat += r['fat'] or 0
        total_carbs += r['carbs'] or 0
        mt = r['meal_type']
        if mt not in by_meal:
            by_meal[mt] = {'calories': 0, 'items': []}
        by_meal[mt]['calories'] += r['calories'] or 0
        by_meal[mt]['items'].append(dict(r))

    db.close()
    return success({
        'date': date,
        'total_calories': round(total_calories, 1),
        'total_protein': round(total_protein, 1),
        'total_fat': round(total_fat, 1),
        'total_carbs': round(total_carbs, 1),
        'by_meal': by_meal,
        'count': len(rows)
    })


# ─── 食物库 ───

food_bp = Blueprint('food', __name__, url_prefix='/api/foods')


@food_bp.route('', methods=['GET'])
def list_foods():
    keyword = request.args.get('keyword', '')
    category = request.args.get('category', '')
    limit = request.args.get('limit', 50)

    db = get_db()
    query = "SELECT * FROM food_database WHERE 1=1"
    params = []
    if keyword:
        query += " AND name LIKE ?"
        params.append(f'%{keyword}%')
    if category:
        query += " AND category = ?"
        params.append(category)
    query += " ORDER BY category, name LIMIT ?"
    params.append(limit)
    rows = db.execute(query, params).fetchall()
    db.close()
    return success([dict(r) for r in rows])


@food_bp.route('/categories', methods=['GET'])
def list_categories():
    db = get_db()
    rows = db.execute(
        "SELECT DISTINCT category FROM food_database WHERE category != '' ORDER BY category"
    ).fetchall()
    db.close()
    return success([r['category'] for r in rows])
