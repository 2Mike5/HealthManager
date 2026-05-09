import random
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from models import get_db

api = Blueprint('api', __name__, url_prefix='/api')

def success(data=None, message='ok'):
    return jsonify({'code': 200, 'data': data, 'message': message})

def error(code, message):
    return jsonify({'code': code, 'data': None, 'message': message}), code
# ──────────────────────────── CRUD ────────────────────────────

@api.route('/records', methods=['GET'])
def list_records():
    start = request.args.get('start_date')
    end = request.args.get('end_date')
    db = get_db()
    query = "SELECT * FROM health_records"
    params = []
    conditions = []
    if start:
        conditions.append("date >= ?")
        params.append(start)
    if end:
        conditions.append("date <= ?")
        params.append(end)
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    query += " ORDER BY date DESC"
    rows = db.execute(query, params).fetchall()
    db.close()
    return success([dict(r) for r in rows])

@api.route('/records/<int:rid>', methods=['GET'])
def get_record(rid):
    db = get_db()
    row = db.execute("SELECT * FROM health_records WHERE id = ?", (rid,)).fetchone()
    db.close()
    if row is None:
        return error(404, '记录不存在')
    return success(dict(row))

@api.route('/records', methods=['POST'])
def create_record():
    data = request.get_json(silent=True)
    if not data or not data.get('date'):
        return error(400, '缺少必填字段 date')
    db = get_db()
    existing = db.execute(
        "SELECT id FROM health_records WHERE date = ?", (data['date'],)
    ).fetchone()
    if existing:
        db.close()
        return error(409, f"日期 {data['date']} 的记录已存在")

    fields = [
        'date', 'steps', 'heart_rate', 'hr_min', 'hr_avg', 'hr_max',
        'sleep', 'water', 'exercise', 'mood', 'health_score'
    ]
    values = {k: data.get(k) for k in fields}
    now = datetime.now().isoformat()
    values['created_at'] = now
    values['updated_at'] = now

    cols = ', '.join(values.keys())
    placeholders = ', '.join('?' for _ in values)
    db.execute(
        f"INSERT INTO health_records ({cols}) VALUES ({placeholders})",
        list(values.values())
    )
    db.commit()
    row = db.execute(
        "SELECT * FROM health_records WHERE date = ?", (data['date'],)
    ).fetchone()
    db.close()
    return success(dict(row), '创建成功'), 201

@api.route('/records/<int:rid>', methods=['PUT'])
def update_record(rid):
    data = request.get_json(silent=True)
    if not data:
        return error(400, '请求体为空')
    db = get_db()
    row = db.execute("SELECT * FROM health_records WHERE id = ?", (rid,)).fetchone()
    if row is None:
        db.close()
        return error(404, '记录不存在')

    allowed = {
        'steps', 'heart_rate', 'hr_min', 'hr_avg', 'hr_max',
        'sleep', 'water', 'exercise', 'mood', 'health_score', 'date'
    }
    updates = {k: v for k, v in data.items() if k in allowed}
    if not updates:
        db.close()
        return error(400, '没有可更新的字段')
    updates['updated_at'] = datetime.now().isoformat()

    cols = ', '.join(f"{k} = ?" for k in updates)
    db.execute(
        f"UPDATE health_records SET {cols} WHERE id = ?",
        list(updates.values()) + [rid]
    )
    db.commit()
    row = db.execute("SELECT * FROM health_records WHERE id = ?", (rid,)).fetchone()
    db.close()
    return success(dict(row), '更新成功')

@api.route('/records/<int:rid>', methods=['DELETE'])
def delete_record(rid):
    db = get_db()
    row = db.execute("SELECT * FROM health_records WHERE id = ?", (rid,)).fetchone()
    if row is None:
        db.close()
        return error(404, '记录不存在')
    db.execute("DELETE FROM health_records WHERE id = ?", (rid,))
    db.commit()
    db.close()
    return success(None, '删除成功')

# ──────────────────────────── Mock ────────────────────────────

@api.route('/mock/generate', methods=['POST'])
def generate_mock():
    data = request.get_json(silent=True) or {}
    days = min(int(data.get('days', 30)), 365)
    db = get_db()

    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    created = 0

    for i in range(days, 0, -1):
        d = today - timedelta(days=i)
        date_str = d.strftime('%Y-%m-%d')

        existing = db.execute(
            "SELECT id FROM health_records WHERE date = ?", (date_str,)
        ).fetchone()
        if existing:
            continue

        steps = random.randint(3000, 15000)
        hr_min = random.randint(55, 70)
        hr_avg = random.randint(hr_min, 85)
        hr_max = random.randint(hr_avg, 120)
        heart_rate = hr_avg
        sleep = round(random.uniform(5.0, 9.5), 1)
        water = random.randint(3, 10)
        exercise = random.randint(0, 90)
        mood = random.randint(40, 100)

        step_score = min(steps / 15000 * 100, 100)
        sleep_score = min(sleep / 9.5 * 100, 100)
        water_score = min(water / 10 * 100, 100)
        exercise_score = min(exercise / 90 * 100, 100)
        hr_norm = max(0, 1 - abs(hr_avg - 72) / 40)
        hr_score = hr_norm * 100
        health_score = int((step_score * 0.25 + sleep_score * 0.20 +
                            water_score * 0.10 + exercise_score * 0.25 +
                            mood * 0.10 + hr_score * 0.10))

        now = datetime.now().isoformat()
        db.execute("""
            INSERT INTO health_records
                (date, steps, heart_rate, hr_min, hr_avg, hr_max,
                 sleep, water, exercise, mood, health_score,
                 created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (date_str, steps, heart_rate, hr_min, hr_avg, hr_max,
              sleep, water, exercise, mood, health_score, now, now))
        created += 1

    db.commit()
    db.close()
    return success({'created': created, 'skipped': days - created},
                   f'生成了 {created} 条模拟数据，跳过 {days - created} 条已存在的记录')

# ──────────────────────────── AI ────────────────────────────

@api.route('/ai/query', methods=['POST'])
def ai_query():
    data = request.get_json(silent=True) or {}
    question = data.get('question', '').strip()
    if not question:
        return error(400, '问题不能为空')
    from ai_service import process_question
    result = process_question(question)
    return success(result)