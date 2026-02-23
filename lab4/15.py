import sys
from datetime import datetime, timedelta


def parse_data(s):
    parts = s.split()
    date_part = parts[0]
    offset_part = parts[1].replace('UTC', '')

    y, m, d = map(int, date_part.split('-'))

    sign = 1 if offset_part[0] == '+' else -1
    off_h, off_m = map(int, offset_part[1:].split(':'))
    offset = timedelta(hours=off_h, minutes=off_m) * sign

    return y, m, d, offset


def is_leap(y):
    return (y % 4 == 0 and y % 100 != 0) or (y % 400 == 0)


def solve():
    line1 = sys.stdin.readline().strip()
    line2 = sys.stdin.readline().strip()
    if not line1 or not line2:
        return

    by, bm, bd, b_offset = parse_data(line1)
    cy, cm, cd, c_offset = parse_data(line2)

    current_local_dt = datetime(cy, cm, cd)
    current_utc = current_local_dt - c_offset

    for year in range(cy, cy + 3):
        ty, tm, td = year, bm, bd
        if tm == 2 and td == 29 and not is_leap(ty):
            td = 28

        target_local_dt = datetime(ty, tm, td)
        target_utc = target_local_dt - b_offset

        diff = int((target_utc - current_utc).total_seconds())

        if diff >= 0:
            print((diff + 86399) // 86400)
            return


if __name__ == "__main__":
    solve()