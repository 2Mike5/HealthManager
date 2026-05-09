"""
ai_service.py — Text-to-SQL 引擎
先用 LLM (DeepSeek) 生成 SQL，失败则回退规则引擎
"""

import re
from datetime import datetime, timedelta
from models import get_db

# ─── 指标映射 ───
METRICS = {
    '步数': 'steps', 'steps': 'steps', '走路': 'steps', '步行': 'steps',
    '心率': 'hr_avg', 'heart': 'hr_avg', '心跳': 'hr_avg',
    '最小心率': 'hr_min', '最大心率': 'hr_max', '平均心率': 'hr_avg',
    '睡眠': 'sleep', '睡觉': 'sleep', '休息': 'sleep',
    '饮水': 'water', '喝水': 'water', '水': 'water',
    '运动': 'exercise', '锻炼': 'exercise', '健身': 'exercise',
    '情绪': 'mood', '心情': 'mood',
    '健康评分': 'health_score', '评分': 'health_score', '健康分': 'health_score',
}
METRICS_CN = {
    'steps': '步数', 'hr_avg': '心率', 'hr_min': '最小心率',
    'hr_max': '最大心率', 'sleep': '睡眠', 'water': '饮水',
    'exercise': '运动', 'mood': '情绪', 'health_score': '健康评分',
}
UNIT_MAP = {
    'steps': '步', 'hr_avg': 'bpm', 'hr_min': 'bpm', 'hr_max': 'bpm',
    'sleep': '小时', 'water': '杯', 'exercise': '分钟', 'mood': '分',
    'health_score': '分',
}


def _parse_time_range(text):
    """规则引擎：解析时间范围"""
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_str = today.strftime('%Y-%m-%d')
    if re.search(r'今天|今日|当天', text):
        return (today_str, today_str, '今天')
    if re.search(r'昨天|昨日', text):
        d = (today - timedelta(days=1)).strftime('%Y-%m-%d')
        return (d, d, '昨天')
    week_start = today - timedelta(days=today.weekday())
    week_end = (week_start + timedelta(days=6)).strftime('%Y-%m-%d')
    ws = week_start.strftime('%Y-%m-%d')
    if re.search(r'这周|本周|这个星期', text):
        return (ws, week_end, '本周')
    if re.search(r'上周|上个星期', text):
        s = (week_start - timedelta(days=7)).strftime('%Y-%m-%d')
        e = (week_start - timedelta(days=1)).strftime('%Y-%m-%d')
        return (s, e, '上周')
    m = re.search(r'近(\d+)天?', text)
    if m:
        n = int(m.group(1))
        return ((today - timedelta(days=n - 1)).strftime('%Y-%m-%d'), today_str, f'近{n}天')
    this_start = today.replace(day=1).strftime('%Y-%m-%d')
    if re.search(r'这个月|本月', text):
        return (this_start, today_str, '本月')
    if re.search(r'上个月|上月', text):
        if today.month == 1:
            s = today.replace(year=today.year - 1, month=12, day=1)
        else:
            s = today.replace(month=today.month - 1, day=1)
        if today.month == 1:
            e = today.replace(year=today.year - 1, month=12, day=31)
        else:
            e = today.replace(day=1) - timedelta(days=1)
        return (s.strftime('%Y-%m-%d'), e.strftime('%Y-%m-%d'), '上月')
    start = (today - timedelta(days=6)).strftime('%Y-%m-%d')
    return (start, today_str, '近7天')


def _extract_metrics(text):
    found = []
    for kw, f in METRICS.items():
        if kw in text and f not in found:
            found.append(f)
    return found or ['steps']


def _needs_chart(text, fields, row_count):
    if row_count <= 1:
        return False
    if any(k in text for k in ['趋势', '变化', '走势', '对比', '比较', '分布', '曲线', '图']):
        return True
    return row_count >= 3


def _detect_chart_type(text, fields, rows):
    if any(k in text for k in ['趋势', '变化', '走势']):
        return 'line'
    if any(k in text for k in ['对比', '比较']):
        return 'column'
    if any(k in text for k in ['比例', '分布', '占比']):
        return 'ring'
    return 'column' if len(rows) <= 7 else 'line'


