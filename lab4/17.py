import sys
import math


def solve():
    input_data = sys.stdin.read().split()
    if not input_data:
        return

    r = float(input_data[0])
    ax, ay = float(input_data[1]), float(input_data[2])
    bx, by = float(input_data[3]), float(input_data[4])

    dx = bx - ax
    dy = by - ay

    a_coef = dx ** 2 + dy ** 2
    b_coef = 2 * (ax * dx + ay * dy)
    c_coef = ax ** 2 + ay ** 2 - r ** 2

    if a_coef == 0:
        if ax ** 2 + ay ** 2 <= r ** 2 + 1e-9:
            print(f"{0.0:.10f}")
        else:
            print(f"{0.0:.10f}")
        return

    dist_ab = math.sqrt(a_coef)
    discriminant = b_coef ** 2 - 4 * a_coef * c_coef

    if discriminant < 0:
        print(f"{0.0:.10f}")
        return

    sqrt_d = math.sqrt(discriminant)
    t1 = (-b_coef - sqrt_d) / (2 * a_coef)
    t2 = (-b_coef + sqrt_d) / (2 * a_coef)

    t_start = max(0.0, t1)
    t_end = min(1.0, t2)

    if t_start < t_end:
        print(f"{(t_end - t_start) * dist_ab:.10f}")
    else:
        print(f"{0.0:.10f}")


if __name__ == "__main__":
    solve()