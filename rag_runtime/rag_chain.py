# rag_runtime/rag_chain.py

from openai import OpenAI
import os
from typing import List, Dict
from tools import calc_yoy, calc_mean, filter_units
from query_parser import parse_query
from rag_retriever import RAGRetriever
from config import DEEPSEEK_API_KEY

client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")

def answer(query: str, retriever: RAGRetriever) -> str:
    # 1. 意图解析
    parsed = parse_query(query)
    intent = parsed["intent"]
    filters = parsed.get("filters", {})

    # 2. 检索（带过滤）
    units = retriever.retrieve(query, filter_dict=filters, k=20, rerank_top_n=5)

    # ==========================================================
    # 1. 同比 / 趋势问题 (YoY)
    # ==========================================================
    if intent == "yoy":
        print_step("Data Extraction", "Extracting [Year, Rent] from retrieved units...")

        values_by_year = {}
        for u in units:
            meta = u.get("meta", {})
            year = meta.get("year")
            rent = meta.get("rent")
            if year and rent is not None:
                year_int = int(year)
                values_by_year.setdefault(year_int, []).append(float(rent))

        if len(values_by_year) < 2:
            return "❌ 资料不足：有效年份少于2个，无法计算趋势。"

        year_avg_map = {}
        for year, rents in values_by_year.items():
            res = calc_mean(values=rents)
            if "mean" in res:
                year_avg_map[year] = res["mean"]

        sorted_years = sorted(year_avg_map.keys())
        # 根据filters中的year_range确定要对比的年份
        year_range = filters.get("year_range")
        if year_range and len(year_range) == 2:
            # 取范围内的最近两年
            years_in_range = [y for y in sorted_years if year_range[0] <= y <= year_range[1]]
            if len(years_in_range) >= 2:
                prev_year, curr_year = years_in_range[-2], years_in_range[-1]
            else:
                prev_year, curr_year = sorted_years[-2], sorted_years[-1]
        else:
            prev_year, curr_year = sorted_years[-2], sorted_years[-1]

        val_prev, val_curr = year_avg_map[prev_year], year_avg_map[curr_year]
        yoy_result = calc_yoy(values=[val_prev, val_curr])
        yoy_rate = yoy_result.get("yoy_rate", "未知")

        prompt = f"""
你是房地产研究分析师。
问题：{query}
【计算结果】（必须基于此回答）：
- {prev_year}年 平均租金：{val_prev}
- {curr_year}年 平均租金：{val_curr}
- 同比变化率：{yoy_rate}%
请输出：1. 直接回答具体的涨跌幅结论。 2. 简要描述趋势。
"""
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你只能基于给定的计算结果回答，禁止编造数字。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )
        return response.choices[0].message.content

    # ==========================================================
    # 2. 平均值问题 (Mean)
    # ==========================================================
    if intent == "mean":
        rents = []
        for u in units:
            r = u.get("meta", {}).get("rent")
            if r is not None:
                rents.append(float(r))

        if not rents:
            return "❌ 资料不足：没有找到有效的租金数值。"

        mean_result = calc_mean(values=rents)
        mean_value = mean_result.get("mean")
        count = mean_result.get("count")

        prompt = f"""
问题：{query}
【统计结果】：
- 样本数量：{count} 个案例
- 平均租金：{mean_value} 元/平方米/天
请基于以上数据回答问题。
"""
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你只能复述结论。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )
        return response.choices[0].message.content

    # ==========================================================
    # 3. 过滤查询 (Filter) 或 一般问答 (QA)
    # ==========================================================
    # 过滤查询：直接返回检索到的文本
    context_text = "\n\n".join([u["text"] for u in units])
    prompt = f"""
你是房地产研究分析师。
资料：
{context_text}
问题：{query}
"""
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1
    )
    return response.choices[0].message.content

def print_step(title, content):
    print(f"\n{'=' * 10} {title} {'=' * 10}")
    print(content)
    print(f"{'=' * 30}")