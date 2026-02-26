# rag_runtime/query_parser.py

import json
from openai import OpenAI
from config import DEEPSEEK_API_KEY, INTENT_MODEL

client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")

SYSTEM_PROMPT = """
你是一个商业地产查询解析器。将用户的问题解析为结构化JSON，包含：
- intent: 用户意图，可选值为["yoy", "mean", "filter", "qa"]。
    - yoy: 同比变化（通常涉及两年数据比较）
    - mean: 计算平均值
    - filter: 仅筛选数据，不需要计算（如“静安区2024年的租金数据”）
    - qa: 一般性问答（不需要计算和筛选）
- filters: 过滤条件，包含以下可选字段：
    - district: 区域（如“静安区”）
    - submarket: 子市场（如“南京西路”）
    - year: 年份（整数）
    - year_range: 年份范围（[start, end]）
    - sector: 行业（如“金融业”）
    - min_rent / max_rent: 租金范围（数字）
    - min_area / max_area: 面积范围（数字）
    - cbd_type: "CBD"或"Decentralised"
请确保字段名与示例一致，若无对应条件则省略。
示例：
输入：2023-2024年静安区写字楼租金同比变化？
输出：{"intent": "yoy", "filters": {"district": "静安区", "year_range": [2023, 2024]}}
输入：陆家嘴2024年金融行业的平均租金
输出：{"intent": "mean", "filters": {"submarket": "陆家嘴", "year": 2024, "sector": "Financial Services"}}
输入：给我看一些前滩的交易案例
输出：{"intent": "filter", "filters": {"submarket": "前滩"}}
输入：上海办公楼市场最近有什么趋势？
输出：{"intent": "qa", "filters": {}}
"""

def parse_query(query: str) -> dict:
    """调用LLM解析查询，返回结构化字典"""
    response = client.chat.completions.create(
        model=INTENT_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": query}
        ],
        temperature=0,
        response_format={"type": "json_object"}  # 确保返回JSON
    )
    content = response.choices[0].message.content
    try:
        result = json.loads(content)
    except json.JSONDecodeError:
        # 降级处理：返回一般问答
        result = {"intent": "qa", "filters": {}}
    return result