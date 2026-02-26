import statistics


def calc_mean(values, **kwargs):
    # **kwargs 用于接收并忽略 LLM 可能幻觉生成的额外参数（如 unit, currency 等）
    if not values:
        return {"error": "no data provided"}
    return {
        "mean": round(statistics.mean(values), 2),
        "count": len(values)
    }


def calc_yoy(values, **kwargs):
    # 修改点：增加 **kwargs 接收 base 参数但不报错
    # 逻辑：默认取列表最后两个值进行计算
    if len(values) < 2:
        return {"error": "not enough data (need at least 2 years)"}

    # 假设 values 是按年份排序的（比如 [2023值, 2024值]）
    prev, curr = values[-2], values[-1]

    if prev == 0:
        return {"error": "previous value is 0, cannot calc yoy"}

    rate = (curr - prev) / prev
    return {
        "yoy_rate": round(rate * 100, 2),
        "values_used": [prev, curr]  # 为了调试，返回实际用到的值
    }


def compare_mean(group_a, group_b, **kwargs):
    if not group_a or not group_b:
        return {"error": "missing data for comparison"}

    mean_a = statistics.mean(group_a)
    mean_b = statistics.mean(group_b)
    return {
        "mean_a": round(mean_a, 2),
        "mean_b": round(mean_b, 2),
        "diff": round(mean_a - mean_b, 2),
        "higher": "A" if mean_a > mean_b else "B"
    }


def filter_units(units, district=None, year=None, **kwargs):
    # 这里的 kwargs 可以吞掉 LLM 传进来的无关过滤条件
    result = []
    for u in units:
        meta = u.get("meta", {})

        # 严格的数据类型转换，防止 meta 里是字符串 '2023' 而参数是整数 2023
        u_year = int(meta.get("year")) if meta.get("year") is not None else None
        q_year = int(year) if year is not None else None

        if district and meta.get("district") != district:
            continue
        if q_year and u_year != q_year:
            continue
        result.append(u)
    return result