def _build_chart_config(chart_type, rows, fields, time_label, metric_label):
    rev = list(reversed(rows))
    if chart_type == 'ring':
        avg = round(sum(r[fields[0]] or 0 for r in rev) / len(rev), 1)
        return {
            'type': 'ring',
            'chartData': {'series': [{'name': metric_label, 'data': avg}]},
            'opts': {
                'legend': {'show': False}, 'title': {'show': False},
                'subtitle': {'show': False}, 'dataLabel': False,
                'extra': {'ring': {'ringWidth': 28, 'ringLabel': False,
                    'linearType': 'custom',
                    'color': [{'offset': 0, 'color': '#536DFE'}, {'offset': 1, 'color': '#7C4DFF'}]}},
                'background': 'transparent'
            }
        }
    dates = [r['date'][5:] for r in rev]
    vals = [r[fields[0]] or 0 for r in rev]
    base_opts = {
        'padding': [20, 15, 10, 35], 'legend': {'show': False},
        'dataLabel': False,
        'xAxis': {'labelCount': min(len(dates), 7), 'itemCount': len(dates),
                  'scrollShow': len(dates) > 10, 'scrollAlign': 'left'},
        'yAxis': {'data': [{'min': 0}]}, 'color': ['#667eea'],
        'background': 'transparent',
        'extra': {'tooltip': {'showBox': True, 'showLabel': True}}
    }
    if chart_type == 'line':
        base_opts['extra']['line'] = {'type': 'curve', 'width': 3, 'areaStyle': {'opacity': 0.1}}
    else:
        base_opts['extra']['column'] = {'type': 'group', 'width': max(10, min(30, 300 // len(dates)))}
    return {'type': chart_type, 'chartData': {'categories': dates, 'series': [{'name': metric_label, 'data': vals}]}, 'opts': base_opts}


def _generate_answer_text(rows, fields, time_label, metric_label, sql_text):
    if not rows:
        return f'{time_label}暂无数据'
    f = fields[0]
    unit = UNIT_MAP.get(f, '')
    if len(rows) == 1:
        return f'{time_label}{metric_label}：**{rows[0][f]}** {unit}'
    vals = [r[f] or 0 for r in rows]
    avg = round(sum(vals) / len(vals), 1)
    mx = max(vals)
    mn = min(vals)
    dates = [r['date'] for r in rows]
    extra = ''
    if f == 'steps':
        extra = f'\n- 达标（>=8000步）：{sum(1 for v in vals if v >= 8000)}天\n- 不足（<5000步）：{sum(1 for v in vals if v < 5000)}天'
    elif f == 'sleep':
        extra = f'\n- 充足（>=7h）：{sum(1 for v in vals if v >= 7)}天\n- 不足（<6h）：{sum(1 for v in vals if v < 6)}天'
    elif f == 'hr_avg':
        extra = f'\n- 正常范围（60-80bpm）：{sum(1 for v in vals if 60 <= v <= 80)}天'
    elif f == 'health_score':
        extra = f'\n- 优秀（>=80分）：{sum(1 for v in vals if v >= 80)}天'
    return (f'{time_label}{metric_label}趋势分析：\n- 平均：**{avg}** {unit}\n- 最高：**{mx}** {unit}（{dates[vals.index(mx)]}）\n- 最低：**{mn}** {unit}（{dates[vals.index(mn)]}）{extra}')


# ─── 主入口 ───

def process_question(question):
    """先尝试 LLM，失败则回退规则引擎"""
    text = question.strip()
    from llm_service import ask_llm

    llm_result = ask_llm(text)
    use_llm = llm_result is not None

    if use_llm:
        # 非数据查询（闲聊），直接返回 LLM 的回答
        direct_answer = llm_result.get('direct_answer', '')
        if direct_answer:
            return {'type': 'text', 'answer': direct_answer, 'sql': None, 'chart_config': None}

        sql = llm_result.get('sql')
        # LLM 给了空 sql，说明不是数据查询
        if not sql or not sql.strip():
            return {'type': 'text', 'answer': '请问你想查询什么健康数据？例如：今天步数、近7天心率趋势', 'sql': None, 'chart_config': None}

        should_chart = llm_result.get('needs_chart', False)
        chart_type = llm_result.get('chart_type')
        answer_template = llm_result.get('answer_template', '')
    else:
        start, end, time_label = _parse_time_range(text)
        fields = _extract_metrics(text)
        f = fields[0]
        sql = f"SELECT date, {f} FROM health_records WHERE date = '{start}'" if time_label in ('今天', '昨天') else f"SELECT date, {f} FROM health_records WHERE date BETWEEN '{start}' AND '{end}' ORDER BY date ASC"
        should_chart = False
        chart_type = None
        answer_template = ''

    try:
        db = get_db()
        rows = [dict(r) for r in db.execute(sql).fetchall()]
        db.close()
    except Exception as e:
        return {'type': 'error', 'answer': f'SQL 执行出错：{e}\n\nSQL：{sql}', 'chart_config': None, 'sql': sql}

    if use_llm:
        if rows and answer_template:
            if len(rows) == 1:
                r = rows[0]
                val = next((r[k] for k in r if k != 'date' and r[k] is not None), '')
                answer = answer_template.replace('{value}', str(val)).replace('{{value}}', str(val)).replace('{{值}}', str(val))
            else:
                first_field = next((k for k in rows[0] if k != 'date' and rows[0][k] is not None), 'steps')
                vals = [r[first_field] or 0 for r in rows]
                avg_val = round(sum(vals) / len(vals), 1)
                answer = answer_template.replace('{value}', str(avg_val)).replace('{{value}}', str(avg_val)).replace('{{值}}', str(avg_val))
        else:
            answer = f'查询到 {len(rows)} 条记录'
    else:
        fields = _extract_metrics(text)
        field = fields[0]
        start, end, time_label = _parse_time_range(text)
        metric_label = METRICS_CN.get(field, field)
        should_chart = _needs_chart(text, fields, len(rows))
        chart_type = _detect_chart_type(text, fields, rows) if should_chart else None
        answer = _generate_answer_text(rows, fields, time_label, metric_label, sql)

    result = {'type': 'chart' if should_chart and len(rows) >= 2 else 'text', 'answer': answer, 'sql': sql, 'chart_config': None}

    if should_chart and len(rows) >= 2:
        if use_llm:
            first_field = next((k for k in rows[0] if k != 'date' and rows[0][k] is not None), 'steps')
            metric_label = METRICS_CN.get(first_field, first_field)
            _, _, time_label = _parse_time_range(text)
            result['chart_config'] = _build_chart_config(chart_type or 'line', rows, [first_field], time_label, metric_label)
        else:
            fields = _extract_metrics(text)
            field = fields[0]
            metric_label = METRICS_CN.get(field, field)
            _, _, time_label = _parse_time_range(text)
            result['chart_config'] = _build_chart_config(chart_type, rows, fields, time_label, metric_label)

    return result
