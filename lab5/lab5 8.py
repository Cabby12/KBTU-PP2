import re

s = input()
pattern = input()
parts = re.split(pattern, s)
print(",".join(parts))
