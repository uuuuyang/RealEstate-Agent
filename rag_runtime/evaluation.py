# rag_runtime/evaluation.py

import json
import numpy as np
from typing import List, Dict, Any
from rag_runtime.rag_retriever import RAGRetriever
from rag_runtime.rag_chain import answer
from rag_runtime.config import EVAL_QUERIES_PATH

def hit_rate_at_k(retrieved_ids: List[str], relevant_ids: List[str], k: int) -> float:
    """计算前k个结果中是否有相关文档"""
    if not relevant_ids:
        return 0.0
    retrieved_set = set(retrieved_ids[:k])
    relevant_set = set(relevant_ids)
    return 1.0 if retrieved_set & relevant_set else 0.0

def mrr(retrieved_ids: List[str], relevant_ids: List[str]) -> float:
    """平均倒数排名"""
    for i, doc_id in enumerate(retrieved_ids):
        if doc_id in relevant_ids:
            return 1.0 / (i + 1)
    return 0.0

def precision_at_k(retrieved_ids: List[str], relevant_ids: List[str], k: int) -> float:
    """前k个结果中相关文档的比例"""
    if k <= 0:
        return 0.0
    retrieved_set = set(retrieved_ids[:k])
    relevant_set = set(relevant_ids)
    return len(retrieved_set & relevant_set) / k

def load_eval_queries(path: str = EVAL_QUERIES_PATH) -> List[Dict]:
    """加载评估测试集，每条包含query、relevant_doc_ids（可选）、expected_answer_summary（可选）"""
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def evaluate_retrieval(retriever: RAGRetriever, queries: List[Dict], k_list: List[int] = [5, 10]) -> Dict:
    """评估检索质量"""
    results = {f"hit_rate@{k}": [] for k in k_list}
    results["mrr"] = []
    for q in queries:
        query = q["query"]
        relevant_ids = q.get("relevant_doc_ids", [])  # 需要预先标注文档ID
        # 执行检索（不带生成）
        docs = retriever.retrieve(query, k=max(k_list), rerank_top_n=max(k_list))
        retrieved_ids = [doc["meta"].get("id", str(i)) for i, doc in enumerate(docs)]  # 假设有id字段，否则用索引代替

        for k in k_list:
            results[f"hit_rate@{k}"].append(hit_rate_at_k(retrieved_ids, relevant_ids, k))
        results["mrr"].append(mrr(retrieved_ids, relevant_ids))

    # 计算平均值
    avg_results = {k: np.mean(v) for k, v in results.items()}
    return avg_results

def evaluate_generation(queries: List[Dict]) -> Dict:
    """评估生成正确率，需要人工或LLM评判，这里简单返回占位"""
    # 实际应用中，可以调用LLM-as-judge或人工评分
    correct = []
    for q in queries:
        query = q["query"]
        expected = q.get("expected_answer_summary", "")
        generated = answer(query, [])  # 注意：这里需要检索，但为了简化，我们假设已有检索结果
        # 需要实现一个判断逻辑，如LLM评分
        correct.append(1)  # 占位
    return {"accuracy": np.mean(correct)}

if __name__ == "__main__":
    retriever = RAGRetriever()
    queries = load_eval_queries()
    ret_metrics = evaluate_retrieval(retriever, queries)
    print("Retrieval Metrics:", ret_metrics)
    # gen_metrics = evaluate_generation(queries)
    # print("Generation Metrics:", gen_metrics)