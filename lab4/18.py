import sys


def solve():
    input_data = sys.stdin.read().split()
    if not input_data:
        return

    x1, y1 = float(input_data[0]), float(input_data[1])
    x2, y2 = float(input_data[2]), float(input_data[3])

    y1_abs = abs(y1)
    y2_abs = abs(y2)

    res_x = x1 + (x2 - x1) * y1_abs / (y1_abs + y2_abs)

    print(f"{res_x:.10f} {0.0:.10f}")


if __name__ == "__main__":
    solve()