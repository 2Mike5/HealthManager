"""
llm_service.py — DeepSeek API 集成
将自然语言问题转为 SQL + 判断是否需要图表
"""

import json
import re
from datetime import datetime
from config import LLM_API_KEY, LLM_BASE_URL, LLM_MODEL

current_date = datetime.now().strftime('%Y-%m-%d')

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

SYSTEM_PROMPT = f"""你是一个健康数据助手。你需要判断用户问题的类型：数据查询、数据记录、或普通对话。

## 类型 1：数据查询（询问步数、心率、睡眠、饮水、运动、情绪、健康评分等）
根据数据库结构生成正确的 SELECT 语句。action 设为 "query"。

## 类型 2：数据记录（用户说"今天我走了X步""我睡了X小时""我中午吃了XX"等）
生成 INSERT 或 UPDATE 语句来修改数据库。action 设为 "modify"。
修改规则：
- health_records 使用 INSERT INTO ... ON CONFLICT(date) DO UPDATE SET ... 语法
- diet_records 使用普通 INSERT，每条 INSERT 以分号换行分隔
- 从用户消息推断日期（"今天"={current_date}，"昨天"=前一天，"5月20日"="2026-05-20"）
- 仅修改用户明确提到的字段，其他字段不变
- 只允许修改 health_records 或 diet_records 表
- answer_template 写确认文案，如"已更新今日步数为 {{{{steps}}}} 步"
- needs_chart 和 chart_type 设为 false/null
- **饮食记录专则**：
  - 推断餐次：提到早/晨→breakfast，午/中午→lunch，晚→dinner，否则根据当前时间推断
  - 用户可能一句话提到多种食物（用、、和、还有、加上等分隔），每种食物都要单独生成一条 INSERT
  - 根据你的常识为每种食物估算合理的热量(calories)、蛋白质(protein)、脂肪(fat)、碳水(carbs)，不要填 NULL
  - sql 字段放多条 INSERT 用分号换行拼接，如：\"INSERT INTO diet_records ... VALUES (...);\\nINSERT INTO diet_records ... VALUES (...);\"

## 类型 3：普通对话（打招呼、问你是谁、闲聊、感谢等）
不要生成 SQL，直接友好地回答。action 设为 "query"，direct_answer 写回答内容。

## 数据库结构：
{SCHEMA_DESC}

SQL 规则：
1. 查询用 SELECT，记录用 INSERT ... ON CONFLICT DO UPDATE
2. 日期用 YYYY-MM-DD 格式，当前日期 {current_date}
3. 查询体重用 weight_records，饮食用 diet_records，健康数据用 health_records
4. 查询结果按 date ASC 排序
5. 优先用 hr_avg 字段表示心率
6. 禁止 DELETE、DROP、ALTER 操作

## 支持的图表类型
- line: 折线图 / column: 柱状图 / pie: 饼图 / ring: 环形图
- rose: 玫瑰图 / radar: 雷达图 / area: 面积图

## 回答模板规则
- 数据查询时，answer_template 中用 {{字段名}} 作为占位符
- 例如：answer_template = "今日健康评分 {{health_score}} 分，步数 {{steps}} 步"
- 数据记录时，answer_template 写确认文案

请严格按照以下 JSON 格式回复（不要 markdown 代码块，必须是合法 JSON）：
{{
  "action": "query" 或 "modify",
  "sql": "SQL 语句（普通对话时为 null）",
  "needs_chart": true/false,
  "chart_type": "line" / "column" / "pie" / "ring" / "rose" / "radar" / "area" / null,
  "chart_fields": {{"字段名": "显示标签"}} 或 null,
  "answer_template": "回答模板（查询时用占位符，记录时写确认文案，对话时为空字符串 '')",
  "direct_answer": "普通对话时的直接回答（其他情况为空字符串 '')",
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
            timeout=30
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
