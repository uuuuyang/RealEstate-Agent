import json
from embed_store import is_valid_unit

with open("C://Users//Lenovo//PycharmProjects//chatbot//jllchatbot//rag_preprocess//units.json", "r", encoding="utf-8") as f:
    units = json.load(f)

valid = [u for u in units if is_valid_unit(u)]

print(f"原始 unit 数量: {len(units)}")
print(f"通过过滤的 unit 数量: {len(valid)}")

# 打印前 10 条有效 unit
for i, u in enumerate(valid[:10]):
    print(f"\n--- Valid Unit {i} ---")
    print(u["text"][:300])
