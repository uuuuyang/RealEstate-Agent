# rag_runtime/config.py
# rag_runtime/config.py

import os

# 分块参数
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

# 检索参数
RETRIEVER_K = 20
RERANK_TOP_N = 5

# 缓存设置
CACHE_EXPIRE = 3600 * 24   # 24小时
ENABLE_CACHE = True

# 评估测试集路径
EVAL_QUERIES_PATH = "data/eval_queries.json"

# 意图解析模型
INTENT_MODEL = "deepseek-chat"

# 嵌入模型
EMBED_MODEL = "BAAI/bge-small-zh-v1.5"
RERANK_MODEL = "BAAI/bge-reranker-base"

# 向量库持久化目录
CHROMA_PERSIST_DIR = "./chroma_jll"

# 向量库集合名称
COLLECTION_NAME = "jll_units"

# DeepSeek API key 从环境变量读取
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "your-key")
