import json
import re


def resolve_query(data, query):
    current = data

    parts = re.findall(r'([^.\[\]]+)|\[(\d+)\]', query)

    for part, index in parts:
        if index:
            idx = int(index)
            if isinstance(current, list) and 0 <= idx < len(current):
                current = current[idx]
            else:
                return None
        else:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None

    return current


data = json.loads(input())
n = int(input())

for _ in range(n):
    query = input().strip()
    result = resolve_query(data, query)

    if result is None and query not in data:
        print("NOT_FOUND")
    else:
        print(json.dumps(result, separators=(',', ':')))