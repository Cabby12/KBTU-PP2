import json


def apply_patch(source, patch):
    result = source.copy() if isinstance(source, dict) else source

    for key, value in patch.items():
        if value is None:
            if key in result:
                del result[key]
        elif isinstance(value, dict) and key in result and isinstance(result[key], dict):
            result[key] = apply_patch(result[key], value)
        else:
            result[key] = value

    return result


source = json.loads(input())
patch = json.loads(input())

patched = apply_patch(source, patch)

print(json.dumps(patched, separators=(',', ':'), sort_keys=True))