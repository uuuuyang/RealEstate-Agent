# rag_preprocess/chunking/table_processor.py

import pandas as pd
from typing import List, Dict

def table_to_text(df: pd.DataFrame, caption: str = "") -> str:
    """将DataFrame转换为自然语言描述"""
    if df.empty:
        return caption
    # 简单描述：列名和每行内容
    lines = [caption] if caption else []
    headers = list(df.columns)
    for _, row in df.iterrows():
        row_desc = "，".join([f"{col}:{row[col]}" for col in headers if pd.notna(row[col])])
        lines.append(row_desc)
    return "\n".join(lines)

def process_table_file(filepath: str, metadata: Dict) -> List[Dict]:
    """处理Excel表格，每张sheet作为独立单元，并生成文本描述"""
    units = []
    xls = pd.ExcelFile(filepath)
    for sheet_name in xls.sheet_names:
        df = pd.read_excel(xls, sheet_name=sheet_name)
        if df.empty:
            continue
        # 将表格转为文本
        text = table_to_text(df, caption=f"表格：{sheet_name}")
        unit_meta = metadata.copy()
        unit_meta['source'] = filepath
        unit_meta['sheet'] = sheet_name
        unit_meta['type'] = 'table'
        units.append({
            "text": text,
            "meta": unit_meta
        })
    return units