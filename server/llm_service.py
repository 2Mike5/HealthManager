"""
llm_service.py — DeepSeek API 集成
将自然语言问题转为 SQL + 判断是否需要图表
"""

import json
import re
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
exercise_type TEXT    运动类型(跑步/骑行/瑜伽/游泳/力量训练/篮球/其他)
mood         INTEGER   情绪评分(0-100)
health_score INTEGER   健康评分(0-100)

另有 weight_records 表：
date         TEXT   日期
weight       REAL   体重(kg)
body_fat     REAL   体脂率(%)

另有 diet_records 表：
date         TEXT   日期
meal_type    TEXT   餐次(breakfast/lunch/dinner/snack)
food_name    TEXT   食物名称
calories     REAL   热量(kcal)
protein      REAL   蛋白质(g)
fat          REAL   脂肪(g)
carbs        REAL   碳水化合物(g)

示例数据(health_records)：
('2026-05-10', 8520, 72, 62, 72, 95, 7.5, 6, 30, '跑步', 80, 75)
('2026-05-09', 12000, 75, 65, 75, 110, 8.0, 8, 45, '骑行', 85, 88)
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
2. 日期用 YYYY-MM-DD 格式，当前日期 2026-05-10
3. 查询体重相关时用 weight_records 表，查询饮食相关时用 diet_records 表（支持按 meal_type 分组）
4. 结果按 date ASC 排序
5. 优先用 hr_avg 字段表示心率

## 支持的图表类型
- line: 折线图（趋势/变化/走势）
- column: 柱状图（对比/比较）
- pie: 饼图（比例/分布/构成）
- ring: 环形图（比例/分布）
- rose: 玫瑰图（分布/对比多分类）
- radar: 雷达图（综合评分多维度展示）
- area: 面积图（趋势+量感）

## 回答模板规则
- 数据查询时，answer_template 中可以用 {{字段名}} 作为占位符，系统会自动替换为查询结果中的值
- 例如：answer_template = "今日健康评分 {{health_score}} 分，步数 {{steps}} 步"
- 查询多个字段时，SQL 中 SELECT 这些字段，在 chart_fields 中指定每个字段的显示名称

## chart_fields 说明（用于多字段图表）
- chart_fields 是一个对象，key=数据库字段名，value=显示标签
- 雷达图示例：SELECT steps, sleep, water FROM ... → chart_fields = {{"steps": "步数", "sleep": "睡眠", "water": "饮水"}}
- 饼图/玫瑰图：多行单字段时 chart_fields 为 null（自动用日期做标签）

请严格按照以下 JSON 格式回复（不要 markdown 代码块标记，必须是一个合法的 JSON 对象）：
{{
  "sql": "SQL 查询语句（普通对话时为 null）",
  "needs_chart": true/false,
  "chart_type": "line" / "column" / "pie" / "ring" / "rose" / "radar" / "area" / null,
  "chart_fields": {{"字段名": "显示标签"}} 或 null,
  "answer_template": "回答模板，用 {{字段名}} 作为占位符（数据查询时使用，普通对话时为 '')",
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


def ask_llm(question, messages=None):
    """
    调用 DeepSeek API，将问题转为 SQL
    支持多轮对话: messages = [{'role': 'user'|'ai', 'content': '...'}, ...]
    返回: { sql, needs_chart, chart_type, answer_template, reasoning }
    失败时返回 None
    """
    if not LLM_API_KEY or 'your' in LLM_API_KEY.lower() or '你的' in LLM_API_KEY:
        return None

    try:
        from openai import OpenAI
        client = OpenAI(
            api_key=LLM_API_KEY,
            base_url=LLM_BASE_URL,
            timeout=8
        )

        # 构建多轮对话消息
        chat_messages = [{'role': 'system', 'content': SYSTEM_PROMPT}]
        if messages:
            for m in messages[-10:]:
                role = 'assistant' if m.get('role') == 'ai' else 'user'
                content = m.get('content', '')
                if content:
                    # 聊天内容太长会影响 LLM，截断到 500 字
                    chat_messages.append({'role': role, 'content': content[:500]})
        chat_messages.append({'role': 'user', 'content': question})

        resp = client.chat.completions.create(
            model=LLM_MODEL,
            messages=chat_messages,
            temperature=0.1,
            max_tokens=1000
        )

        content = resp.choices[0].message.content
        return _parse_llm_response(content)

    except Exception as e:
        print(f'[LLM] API 调用失败: {e}')
        return None
