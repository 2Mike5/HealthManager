"""
llm_service.py — DeepSeek API 集成
将自然语言问题转为 SQL + 判断是否需要图表
"""

import json
import re
from openai import OpenAI
from config import LLM_API_KEY, LLM_BASE_URL, LLM_MODEL

# ─── 数据库 Schema 描述 ───

SCHEMA_DESC = """
数据库表 health_records 结构：

date         TEXT   日期 (YYYY-MM-DD)
steps        INTEGER   步数
heart_rate   INTEGER   平均心率 (兼容旧字段)
hr_min       INTEGER   最小心率
hr_avg       INTEGER   平均心率
hr_max       INTEGER   最大心率
sleep        REAL      睡眠时长(小时)
water        INTEGER   饮水量(杯)
exercise     INTEGER   运动时长(分钟)
mood         INTEGER   情绪评分(0-100)
health_score INTEGER   健康评分(0-100)

示例数据：
('2026-05-09', 8520, 72, 62, 72, 95, 7.5, 6, 30, 80, 75)
('2026-05-08', 12000, 75, 65, 75, 110, 8.0, 8, 45, 85, 88)
"""

SYSTEM_PROMPT = f"""你是一个健康数据查询助手。你需要判断用户的问题是健康数据查询还是普通对话。

## 如果是健康数据查询（询问步数、心率、睡眠、饮水、运动、情绪、健康评分等）：
根据数据库结构生成正确的 SQL 语句。

## 如果是普通对话（打招呼、问你是谁、闲聊、感谢等）：
不要生成 SQL，直接友好地回答。

## 数据库结构：
{SCHEMA_DESC}

SQL 规则：
1. 只做 SELECT 查询，不修改数据
2. 日期用 YYYY-MM-DD 格式，当前日期 2026-05-09
3. SQLite 语法（不支持 DATEADD/DATEDIFF，用 date() 函数）
4. 结果按 date ASC 排序
5. 优先用 hr_avg 字段表示心率

图表规则：
- 趋势/变化/走势 → needs_chart = true, chart_type = line
- 对比/比较 → needs_chart = true, chart_type = column
- 占比/分布 → needs_chart = true, chart_type = ring
- 单一数值 → needs_chart = false, chart_type = null

请严格按照以下 JSON 格式回复（不要 markdown 代码块标记）：
{{
  "sql": "SQL 语句（普通对话时为 null）",
  "needs_chart": true/false,
  "chart_type": "line" / "column" / "ring" / null,
  "answer_template": "回答模板，用 {{value}} 占位（普通对话时为 ''）",
  "direct_answer": "普通对话时的直接回答（数据查询时为空字符串 '')",
  "reasoning": "简要说明思路"
}}"""


def _parse_llm_response(text):
    """从 LLM 回复中提取 JSON"""
    # 尝试直接解析
    text = text.strip()
    if text.startswith('```'):
        text = re.sub(r'```(?:json)?\s*', '', text)
        text = text.rstrip('`').strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    # 尝试从中提取 {...}
    m = re.search(r'\{[^{}]*\}', text, re.DOTALL)
    if m:
        try:
            return json.loads(m.group())
        except json.JSONDecodeError:
            pass
    raise ValueError(f"无法解析 LLM 响应: {text[:200]}")


def ask_llm(question):
    """
    调用 DeepSeek API，将问题转为 SQL
    返回: { sql, needs_chart, chart_type, answer_template, reasoning }
    失败时返回 None
    """
    if not LLM_API_KEY or '你的' in LLM_API_KEY:
        return None

    try:
        client = OpenAI(
            api_key=LLM_API_KEY,
            base_url=LLM_BASE_URL,
            timeout=8
        )

        resp = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {'role': 'system', 'content': SYSTEM_PROMPT},
                {'role': 'user', 'content': question}
            ],
            temperature=0.1,
            max_tokens=1000
        )

        content = resp.choices[0].message.content
        return _parse_llm_response(content)

    except Exception as e:
        print(f'[LLM] API 调用失败: {e}')
        return None
