# rag_runtime/run_query.py

from rag_retriever import RAGRetriever
from rag_chain import answer
import sys

retriever = RAGRetriever(persist_dir="./chroma_jll")

if len(sys.argv) > 1:
    query = " ".join(sys.argv[1:])
else:
    query = "2023-2024年静安区写字楼租金同比变化？"

result = answer(query, retriever)
print(result)