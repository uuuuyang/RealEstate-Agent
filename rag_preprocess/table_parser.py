import pandas as pd
import datetime


def load_and_clean_table(path: str):
    df = pd.read_excel(path)

    # 1. 清洗面积 (移除逗号，转浮点)
    df["Adjusted Area (sqm)"] = (
        df["Adjusted Area (sqm)"]
        .astype(str)
        .str.replace(",", "")
        .str.strip()
        .astype(float)
    )

    # 2. 清洗租金 (确保是数字)
    # 假设 Excel 中可能有非数字字符，强制转为 numeric，错误的变为 NaN 后填充 0 或丢弃
    df["Dest_Effective Rent"] = pd.to_numeric(df["Dest_Effective Rent"], errors='coerce').fillna(0.0)

    # 3. 处理日期
    df["Trasaction Date"] = pd.to_datetime(df["Trasaction Date"])

    return df


def row_to_units(row):
    units = []

    # 提取基础计算数据 (Common Metadata)
    # 这些数据将被注入到该行生成的每一个 Unit 中，确保无论检索到哪个 Unit，都能获得计算能力
    transaction_date = row["Trasaction Date"]

    base_meta = {
        "source_type": "transaction_table",
        "is_computable": True,  # 标记：此 Unit 可用于计算

        # --- 时间维度 ---
        "year": int(transaction_date.year),
        "month": int(transaction_date.month),
        "date_str": transaction_date.strftime("%Y-%m-%d"),

        # --- 空间维度 ---
        "district": str(row.get("Dest_District_CN", "")),
        "submarket": str(row.get("Dest_Submarket_CN", "")),
        "building": str(row.get("Dest_Building Name Local_REIS", "")),
        "cbd_type": str(row.get("Dest_CBD/DBD", "")),

        # --- 数值维度 (核心) ---
        "rent": float(row["Dest_Effective Rent"]),  # 有效租金
        "area": float(row["Adjusted Area (sqm)"]),  # 面积 (可用于加权计算)

        # --- 业务维度 ---
        "sector": str(row.get("Primary Sector", "")),
        "tenant": str(row.get("Tenant", "")),
        "trans_type": str(row.get("Transaction Type", ""))
    }

    # Unit 1：基础交易事实 (侧重描述整体事件)
    # 文本保留用于语义检索 (Embedding)
    units.append({
        "type": "transaction_fact",
        "text": (
            f"{base_meta['year']}年{base_meta['month']}月，"
            f"客户{base_meta['tenant']}在{base_meta['district']}区{base_meta['submarket']}板块的"
            f"{base_meta['building']}达成交易。"
            f"成交面积{base_meta['area']}平方米，有效租金为{base_meta['rent']}元。"
            f"客户所属行业为{base_meta['sector']}。"
        ),
        "meta": base_meta.copy()  # 完整继承 meta
    })

    # Unit 2：租金价格锚点 (侧重价格查询)
    # 专门优化 prompt：当用户问“xx价格多少”时容易召回此条
    units.append({
        "type": "rent_price_point",
        "text": (
            f"{base_meta['year']}年，{base_meta['district']}{base_meta['submarket']}板块"
            f"录得一笔有效租金为 {base_meta['rent']} 的办公楼租赁成交。"
            f"该楼宇属于{base_meta['cbd_type']}性质。"
        ),
        "meta": base_meta.copy()
    })

    # Unit 3：行业选址偏好 (侧重行业分析)
    units.append({
        "type": "sector_behavior",
        "text": (
            f"{base_meta['sector']}行业在{base_meta['year']}年选择入驻"
            f"{base_meta['district']}区的{base_meta['submarket']}板块。"
            f"交易类型为{base_meta['trans_type']}。"
        ),
        "meta": base_meta.copy()
    })

    return units


def table_to_units(path: str):
    df = load_and_clean_table(path)
    all_units = []

    for _, row in df.iterrows():
        # 过滤掉租金或面积无效的数据，避免污染计算库
        if row["Dest_Effective Rent"] <= 0 or row["Adjusted Area (sqm)"] <= 0:
            continue

        all_units.extend(row_to_units(row))

    return all_units