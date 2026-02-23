import sys
import importlib


def solve():
    input_data = sys.stdin.read().splitlines()
    if not input_data:
        return

    try:
        n = int(input_data[0].strip())
    except (ValueError, IndexError):
        return

    for i in range(1, n + 1):
        line = input_data[i].strip().split()
        if len(line) < 2:
            continue

        module_path, attr_name = line[0], line[1]

        try:
            mod = importlib.import_module(module_path)
        except ImportError:
            print("MODULE_NOT_FOUND")
            continue

        if not hasattr(mod, attr_name):
            print("ATTRIBUTE_NOT_FOUND")
            continue

        attr = getattr(mod, attr_name)
        if callable(attr):
            print("CALLABLE")
        else:
            print("VALUE")


if __name__ == "__main__":
    solve()