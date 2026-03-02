import re

s = input()
p = input()
matches = re.findall(p, s)
print(len(matches))
