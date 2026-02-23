import sys
import math


def solve():
    input_data = sys.stdin.read().split()
    if not input_data:
        return

    r = float(input_data[0])
    ax, ay = float(input_data[1]), float(input_data[2])
    bx, by = float(input_data[3]), float(input_data[4])

    dist_a = math.sqrt(ax ** 2 + ay ** 2)
    dist_b = math.sqrt(bx ** 2 + by ** 2)
    dist_ab = math.sqrt((bx - ax) ** 2 + (by - ay) ** 2)

    if dist_ab < 1e-12:
        print(f"{0.0:.10f}")
        return

    h = abs(ax * by - ay * bx) / dist_ab

    dot1 = (bx - ax) * (-ax) + (by - ay) * (-ay)
    dot2 = (ax - bx) * (-bx) + (ay - by) * (-by)

    intersects = (h < r - 1e-11) and (dot1 > 0) and (dot2 > 0)

    if not intersects:
        print(f"{dist_ab:.10f}")
    else:
        cos_gamma = (ax * bx + ay * by) / (dist_a * dist_b)
        cos_gamma = max(-1.0, min(1.0, cos_gamma))
        gamma = math.acos(cos_gamma)

        alpha = math.acos(r / dist_a)
        beta = math.acos(r / dist_b)

        arc_angle = max(0.0, gamma - alpha - beta)

        len_a = math.sqrt(max(0.0, dist_a ** 2 - r ** 2))
        len_b = math.sqrt(max(0.0, dist_b ** 2 - r ** 2))
        len_arc = arc_angle * r

        print(f"{len_a + len_b + len_arc:.10f}")


if __name__ == "__main__":
    solve()