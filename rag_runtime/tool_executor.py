# rag_runtime/tool_executor.py
from tool_registry import TOOL_REGISTRY

def execute_tool(tool_call):
    name = tool_call["name"]
    args = tool_call["arguments"]

    if name not in TOOL_REGISTRY:
        raise ValueError(f"Unknown tool: {name}")

    return TOOL_REGISTRY[name](**args)
