# rag_preprocess/chunking/text_splitter.py
from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import List, Dict
import tiktoken

def num_tokens_from_string(text: str, encoding_name: str = "cl100k_base") -> int:
    """估算字符串的token数，使用tiktoken"""
    encoding = tiktoken.get_encoding(encoding_name)
    return len(encoding.encode(text))

class SmartTextSplitter:
    def __init__(self, chunk_size: int, chunk_overlap: int):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=num_tokens_from_string,
            separators=["\n\n", "\n", "。", "；", "，", " ", ""]
        )

    def split_text(self, text: str, metadata: Dict) -> List[Dict]:
        """将文本分割成多个块，每个块继承原始metadata"""
        chunks = self.splitter.create_documents([text], [metadata])
        result = []
        for i, doc in enumerate(chunks):
            chunk_meta = doc.metadata.copy()
            chunk_meta['chunk_index'] = i
            chunk_meta['chunk_total'] = len(chunks)
            result.append({
                "text": doc.page_content,
                "meta": chunk_meta
            })
        return result