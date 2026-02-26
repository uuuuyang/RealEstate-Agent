# rag_runtime/rag_retriever.py

import json
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from sentence_transformers import CrossEncoder
from config import EMBED_MODEL, RERANK_MODEL, CHROMA_PERSIST_DIR, RETRIEVER_K, RERANK_TOP_N
from cache_manager import cache

COLLECTION_NAME = "jll_units"

class RAGRetriever:
    def __init__(self, persist_dir: str = CHROMA_PERSIST_DIR):
        print("🚀 [System] Initializing Retriever (Embedding + Reranker)...")
        self.embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL)
        self.vectordb = Chroma(
            collection_name=COLLECTION_NAME,
            persist_directory=persist_dir,
            embedding_function=self.embeddings
        )
        self.reranker = CrossEncoder(RERANK_MODEL)

    @cache(ttl=3600)  # 缓存检索结果1小时
    def retrieve(self, query: str, filter_dict: dict = None, k=RETRIEVER_K, rerank_top_n=RERANK_TOP_N):
        print(f"\n🔍 [Retrieval] Start searching for: '{query}'")
        print(f"   Filter: {filter_dict}")

        # 将filter_dict转换为Chroma支持的格式
        chroma_filter = self._convert_filter(filter_dict) if filter_dict else None

        # 1. 向量检索（带过滤）
        docs = self.vectordb.similarity_search(query, k=k, filter=chroma_filter)
        print(f"   ↳ Initial Recall: {len(docs)} documents")

        if not docs:
            return []

        # 2. Rerank 重排序
        pairs = [(query, d.page_content) for d in docs]
        scores = self.reranker.predict(pairs)

        doc_scores = list(zip(docs, scores))
        doc_scores.sort(key=lambda x: x[1], reverse=True)

        final_results = doc_scores[:rerank_top_n]

        print(f"📉 [Rerank] Filtered to Top-{rerank_top_n}")

        structured_results = []
        for i, (doc, score) in enumerate(final_results):
            meta = doc.metadata
            print(
                f"   [{i + 1}] Score: {score:.4f} | Year: {meta.get('year')} | District: {meta.get('district')} | Rent: {meta.get('rent')}")
            structured_results.append({
                "text": doc.page_content,
                "meta": doc.metadata
            })

        return structured_results

    def _convert_filter(self, filter_dict: dict) -> dict:
        """将解析出的过滤器转换为Chroma支持的$and/$or格式"""
        conditions = []
        for key, value in filter_dict.items():
            if key == "year_range":
                # 范围过滤：year >= start and year <= end
                conditions.append({"year": {"$gte": value[0]}})
                conditions.append({"year": {"$lte": value[1]}})
            elif key in ["min_rent", "max_rent", "min_area", "max_area"]:
                # 处理数值范围，假设对应字段名为rent/area
                field = key.split("_")[1]
                op = "$gte" if key.startswith("min") else "$lte"
                conditions.append({field: {op: value}})
            else:
                # 精确匹配
                conditions.append({key: {"$eq": value}})
        if len(conditions) == 1:
            return conditions[0]
        elif len(conditions) > 1:
            return {"$and": conditions}
        else:
            return None