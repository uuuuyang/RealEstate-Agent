# rag_preprocess/incremental_updater.py

import json
import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from doc_parser import docx_to_blocks
from table_parser import table_to_units
from chunking.table_processor import process_table_file
from rag_runtime.config import EMBED_MODEL, CHROMA_PERSIST_DIR, COLLECTION_NAME

def update_from_new_files(new_files: list):
    """增量处理新文件，添加到向量库"""
    embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL)
    vectordb = Chroma(
        collection_name=COLLECTION_NAME,
        persist_directory=CHROMA_PERSIST_DIR,
        embedding_function=embeddings
    )

    all_units = []
    for filepath in new_files:
        ext = os.path.splitext(filepath)[1].lower()
        if ext == ".docx":
            units = docx_to_blocks(filepath)
            all_units.extend(units)
        elif ext == ".xlsx":
            # 先尝试用交易表解析（假设结构固定）
            try:
                units = table_to_units(filepath)
                all_units.extend(units)
            except:
                # 否则作为普通表格处理
                meta = {"source": filepath, "source_type": "table_doc"}
                units = process_table_file(filepath, meta)
                all_units.extend(units)

    # 过滤无效单元（与embed_store中一致）
    def is_valid_unit(u):
        text = u["text"].strip()
        if len(text) < 15:
            return False
        return True

    texts = []
    metadatas = []
    for u in all_units:
        if is_valid_unit(u):
            texts.append(u["text"])
            metadatas.append(u.get("meta", {}))

    if texts:
        vectordb.add_texts(texts=texts, metadatas=metadatas)
        print(f"Added {len(texts)} new units to vector store.")

if __name__ == "__main__":
    # 示例：处理data/new/下的所有文件
    new_files = [os.path.join("data/new", f) for f in os.listdir("data/new") if f.endswith(('.docx', '.xlsx'))]
    update_from_new_files(new_files)