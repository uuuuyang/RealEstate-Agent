import json

with open("units.json", "r", encoding="utf-8") as f:
    units = json.load(f)

print(f"units.json 总条数: {len(units)}")

# 打印前 10 条
for i, u in enumerate(units[:10]):
    print(f"\n--- Unit {i} ---")
    print("type:", u.get("type"))
    print("text:", u.get("text")[:200])
    print("meta:", u.get("meta"))
