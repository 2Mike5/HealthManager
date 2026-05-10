"""
ai_service.py — Text-to-SQL 引擎
先用 LLM 生成 SQL，失败则回退规则引擎
支持 chart_types: line, column, pie, ring, rose, radar, area
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
    '运动类型': 'exercise_type', '运动项目': 'exercise_type',
    '情绪': 'mood', '心情': 'mood',
    '健康评分': 'health_score', '评分': 'health_score', '健康分': 'health_score',
}
METRICS_CN = {
    'steps': '步数', 'hr_avg': '心率', 'hr_min': '最小心率',
    'hr_max': '最大心率', 'sleep': '睡眠', 'water': '饮水',
    'exercise': '运动', 'exercise_type': '运动类型', 'mood': '情绪',
    'health_score': '健康评分',
}
UNIT_MAP = {
    'steps': '步', 'hr_avg': 'bpm', 'hr_min': 'bpm', 'hr_max': 'bpm',
    'sleep': '小时', 'water': '杯', 'exercise': '分钟', 'exercise_type': '',
    'mood': '分', 'health_score': '分',
}

# ─── uCharts 色板（按顺序取色） ───
COLORS = ['#667eea', '#4CAF50', '#FF6B6B', '#45B7D1', '#FFA94D',
          '#F783AC', '#7C4DFF', '#26A69A', '#EF5350', '#42A5F5']


def _fill_template(template, row):
    """将模板中的 {field_name} 替换为 row 中的实际值"""
    if not template or not row:
        return template or ''
    result = template
    for k, v in row.items():
        placeholder = '{' + k + '}'
        if placeholder in result:
            result = result.replace(placeholder, str(v or ''))
    # 也替换 {{value}} 等旧格式
    first_val = next((str(v) for v in row.values() if v is not None), '')
    result = result.replace('{value}', first_val).replace('{{value}}', first_val)
    return result


def _build_chart_config(chart_type, rows, fields=None, time_label='', metric_label='',
                        chart_labels=None):
    """
    通用图表配置生成器
    支持: line, column, pie, ring, rose, radar, area
    fields: 要展示的字段列表（多字段时 = 多个 series）
    chart_labels: {字段名: 显示标签} 映射（来自 LLM）
    """
    rev = list(reversed(rows)) if rows else []
    if not rev:
        return None

    # 确定字段和标签
    if fields is None:
        fields = [k for k in rev[0] if k not in ('date', 'id', 'created_at', 'updated_at')]
    labels_map = chart_labels or {}
    field_labels = [labels_map.get(f, METRICS_CN.get(f, f)) for f in fields]

    # ── 饼/环/玫瑰图（多字段、单行） ──
    if chart_type in ('pie', 'ring', 'rose'):
        if len(rev) == 1:
            # 单行多字段 → 每个字段一个扇区
            row = rev[0]
            series = []
            for i, f in enumerate(fields):
                val = row.get(f) or 0
                if val:
                    series.append({
                        'name': field_labels[i],
                        'data': round(val, 1)
                    })
            if not series:
                return None
            chart_data = {'series': series}
        else:
            # 多行单字段 → 每行一个扇区
            series = [{'name': r.get('date', str(i)), 'data': round(r.get(fields[0]) or 0, 1)}
                      for i, r in enumerate(rev)]
            chart_data = {'series': series}

        opts = {
            'legend': {'position': 'bottom', 'show': len(series) > 1},
            'dataLabel': True,
            'title': {'show': False},
            'background': 'transparent',
            'color': COLORS[:len(series)]
        }
        if chart_type == 'ring':
            opts['extra'] = {'ring': {'ringWidth': 24}}
        elif chart_type == 'rose':
            opts['extra'] = {'rose': {'type': 'area', 'maxRadius': '90%'}}

        return {'type': chart_type, 'chartData': chart_data, 'opts': opts}

    # ── 雷达图（多字段、单行） ──
    if chart_type == 'radar':
        row = rev[0] if len(rev) == 1 else rev[-1]
        categories = field_labels
        data = [round(row.get(f) or 0, 1) for f in fields]
        chart_data = {'categories': categories, 'series': [{'name': metric_label or '健康指标', 'data': data}]}
        opts = {
            'legend': {'show': False},
            'dataLabel': True,
            'background': 'transparent',
            'color': ['#667eea'],
            'extra': {
                'radar': {
                    'max': 100,
                    'labelColor': '#666',
                    'gridColor': '#eee',
                    'axisLabel': True
                }
            }
        }
        return {'type': 'radar', 'chartData': chart_data, 'opts': opts}

    # ── 折线图 / 柱状图 / 面积图（多行、时间序列） ──
    has_multiple_fields = len(fields) > 1 or (len(fields) == 1 and fields[0] != 'steps')
    if has_multiple_fields and len(rev) == 1:
        row = rev[0]
        categories = field_labels
        series = [{'name': time_label or '今日', 'data': [round(row.get(f) or 0, 1) for f in fields]}]
    else:
        categories = [r.get('date', '')[-5:] for r in rev]
        series = []
        for i, f in enumerate(fields):
            vals = [round(r.get(f) or 0, 1) for r in rev]
            series.append({'name': field_labels[i], 'data': vals})

    base_opts = {
        'padding': [20, 15, 10, 35],
        'legend': {'show': len(series) > 1},
        'dataLabel': False,
        'background': 'transparent',
        'color': COLORS[:len(series)],
        'xAxis': {
            'labelCount': min(len(categories), 7),
            'itemCount': len(categories),
            'scrollShow': len(categories) > 10,
            'scrollAlign': 'left'
        },
        'yAxis': {'data': [{'min': 0}]},
        'extra': {'tooltip': {'showBox': True, 'showLabel': True}}
    }
    if chart_type == 'area':
        base_opts['extra']['area'] = {'type': 'curve', 'width': 2, 'opacity': 0.2}
        base_opts['extra']['line'] = {'type': 'curve', 'width': 2}
    elif chart_type == 'line':
        base_opts['extra']['line'] = {'type': 'curve', 'width': 3, 'areaStyle': {'opacity': 0.1}}
    else:
        bar_width = max(8, min(30, 200 // len(categories)))
        base_opts['extra']['column'] = {'type': 'group', 'width': bar_width}

    return {
        'type': chart_type,
        'chartData': {'categories': categories, 'series': series},
        'opts': base_opts
    }


def process_question(question, messages=None):
    """先尝试 LLM，失败则回退规则引擎
    messages: 可选的多轮对话历史 [{'role': 'user'|'ai', 'content': str}, ...]
    """
    text = question.strip()
    from llm_service import ask_llm

    llm_result = ask_llm(text, messages)
    use_llm = llm_result is not None

    if use_llm:
        direct_answer = llm_result.get('direct_answer', '')
        if direct_answer:
            return {'type': 'text', 'answer': direct_answer, 'sql': None, 'chart_config': None}

        sql = llm_result.get('sql')
        if not sql or not sql.strip():
            return {'type': 'text', 'answer': '请问你想查询什么健康数据？例如：今天步数、近7天心率趋势', 'sql': None, 'chart_config': None}

        should_chart = llm_result.get('needs_chart', False)
        chart_type = llm_result.get('chart_type')
        chart_fields = llm_result.get('chart_fields')  # {field: label}
        answer_template = llm_result.get('answer_template', '')
    else:
        start, end, time_label = _parse_time_range(text)
        fields = _extract_metrics(text)
        f = fields[0]
        sql = (f"SELECT date, {f} FROM health_records WHERE date = '{start}'"
               if time_label in ('今天', '昨天')
               else f"SELECT date, {f} FROM health_records WHERE date BETWEEN '{start}' AND '{end}' ORDER BY date ASC")
        should_chart = False
        chart_type = None
        chart_fields = None
        answer_template = ''

    try:
        db = get_db()
        rows = [dict(r) for r in db.execute(sql).fetchall()]
        db.close()
    except Exception as e:
        return {'type': 'error', 'answer': f'SQL 执行出错：{e}\n\nSQL：{sql}', 'chart_config': None, 'sql': sql}

    if use_llm:
        # LLM 路径：模板变量替换
        if rows and answer_template:
            if len(rows) == 1:
                answer = _fill_template(answer_template, rows[0])
            else:
                first_field = next((k for k in rows[0] if k != 'date' and rows[0][k] is not None), 'steps')
                vals = [r[first_field] or 0 for r in rows]
                avg_val = round(sum(vals) / len(vals), 1)
                answer = answer_template.replace('{value}', str(avg_val)).replace('{{value}}', str(avg_val))
                # Also fill per-row templates for multi-row
                if len(rows) <= 14:
                    lines = []
                    for r in rows:
                        line = _fill_template(answer_template, r)
                        if line != answer_template:
                            lines.append(line)
                    if lines:
                        answer = '\n'.join(lines)
        else:
            answer = f'查询到 {len(rows)} 条记录'
    else:
        # 规则引擎路径
        fields = _extract_metrics(text)
        field = fields[0]
        start, end, time_label = _parse_time_range(text)
        metric_label = METRICS_CN.get(field, field)
        should_chart = _needs_chart(text, fields, len(rows))
        chart_type = _detect_chart_type(text, fields, rows) if should_chart else None
        answer = _generate_answer_text(rows, fields, time_label, metric_label, sql)

    result = {'type': 'text', 'answer': answer, 'sql': sql, 'chart_config': None}

    # ── 构建图表 ──
    if rows and len(rows) >= 1:
        should_make_chart = should_chart and len(rows) >= 2
        if use_llm and chart_type:
            should_make_chart = True

        if should_make_chart or (chart_type and chart_type in ('pie', 'ring', 'rose', 'radar')):
            if use_llm:
                fields_to_use = list(chart_fields.keys()) if chart_fields else None
                labels = chart_fields or {}
                _, _, time_label = _parse_time_range(text)
                result['chart_config'] = _build_chart_config(
                    chart_type, rows, fields=fields_to_use,
                    time_label=time_label, chart_labels=labels
                )
                result['type'] = 'chart'
            else:
                field = _extract_metrics(text)[0]
                metric_label = METRICS_CN.get(field, field)
                _, _, time_label = _parse_time_range(text)
                result['chart_config'] = _build_chart_config(
                    chart_type, rows, fields=[field],
                    time_label=time_label, chart_labels={field: metric_label}
                )
                result['type'] = 'chart'

    return result


# ─── 规则引擎辅助函数（兼容旧版） ───

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
        return '趋势' in text or '走势' in text or '图' in text
    if any(k in text for k in ['趋势', '变化', '走势', '对比', '比较', '分布', '曲线']):
        return True
    return row_count >= 3


def _detect_chart_type(text, fields, rows):
    if any(k in text for k in ['趋势', '变化', '走势']):
        return 'line'
    if any(k in text for k in ['对比', '比较']):
        return 'column'
    if any(k in text for k in ['比例', '分布', '占比', '构成', '组成']):
        return 'pie'
    return 'column' if len(rows) <= 7 else 'line'


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
