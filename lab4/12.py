import json


def find_differences(obj1, obj2, path=""):
    differences = []

    keys1 = set(obj1.keys()) if isinstance(obj1, dict) else set()
    keys2 = set(obj2.keys()) if isinstance(obj2, dict) else set()

    all_keys = keys1.union(keys2)

    for key in sorted(all_keys):
        current_path = f"{path}.{key}" if path else key

        if key not in obj1:
            val2 = json.dumps(obj2[key], separators=(',', ':'))
            differences.append(f"{current_path} : <missing> -> {val2}")
        elif key not in obj2:
            val1 = json.dumps(obj1[key], separators=(',', ':'))
            differences.append(f"{current_path} : {val1} -> <missing>")
        else:
            val1 = obj1[key]
            val2 = obj2[key]

            if isinstance(val1, dict) and isinstance(val2, dict):
                differences.extend(find_differences(val1, val2, current_path))
            elif val1 != val2:
                val1_str = json.dumps(val1, separators=(',', ':'))
                val2_str = json.dumps(val2, separators=(',', ':'))
                differences.append(f"{current_path} : {val1_str} -> {val2_str}")

    return differences


obj1 = json.loads(input())
obj2 = json.loads(input())

diffs = find_differences(obj1, obj2)

if diffs:
    for diff in sorted(diffs):
        print(diff)
else:
    print("No differences")