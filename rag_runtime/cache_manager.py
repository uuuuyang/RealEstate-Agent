# rag_runtime/cache_manager.py

import hashlib
import json
import time
from functools import wraps
from typing import Any, Callable

# 简单的内存缓存，生产环境可替换为Redis
_cache = {}
_embedding_cache = {}

def cache(ttl: int = 3600):
    """函数结果缓存装饰器，key为函数名+参数JSON"""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 生成缓存key
            key_parts = [func.__name__]
            key_parts.extend([str(arg) for arg in args])
            key_parts.extend([f"{k}:{v}" for k, v in sorted(kwargs.items())])
            key_str = json.dumps(key_parts, ensure_ascii=False)
            key = hashlib.md5(key_str.encode()).hexdigest()

            now = time.time()
            if key in _cache:
                value, expire_time = _cache[key]
                if now < expire_time:
                    return value
            result = func(*args, **kwargs)
            _cache[key] = (result, now + ttl)
            return result
        return wrapper
    return decorator

def cache_embedding(text: str, embedding_func: Callable) -> list:
    """专门缓存嵌入向量，避免重复计算"""
    key = hashlib.md5(text.encode()).hexdigest()
    if key in _embedding_cache:
        return _embedding_cache[key]
    emb = embedding_func(text)
    _embedding_cache[key] = emb
    return emb