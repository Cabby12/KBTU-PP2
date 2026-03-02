import re

s = input()
pattern = r'Name: (.*?), Age: (.*)'
match = re.search(pattern, s)
if match:
    print(f"{match.group(1)} {match.group(2)}")
