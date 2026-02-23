import sys


def solve():
    input_data = sys.stdin.read().split()
    if not input_data:
        return

    n_commands = int(input_data[0])
    g = 0
    n = 0

    idx = 1
    for _ in range(n_commands):
        scope = input_data[idx]
        value = int(input_data[idx + 1])

        if scope == "global":
            g += value
        elif scope == "nonlocal":
            n += value

        idx += 2

    print(g, n)


if __name__ == "__main__":
    solve()