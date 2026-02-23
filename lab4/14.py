from datetime import datetime, timedelta
import sys

def parse_line(line):
    date_part, tz_part = line.strip().split()
    dt = datetime.strptime(date_part, "%Y-%m-%d")
    sign = 1 if tz_part[3] == '+' else -1
    hours, minutes = map(int, tz_part[4:].split(':'))
    offset = timedelta(hours=hours, minutes=minutes)
    if sign == 1:
        dt -= offset
    else:
        dt += offset
    return dt

dt1 = parse_line(sys.stdin.readline())
dt2 = parse_line(sys.stdin.readline())

diff_seconds = abs((dt1 - dt2).total_seconds())
print(int(diff_seconds // 86400))