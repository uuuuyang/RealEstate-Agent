# rag_runtime/tools_schema.py

TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "calc_mean",
            "description": "计算一组数值的平均值",
            "parameters": {
                "type": "object",
                "properties": {
                    "values": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "数值列表"
                    }
                },
                "required": ["values"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calc_yoy",
            "description": "计算同比变化率，输入按时间顺序排列",
            "parameters": {
                "type": "object",
                "properties": {
                    "values": {
                        "type": "array",
                        "items": {"type": "number"},
                        "minItems": 2
                    }
                },
                "required": ["values"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "compare_mean",
            "description": "对比两组数值的平均值",
            "parameters": {
                "type": "object",
                "properties": {
                    "group_a": {
                        "type": "array",
                        "items": {"type": "number"}
                    },
                    "group_b": {
                        "type": "array",
                        "items": {"type": "number"}
                    }
                },
                "required": ["group_a", "group_b"]
            }
        }
    }
]
