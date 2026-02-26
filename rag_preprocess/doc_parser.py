# rag_preprocess/doc_parser.py

from docx import Document
from typing import List, Dict

from rag_preprocess.chunking.text_splitter import SmartTextSplitter
from rag_runtime.config import CHUNK_SIZE, CHUNK_OVERLAP

splitter = SmartTextSplitter(CHUNK_SIZE, CHUNK_OVERLAP)

def docx_to_blocks(path: str) -> List[Dict]:
    try:
        doc = Document(path)
    except Exception as e:
        print(f"Error reading docx file {path}: {e}")
        return []

    full_text = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
    if not full_text:
        return []

    metadata = {
        "source": path,
        "type": "docx"
    }
    # 使用分块器分割全文
    chunks = splitter.split_text(full_text, metadata)
    return chunks