import re

s = input()
p = input()
escaped_p = re.escape(p)
matches = re.findall(escaped_p, s)
print(len(matches))
