def blocks_to_units(blocks):
    units = []

    for block in blocks:
        text = block["content"]

        # 简单的预处理：如果文本太短（例如只有页码），可以跳过
        if len(text) < 10:
            continue

        units.append({
            "type": "text_unit",  # 纯文本单元
            "text": text,
            "meta": {
                "source": "docx",
                "source_type": "market_report",
                "is_computable": False,  # 明确标记不可直接计算
                # 这里未来可以扩展：通过 LLM 提取文档中的年份、区域并填入
                "year": None,
                "district": None
            }
        })

    return units