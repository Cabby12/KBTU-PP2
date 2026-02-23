import sys
from datetime import datetime, timedelta


def parse_utc_seconds(line):
    parts = line.split()
    date_str = f"{parts[0]} {parts[1]}"
    offset_str = parts[2].replace('UTC', '')

    dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")

    sign = 1 if offset_str[0] == '+' else -1
    h, m = map(int, offset_str[1:].split(':'))
    offset = timedelta(hours=h, minutes=m) * sign

    utc_dt = dt - offset
    return int(utc_dt.timestamp())


def solve():
    line1 = sys.stdin.readline().strip()
    line2 = sys.stdin.readline().strip()

    if not line1 or not line2:
        return

    start_seconds = parse_utc_seconds(line1)
    end_seconds = parse_utc_seconds(line2)

    print(end_seconds - start_seconds)


if __name__ == "__main__":
    solve()