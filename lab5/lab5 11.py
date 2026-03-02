import re

s = input()
matches = re.findall(r'[A-Z]', s)
print(len(matches))
