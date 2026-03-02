import re

s = input()
matches = re.findall(r'\b[a-zA-Z]{3}\b', s)
print(len(matches))
