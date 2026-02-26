# rag_preprocess/run.py

import json
import os
from doc_parser import docx_to_blocks
from unit_builder import blocks_to_units
from table_parser import table_to_units
from chunking.table_processor import process_table_file

def main():
    all_units = []

    # 处理文档
    if os.path.exists("data/report.docx"):
        print("Processing report.docx...")
        doc_blocks = docx_to_blocks("data/report.docx")
        # 注意：doc_blocks已经是分块后的单元，不需要再调用blocks_to_units？
        # 为保持统一，可以仍调用blocks_to_units，但blocks_to_units需要修改以接受已有块
        # 这里简单将doc_blocks直接作为单元
        all_units.extend(doc_blocks)
    else:
        print("Skipping report.docx (not found)")

    # 处理交易表格（保留原table_parser，它生成的是可计算单元）
    if os.path.exists("data/transaction.xlsx"):
        print("Processing transaction.xlsx...")
        try:
            table_units = table_to_units("data/transaction.xlsx")
            all_units.extend(table_units)
            print(f"Generated {len(table_units)} computable units from table.")
        except Exception as e:
            print(f"Error processing table: {e}")
    else:
        print("Skipping transaction.xlsx (not found)")

    # 处理其他Excel文件（作为文档表格处理）
    if os.path.exists("data/other_table.xlsx"):
        print("Processing other_table.xlsx...")
        meta = {"source": "other_table.xlsx", "source_type": "table_doc"}
        table_text_units = process_table_file("data/other_table.xlsx", meta)
        all_units.extend(table_text_units)
        print(f"Generated {len(table_text_units)} text units from table.")

    # 输出为统一格式
    output_file = "units.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_units, f, ensure_ascii=False, indent=2)

    print(f"Done. Total units: {len(all_units)}. Saved to {output_file}")

if __name__ == "__main__":
    main()