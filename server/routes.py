import random
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from models import get_db
from auth import require_auth, success, error

api = Blueprint('api', __name__, url_prefix='/api')

def _calc_score(rec):
    steps = rec.get('steps') or 0
    hr_avg = rec.get('hr_avg') or rec.get('heart_rate') or 70
    sleep = rec.get('sleep') or 0
    water = rec.get('water') or 0
    exercise = rec.get('exercise') or 0
    mood = rec.get('mood') or 70
    step_score = min(steps / 10000 * 100, 100)
    hr_score = max(0, min(100, 100 - abs(hr_avg - 70) * 2.5))
    sleep_score = min(sleep / 8 * 100, 100)
    water_score = min(water / 8 * 100, 100)
    exercise_score = min(exercise / 60 * 100, 100)
    return int(step_score * 0.25 + hr_score * 0.20 + sleep_score * 0.20 +
               water_score * 0.10 + exercise_score * 0.15 + mood * 0.10)

# ──────────────────────────── CRUD ────────────────────────────

@api.route('/records', methods=['GET'])
@require_auth
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
@require_auth
def get_record(rid):
    db = get_db()
    row = db.execute("SELECT * FROM health_records WHERE id = ?", (rid,)).fetchone()
    db.close()
    if row is None:
        return error(404, '记录不存在')
    return success(dict(row))

@api.route('/records', methods=['POST'])
@require_auth
def create_record():
    data = request.get_json(silent=True)
    if not data or not data.get('date'):
        return error(400, '缺少必填字段 date')
    db = get_db()
    existing = db.execute(
        "SELECT id FROM health_records WHERE date = ?", (data['date'],)
    ).fetchone()
    if existing:
        # 已有记录 → 更新
        allowed = {
            'steps', 'heart_rate', 'hr_min', 'hr_avg', 'hr_max',
            'sleep', 'water', 'exercise', 'exercise_type', 'mood', 'health_score'
        }
        updates = {k: v for k, v in data.items() if k in allowed}
        if updates:
            updated_row = db.execute(
                "SELECT * FROM health_records WHERE id = ?", (existing['id'],)
            ).fetchone()
            merged = dict(updated_row)
            merged.update(updates)
            updates['health_score'] = _calc_score(merged)
            updates['updated_at'] = datetime.now().isoformat()
            cols = ', '.join(f"{k} = ?" for k in updates)
            db.execute(
                f"UPDATE health_records SET {cols} WHERE id = ?",
                list(updates.values()) + [existing['id']]
            )
            db.commit()
        row = db.execute(
            "SELECT * FROM health_records WHERE id = ?", (existing['id'],)
        ).fetchone()
        db.close()
        return success(dict(row), '更新成功')

    fields = [
        'date', 'steps', 'heart_rate', 'hr_min', 'hr_avg', 'hr_max',
        'sleep', 'water', 'exercise', 'exercise_type', 'mood', 'health_score'
    ]
    values = {k: data.get(k) for k in fields}
    values['health_score'] = _calc_score(values)
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
@require_auth
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
        'sleep', 'water', 'exercise', 'exercise_type', 'mood', 'health_score', 'date'
    }
    updates = {k: v for k, v in data.items() if k in allowed}
    if not updates:
        db.close()
        return error(400, '没有可更新的字段')
    merged = dict(row)
    merged.update(updates)
    updates['health_score'] = _calc_score(merged)
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
@require_auth
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
@require_auth
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
        exercise_type = random.choice(['跑步','骑行','瑜伽','游泳','力量训练','篮球','足球','羽毛球','乒乓球','跳绳','快走','散步']) if exercise > 0 else None
        mood = random.randint(40, 100)

        step_score = min(steps / 10000 * 100, 100)
        sleep_score = min(sleep / 8 * 100, 100)
        water_score = min(water / 8 * 100, 100)
        exercise_score = min(exercise / 60 * 100, 100)
        hr_score = max(0, min(100, 100 - abs(hr_avg - 70) * 2.5))
        health_score = int((step_score * 0.25 + hr_score * 0.20 +
                            sleep_score * 0.20 + water_score * 0.10 +
                            exercise_score * 0.15 + mood * 0.10))

        now = datetime.now().isoformat()
        db.execute("""
            INSERT INTO health_records
                (date, steps, heart_rate, hr_min, hr_avg, hr_max,
                 sleep, water, exercise, exercise_type, mood, health_score,
                 created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (date_str, steps, heart_rate, hr_min, hr_avg, hr_max,
              sleep, water, exercise, exercise_type, mood, health_score, now, now))
        created += 1

    db.commit()
    db.close()
    return success({'created': created, 'skipped': days - created},
                   f'生成了 {created} 条模拟数据，跳过 {days - created} 条已存在的记录')

# ──────────────────────────── AI ────────────────────────────


@api.route('/ai/insight', methods=['POST'])
@require_auth
def ai_insight():
    data = request.get_json(silent=True) or {}
    metrics = data.get('metrics', {})
    if not metrics:
        return error(400, '缺少健康数据')
    from llm_service import ask_llm
    prompt = (
        "你是一个专业的健康教练。请根据用户今天的健康数据，用2-3句话给出个性化的简短健康建议。"
        "风格：温暖鼓励、具体可操作、不超过80字。\n"
        "今日数据：步数" + str(metrics.get('steps',0)) + "步，睡眠" + str(metrics.get('sleep',0)) + "小时，"
        "心率" + str(metrics.get('heart',0)) + "bpm，饮水" + str(metrics.get('water',0)) + "杯，"
        "运动" + str(metrics.get('exercise',0)) + "分钟，健康评分" + str(metrics.get('score',0)) + "分。"
        "评分等级：" + str(metrics.get('level','')) + "。"
        "最佳指标：" + str(metrics.get('best','')) + "，最差指标：" + str(metrics.get('worst','')) + "。"
    )
    result = ask_llm(prompt)
    if result:
        return success({'insight': result.get('direct_answer', '') or result.get('answer_template', '')})
    return error(500, 'AI 服务暂时不可用')

@api.route('/ai/query', methods=['POST'])
def ai_query():
    data = request.get_json(silent=True) or {}
    question = data.get('question', '').strip()
    if not question:
        return error(400, '问题不能为空')
    messages = data.get('messages', [])
    from ai_service import process_question
    result = process_question(question, messages)
    return success(result)