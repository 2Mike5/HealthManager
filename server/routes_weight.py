"""
routes_weight.py — 体重记录 API
"""
from datetime import datetime
from flask import Blueprint, request, jsonify
from auth import require_auth, success, error
from models import get_db

weight_bp = Blueprint('weight', __name__, url_prefix='/api/weight')


@weight_bp.route('', methods=['POST'])
@require_auth
def create_weight():
    data = request.get_json(silent=True) or {}
    date = data.get('date', datetime.now().strftime('%Y-%m-%d'))
    weight = data.get('weight')
    body_fat = data.get('body_fat')

    if weight is None:
        return error(400, '体重不能为空')

    db = get_db()
    existing = db.execute(
        "SELECT id FROM weight_records WHERE user_id = ? AND date = ?",
        (request.user_id, date)
    ).fetchone()
    if existing:
        db.execute(
            "UPDATE weight_records SET weight = ?, body_fat = ? WHERE id = ?",
            (weight, body_fat, existing['id'])
        )
    else:
        db.execute(
            "INSERT INTO weight_records (user_id, date, weight, body_fat) VALUES (?, ?, ?, ?)",
            (request.user_id, date, weight, body_fat)
        )
    db.commit()
    row = db.execute(
        "SELECT * FROM weight_records WHERE user_id = ? AND date = ?",
        (request.user_id, date)
    ).fetchone()
    db.close()
    return success(dict(row), '保存成功'), 201


@weight_bp.route('', methods=['GET'])
@require_auth
def list_weight():
    start = request.args.get('start_date')
    end = request.args.get('end_date')
    limit = request.args.get('limit', 100)

    db = get_db()
    query = "SELECT * FROM weight_records WHERE user_id = ?"
    params = [request.user_id]
    if start:
        query += " AND date >= ?"
        params.append(start)
    if end:
        query += " AND date <= ?"
        params.append(end)
    query += " ORDER BY date DESC LIMIT ?"
    params.append(limit)
    rows = db.execute(query, params).fetchall()
    db.close()
    return success([dict(r) for r in rows])


@weight_bp.route('/latest', methods=['GET'])
@require_auth
def latest_weight():
    db = get_db()
    row = db.execute(
        "SELECT * FROM weight_records WHERE user_id = ? ORDER BY date DESC LIMIT 1",
        (request.user_id,)
    ).fetchone()
    db.close()
    if row is None:
        return success(None)

    # 计算 BMI
    user_db = get_db()
    user = user_db.execute(
        "SELECT height FROM users WHERE id = ?", (request.user_id,)
    ).fetchone()
    user_db.close()

    result = dict(row)
    if user and user['height'] and user['height'] > 0:
        bmi = round(row['weight'] / ((user['height'] / 100) ** 2), 1)
        result['bmi'] = bmi
        if bmi < 18.5:
            result['bmi_label'] = '偏瘦'
        elif bmi < 24:
            result['bmi_label'] = '正常'
        elif bmi < 28:
            result['bmi_label'] = '超重'
        else:
            result['bmi_label'] = '肥胖'
    return success(result)


@weight_bp.route('/<int:wid>', methods=['DELETE'])
@require_auth
def delete_weight(wid):
    db = get_db()
    row = db.execute(
        "SELECT id FROM weight_records WHERE id = ? AND user_id = ?",
        (wid, request.user_id)
    ).fetchone()
    if row is None:
        db.close()
        return error(404, '记录不存在')
    db.execute("DELETE FROM weight_records WHERE id = ?", (wid,))
    db.commit()
    db.close()
    return success(None, '删除成功')
