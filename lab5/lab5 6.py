import re

s = input()
pattern = r'\S+@\S+\.\S+'
match = re.search(pattern, s)

if match:
    print(match.group())
else:
    print("No email")
